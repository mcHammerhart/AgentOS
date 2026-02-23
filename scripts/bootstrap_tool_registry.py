#!/usr/bin/env python3
"""
bootstrap_tool_registry.py — Seed tool_registry.db from extensions/ directory.

Usage:
  python3 scripts/bootstrap_tool_registry.py            # dry-run (preview)
  python3 scripts/bootstrap_tool_registry.py --apply    # write to DB
  python3 scripts/bootstrap_tool_registry.py --activate telegram,memory-core  # activate specific tools
  python3 scripts/bootstrap_tool_registry.py --status   # show current registry state

Rules:
  - New extensions are inserted as 'inactive' (never auto-activated)
  - Existing entries are NOT overwritten (idempotent)
  - Manual activation required: set allow_status='active' per tool
  - Every status change is audit-logged
"""

import argparse
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

# ─── Paths ───────────────────────────────────────────────────────────────────
REPO_ROOT   = Path(__file__).parent.parent.resolve()
EXT_DIR     = REPO_ROOT / "extensions"
DB_PATH     = Path.home() / "agent-os" / "state" / "tool_registry.db"

# ─── Active-by-default for THIS install (curated list) ───────────────────────
# Only tools actually in use on this machine. Edit to taste.
ACTIVE_BY_DEFAULT = {
    "telegram",
    "memory-core",
    "lobster",
    "shared",
    "diagnostics-otel",
}

# Known upstream repo URLs per extension
KNOWN_REPOS: dict[str, str] = {
    "telegram":        "https://github.com/openclaw-dev/openclaw/tree/main/extensions/telegram",
    "memory-core":     "https://github.com/openclaw-dev/openclaw/tree/main/extensions/memory-core",
    "discord":         "https://github.com/openclaw-dev/openclaw/tree/main/extensions/discord",
    "slack":           "https://github.com/openclaw-dev/openclaw/tree/main/extensions/slack",
    "whatsapp":        "https://github.com/openclaw-dev/openclaw/tree/main/extensions/whatsapp",
    "signal":          "https://github.com/openclaw-dev/openclaw/tree/main/extensions/signal",
    "lobster":         "https://github.com/openclaw-dev/openclaw/tree/main/extensions/lobster",
    "shared":          "https://github.com/openclaw-dev/openclaw/tree/main/extensions/shared",
    "imessage":        "https://github.com/openclaw-dev/openclaw/tree/main/extensions/imessage",
    "googlechat":      "https://github.com/openclaw-dev/openclaw/tree/main/extensions/googlechat",
}


def get_extension_version(ext_path: Path) -> str | None:
    """Read version from package.json if present."""
    pkg = ext_path / "package.json"
    if pkg.exists():
        try:
            import json
            data = json.loads(pkg.read_text())
            return data.get("version")
        except Exception:
            pass
    return None


def discover_extensions() -> list[dict]:
    """Scan extensions/ directory and return list of extension info dicts."""
    if not EXT_DIR.exists():
        print(f"ERROR: extensions/ not found at {EXT_DIR}", file=sys.stderr)
        sys.exit(1)
    result = []
    for entry in sorted(EXT_DIR.iterdir()):
        if not entry.is_dir():
            continue
        ext_id = entry.name
        result.append({
            "id":            ext_id,
            "name":          ext_id,
            "local_path":    f"extensions/{ext_id}",
            "upstream_repo": KNOWN_REPOS.get(ext_id),
            "version":       get_extension_version(entry),
            "allow_status":  "active" if ext_id in ACTIVE_BY_DEFAULT else "inactive",
        })
    return result


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS tools (
          id           TEXT PRIMARY KEY,
          name         TEXT NOT NULL,
          description  TEXT,
          local_path   TEXT NOT NULL,
          upstream_repo TEXT,
          version      TEXT,
          allow_status TEXT CHECK(allow_status IN ('active','inactive')) NOT NULL DEFAULT 'inactive',
          created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS tool_audit_log (
          id           INTEGER PRIMARY KEY AUTOINCREMENT,
          tool_id      TEXT,
          action       TEXT,
          old_status   TEXT,
          new_status   TEXT,
          triggered_by TEXT,
          timestamp    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_tools_allow ON tools(allow_status);
        CREATE INDEX IF NOT EXISTS idx_audit_tool  ON tool_audit_log(tool_id);
    """)


def cmd_bootstrap(conn: sqlite3.Connection, extensions: list[dict], apply: bool) -> None:
    now = datetime.now(timezone.utc).isoformat()
    inserted = []
    skipped  = []

    for ext in extensions:
        existing = conn.execute(
            "SELECT id, allow_status FROM tools WHERE id = ?", (ext["id"],)
        ).fetchone()

        if existing:
            skipped.append(f"  EXISTS  {ext['id']:30} allow_status={existing[1]}")
            continue

        status = "inactive"  # RULE 5: new tools always inactive
        tag = "  NEW     "
        inserted.append(f"{tag}{ext['id']:30} → {status}")

        if apply:
            conn.execute(
                """INSERT INTO tools (id, name, local_path, upstream_repo, version, allow_status)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (ext["id"], ext["name"], ext["local_path"],
                 ext["upstream_repo"], ext["version"], status),
            )
            conn.execute(
                """INSERT INTO tool_audit_log (tool_id, action, old_status, new_status, triggered_by)
                   VALUES (?, 'register', NULL, ?, 'bootstrap_tool_registry.py')""",
                (ext["id"], status),
            )

    if not apply:
        print("DRY RUN — no changes written. Pass --apply to execute.\n")

    if inserted:
        print(f"New extensions ({len(inserted)}):")
        for line in inserted:
            print(line)
    if skipped:
        print(f"\nAlready in registry ({len(skipped)}):")
        for line in skipped:
            print(line)

    if apply and inserted:
        conn.commit()
        print(f"\n✅ Inserted {len(inserted)} new extension(s) as 'inactive'.")
        print("   Use --activate <id,id,...> to enable specific tools.")


def cmd_activate(conn: sqlite3.Connection, ids: list[str]) -> None:
    now = datetime.now(timezone.utc).isoformat()
    for ext_id in ids:
        row = conn.execute(
            "SELECT allow_status FROM tools WHERE id = ?", (ext_id,)
        ).fetchone()
        if not row:
            print(f"  ERROR: '{ext_id}' not in registry. Run --apply first.")
            continue
        old = row[0]
        conn.execute(
            "UPDATE tools SET allow_status='active', updated_at=? WHERE id=?",
            (now, ext_id)
        )
        conn.execute(
            """INSERT INTO tool_audit_log (tool_id, action, old_status, new_status, triggered_by)
               VALUES (?, 'activate', ?, 'active', 'bootstrap_tool_registry.py')""",
            (ext_id, old)
        )
        print(f"  ✅ {ext_id}: {old} → active")
    conn.commit()


def cmd_status(conn: sqlite3.Connection) -> None:
    rows = conn.execute(
        "SELECT id, allow_status, version, updated_at FROM tools ORDER BY allow_status DESC, id"
    ).fetchall()
    if not rows:
        print("Registry is empty. Run: python3 scripts/bootstrap_tool_registry.py --apply")
        return
    active   = [r for r in rows if r[1] == "active"]
    inactive = [r for r in rows if r[1] == "inactive"]
    print(f"\n{'Tool Registry':50} Status     Version    Updated")
    print("─" * 90)
    for r in active:
        print(f"  ✅ {r[0]:46} active     {r[2] or '?':10} {r[3][:10] if r[3] else '?'}")
    for r in inactive:
        print(f"  ⏸  {r[0]:46} inactive   {r[2] or '?':10} {r[3][:10] if r[3] else '?'}")
    print(f"\nTotal: {len(rows)} | Active: {len(active)} | Inactive: {len(inactive)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bootstrap and manage tool_registry.db"
    )
    parser.add_argument("--apply",    action="store_true",
                        help="Write new extensions to DB (inactive by default)")
    parser.add_argument("--activate", type=str, metavar="ID,ID,...",
                        help="Activate specific extension IDs (comma-separated)")
    parser.add_argument("--status",   action="store_true",
                        help="Show current registry state")
    parser.add_argument("--db",       type=str, default=str(DB_PATH),
                        help=f"Path to DB (default: {DB_PATH})")
    args = parser.parse_args()

    db_path = Path(args.db)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    ensure_schema(conn)

    if args.status:
        cmd_status(conn)
        return

    if args.activate:
        ids = [i.strip() for i in args.activate.split(",") if i.strip()]
        print(f"Activating {len(ids)} tool(s): {ids}")
        cmd_activate(conn, ids)
        return

    # Default: bootstrap (dry-run unless --apply)
    extensions = discover_extensions()
    print(f"Discovered {len(extensions)} extensions in {EXT_DIR}\n")
    cmd_bootstrap(conn, extensions, apply=args.apply)

    conn.close()


if __name__ == "__main__":
    main()
