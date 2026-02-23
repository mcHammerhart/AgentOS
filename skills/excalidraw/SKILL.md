# Skill: Excalidraw Diagrams

**Trigger:** Any request to create a diagram, architecture overview, flowchart, system map, or visual.

## Step-by-Step

1. Design the diagram elements as Excalidraw JSON (see format below)
2. Save to a `.excalidraw` file in `~/agent-os/diagrams/` (create dir if needed)
3. Run the export script to get a shareable URL:
   ```bash
   node /Users/tilohammer/agent-os/bin/excalidraw_export.js /path/to/diagram.excalidraw
   ```
4. Reply with the URL + brief description

---

## Excalidraw JSON Structure

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [...],
  "appState": { "gridSize": null, "viewBackgroundColor": "#ffffff" },
  "files": {}
}
```

---

## Element Types and Properties

### Rectangle

```json
{
  "id": "unique-id",
  "type": "rectangle",
  "x": 100,
  "y": 100,
  "width": 160,
  "height": 60,
  "angle": 0,
  "strokeColor": "#1e1e1e",
  "backgroundColor": "#a5d8ff",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 1,
  "opacity": 100,
  "roundness": { "type": 3 },
  "seed": 12345,
  "version": 1,
  "versionNonce": 0,
  "isDeleted": false,
  "boundElements": null,
  "updated": 1,
  "link": null,
  "locked": false
}
```

### Text

```json
{
  "id": "text-id",
  "type": "text",
  "x": 120,
  "y": 120,
  "width": 120,
  "height": 25,
  "angle": 0,
  "strokeColor": "#1e1e1e",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 1,
  "opacity": 100,
  "text": "Label",
  "fontSize": 16,
  "fontFamily": 1,
  "textAlign": "center",
  "verticalAlign": "middle",
  "seed": 99,
  "version": 1,
  "versionNonce": 0,
  "isDeleted": false,
  "boundElements": null,
  "updated": 1,
  "link": null,
  "locked": false,
  "containerId": null,
  "originalText": "Label",
  "lineHeight": 1.25
}
```

### Arrow

```json
{
  "id": "arrow-id",
  "type": "arrow",
  "x": 260,
  "y": 130,
  "width": 80,
  "height": 0,
  "angle": 0,
  "strokeColor": "#1e1e1e",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 1,
  "opacity": 100,
  "points": [
    [0, 0],
    [80, 0]
  ],
  "lastCommittedPoint": null,
  "startBinding": { "elementId": "source-rect-id", "focus": 0, "gap": 1 },
  "endBinding": { "elementId": "target-rect-id", "focus": 0, "gap": 1 },
  "startArrowhead": null,
  "endArrowhead": "arrow",
  "seed": 55,
  "version": 1,
  "versionNonce": 0,
  "isDeleted": false,
  "boundElements": null,
  "updated": 1,
  "link": null,
  "locked": false
}
```

### Diamond (Decision)

Same as rectangle but `"type": "diamond"`.

### Ellipse

Same as rectangle but `"type": "ellipse"`.

---

## Color Palette

### Shape backgrounds (pastel)

| Use               | Hex                      |
| ----------------- | ------------------------ |
| Input / source    | `#a5d8ff` (light blue)   |
| Success / output  | `#b2f2bb` (light green)  |
| Warning / pending | `#ffd8a8` (light orange) |
| Processing / AI   | `#d0bfff` (light purple) |
| Error / critical  | `#ffc9c9` (light red)    |
| Notes / decisions | `#fff3bf` (light yellow) |
| Storage / data    | `#c3fae8` (light teal)   |

### Stroke / text colors

- Default stroke: `#1e1e1e`
- Primary accent: `#4a9eed`
- Warning: `#f59e0b`
- Success: `#22c55e`
- Error: `#ef4444`

---

## Layout Guidelines

- **Grid**: use multiples of 20px for x/y positions
- **Node size**: rectangles typically 160×60 for boxes, 200×80 for large nodes
- **Spacing**: 60px gap between connected nodes horizontally, 40px vertically
- **Arrow**: connect from right edge of source to left edge of target
- **IDs**: use short descriptive strings (`node-1`, `arrow-user-api`)
- **roughness: 1** = hand-drawn look (signature Excalidraw style)

---

## Example: Simple Architecture

User → API → Database

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [
    {
      "id": "r1",
      "type": "rectangle",
      "x": 50,
      "y": 100,
      "width": 140,
      "height": 60,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#a5d8ff",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "roundness": { "type": 3 },
      "seed": 1,
      "version": 1,
      "versionNonce": 0,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1,
      "link": null,
      "locked": false
    },
    {
      "id": "t1",
      "type": "text",
      "x": 90,
      "y": 120,
      "width": 60,
      "height": 20,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "text": "User",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "seed": 2,
      "version": 1,
      "versionNonce": 0,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1,
      "link": null,
      "locked": false,
      "containerId": null,
      "originalText": "User",
      "lineHeight": 1.25
    },
    {
      "id": "a1",
      "type": "arrow",
      "x": 190,
      "y": 130,
      "width": 60,
      "height": 0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "points": [
        [0, 0],
        [60, 0]
      ],
      "lastCommittedPoint": null,
      "startBinding": null,
      "endBinding": null,
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "seed": 3,
      "version": 1,
      "versionNonce": 0,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1,
      "link": null,
      "locked": false
    },
    {
      "id": "r2",
      "type": "rectangle",
      "x": 250,
      "y": 100,
      "width": 140,
      "height": 60,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#d0bfff",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "roundness": { "type": 3 },
      "seed": 4,
      "version": 1,
      "versionNonce": 0,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1,
      "link": null,
      "locked": false
    },
    {
      "id": "t2",
      "type": "text",
      "x": 290,
      "y": 120,
      "width": 60,
      "height": 20,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "text": "API",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "seed": 5,
      "version": 1,
      "versionNonce": 0,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1,
      "link": null,
      "locked": false,
      "containerId": null,
      "originalText": "API",
      "lineHeight": 1.25
    },
    {
      "id": "a2",
      "type": "arrow",
      "x": 390,
      "y": 130,
      "width": 60,
      "height": 0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "points": [
        [0, 0],
        [60, 0]
      ],
      "lastCommittedPoint": null,
      "startBinding": null,
      "endBinding": null,
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "seed": 6,
      "version": 1,
      "versionNonce": 0,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1,
      "link": null,
      "locked": false
    },
    {
      "id": "r3",
      "type": "rectangle",
      "x": 450,
      "y": 100,
      "width": 140,
      "height": 60,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#c3fae8",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "roundness": { "type": 3 },
      "seed": 7,
      "version": 1,
      "versionNonce": 0,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1,
      "link": null,
      "locked": false
    },
    {
      "id": "t3",
      "type": "text",
      "x": 485,
      "y": 120,
      "width": 70,
      "height": 20,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "text": "Database",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "seed": 8,
      "version": 1,
      "versionNonce": 0,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1,
      "link": null,
      "locked": false,
      "containerId": null,
      "originalText": "Database",
      "lineHeight": 1.25
    }
  ],
  "appState": { "gridSize": null, "viewBackgroundColor": "#ffffff" },
  "files": {}
}
```

---

## Notes

- MCP server binary: `~/Documents/GitHub/excalidraw-mcp/dist/index.js --stdio`
- Export helper: `~/agent-os/bin/excalidraw_export.js`
- Diagrams saved to: `~/agent-os/diagrams/`
- Claude Desktop MCP config: already includes excalidraw entry
- Always generate unique element IDs (short descriptive strings)
- Always include ALL required fields per element (no missing keys)
