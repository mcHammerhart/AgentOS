/**
 * tool-registry.ts — Tool Governance Allowlist
 *
 * Hard enforcement layer for extension loading and tool execution.
 * Uses ~/agent-os/state/tool_registry.db (SQLite) as single source of truth.
 *
 * Rules enforced here:
 *   RULE 1 – Only tools with allow_status='active' may load
 *   RULE 2 – Tools without a registry entry are BLOCKED by default
 *   RULE 5 – New tools from upstream updates default to 'inactive'
 *
 * Fail-closed: if the DB is unreadable, NO tools are allowed.
 * TTL cache: avoids DB hit on every tool call (default: 60s).
 */

import fs from "node:fs";
import { createRequire } from "node:module";
import os from "node:os";
import path from "node:path";
import { createSubsystemLogger } from "../logging/subsystem.js";

const log = createSubsystemLogger("tool-governance");

// ─── DB Path ─────────────────────────────────────────────────────────────────
const DEFAULT_DB_PATH = path.join(os.homedir(), "agent-os", "state", "tool_registry.db");

// ─── Types ───────────────────────────────────────────────────────────────────
type CacheEntry = {
  allowed: boolean;
  expiresAt: number;
};

// Minimal type for node:sqlite DatabaseSync
type SqliteStatement = {
  get: (...args: unknown[]) => Record<string, unknown> | undefined;
};
type SqliteDB = {
  prepare: (sql: string) => SqliteStatement;
  exec: (sql: string) => void;
  close: () => void;
};

// ─── Singleton ───────────────────────────────────────────────────────────────
let _registry: ToolRegistry | null = null;

export function getToolRegistry(): ToolRegistry {
  if (!_registry) {
    _registry = createToolRegistry();
  }
  return _registry;
}

export function resetToolRegistry(): void {
  if (_registry) {
    try {
      _registry.close();
    } catch {
      // ignore
    }
  }
  _registry = null;
}

// ─── Factory ─────────────────────────────────────────────────────────────────
export type ToolRegistryOptions = {
  dbPath?: string;
  cacheTtlMs?: number;
};

export class ToolRegistry {
  private readonly dbPath: string;
  private readonly cacheTtlMs: number;
  private readonly cache = new Map<string, CacheEntry>();
  private db: SqliteDB | null = null;
  private stmt: SqliteStatement | null = null;
  private _available = false;

  constructor(options: ToolRegistryOptions = {}) {
    this.dbPath = options.dbPath ?? DEFAULT_DB_PATH;
    this.cacheTtlMs = options.cacheTtlMs ?? 60_000;
    this._init();
  }

  private _init(): void {
    if (!fs.existsSync(this.dbPath)) {
      log.warn(
        `[tool-governance] DB not found at ${this.dbPath} — fail-closed: no extensions will load`,
      );
      return;
    }
    try {
      const req = createRequire(import.meta.url);
      const sqlite = req("node:sqlite") as {
        DatabaseSync: new (path: string, opts?: { readonly?: boolean }) => SqliteDB;
      };
      this.db = new sqlite.DatabaseSync(this.dbPath, { readonly: true });
      this.stmt = this.db.prepare("SELECT allow_status FROM tools WHERE id = ? LIMIT 1");
      this._available = true;
      log.info(`[tool-governance] registry loaded from ${this.dbPath}`);
    } catch (err) {
      log.error(`[tool-governance] failed to open registry DB — fail-closed: ${String(err)}`);
      this._available = false;
    }
  }

  /**
   * Check if an extension is allowed to load.
   * Fail-closed: returns false if DB is unavailable or extension not in registry.
   */
  isAllowedSync(extensionId: string): boolean {
    const now = Date.now();
    const hit = this.cache.get(extensionId);
    if (hit && hit.expiresAt > now) {
      return hit.allowed;
    }

    let allowed = false;
    if (this._available && this.stmt) {
      try {
        const row = this.stmt.get(extensionId) as { allow_status: string } | undefined;
        allowed = row?.allow_status === "active";
      } catch (err) {
        // DB error → fail-closed
        log.error(
          `[tool-governance] DB read error for "${extensionId}", blocking — ${String(err)}`,
        );
        allowed = false;
      }
    }

    this.cache.set(extensionId, {
      allowed,
      expiresAt: now + this.cacheTtlMs,
    });
    return allowed;
  }

  /** Invalidate cache for a specific extension (e.g. after status change) */
  invalidate(extensionId?: string): void {
    if (extensionId) {
      this.cache.delete(extensionId);
    } else {
      this.cache.clear();
    }
  }

  get available(): boolean {
    return this._available;
  }

  close(): void {
    try {
      this.db?.close();
    } catch {
      // ignore
    }
    this.db = null;
    this.stmt = null;
    this._available = false;
  }
}

export function createToolRegistry(options: ToolRegistryOptions = {}): ToolRegistry {
  return new ToolRegistry(options);
}

// ─── Audit helpers (write-path, used by management scripts) ──────────────────
export type AuditAction = "activate" | "deactivate" | "register" | "delete_requested" | "deleted";

export function writeAuditLog(params: {
  dbPath?: string;
  toolId: string;
  action: AuditAction;
  oldStatus?: string;
  newStatus?: string;
  triggeredBy: string;
}): void {
  const dbPath = params.dbPath ?? DEFAULT_DB_PATH;
  try {
    const req = createRequire(import.meta.url);
    const sqlite = req("node:sqlite") as {
      DatabaseSync: new (path: string) => SqliteDB;
    };
    const db = new sqlite.DatabaseSync(dbPath);
    const stmt = db.prepare(
      `INSERT INTO tool_audit_log (tool_id, action, old_status, new_status, triggered_by)
       VALUES (?, ?, ?, ?, ?)`,
    );
    stmt.get(
      params.toolId,
      params.action,
      params.oldStatus ?? null,
      params.newStatus ?? null,
      params.triggeredBy,
    );
    db.close();
  } catch (err) {
    log.error(`[tool-governance] audit write failed: ${String(err)}`);
  }
}
