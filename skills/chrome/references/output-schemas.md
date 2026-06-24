# Output schemas

All commands print JSON to stdout.

## Common error shape

```json
{
  "error": {
    "code": "captcha",
    "message": "Human-readable explanation",
    "remediation": "Optional next step"
  }
}
```

## cdp launch

```json
{
  "command": "cdp",
  "action": "launch",
  "session_id": "a1b2c3d4",
  "port": 54321,
  "headed": false,
  "error": null
}
```

## cdp navigate

```json
{
  "command": "cdp",
  "action": "navigate",
  "session_id": "a1b2c3d4",
  "url": "https://example.com",
  "final_url": "https://example.com/",
  "wait": "load",
  "error": null
}
```

## extract article

```json
{
  "command": "extract",
  "mode": "article",
  "url": "https://example.com/",
  "final_url": "https://example.com/",
  "title": "Example Domain",
  "description": null,
  "canonical": null,
  "content_markdown": "# Example Domain\n\n...",
  "headings": [{ "level": 1, "text": "Example Domain" }],
  "word_count": 42,
  "fetched_at": "2026-06-24T12:00:00+00:00",
  "error": null
}
```

## extract serp

```json
{
  "command": "extract",
  "mode": "serp",
  "engine": "google",
  "results": [
    { "rank": 1, "title": "...", "url": "https://...", "snippet": "..." }
  ],
  "result_count": 10,
  "fetched_at": "2026-06-24T12:00:00+00:00",
  "error": null
}
```

## search

```json
{
  "command": "search",
  "query": "python asyncio",
  "engine": "google",
  "results": [
    { "rank": 1, "title": "...", "url": "https://...", "snippet": "..." }
  ],
  "result_count": 10,
  "error": null
}
```

## fetch

```json
{
  "command": "fetch",
  "url": "https://example.com",
  "final_url": "https://example.com/",
  "title": "Example Domain",
  "description": null,
  "content_markdown": "# Example Domain\n\n...",
  "headings": [{ "level": 1, "text": "Example Domain" }],
  "word_count": 42,
  "fetched_at": "2026-06-24T12:00:00+00:00",
  "error": null
}
```

## extract layout

```json
{
  "command": "extract",
  "mode": "layout",
  "viewport": { "width": 1280, "height": 720, "scrollWidth": 1280, "scrollHeight": 2400 },
  "overflow": { "horizontal": false, "vertical": true },
  "elements": [
    {
      "selector": "main",
      "path": "main",
      "role": "main",
      "box": { "x": 0, "y": 64, "width": 1280, "height": 800 },
      "styles": {
        "marginTop": "0px",
        "marginBottom": "0px",
        "paddingTop": "24px",
        "fontSize": "16px",
        "lineHeight": "24px"
      },
      "visible": true
    }
  ],
  "pairs": [
    { "a": "h1", "b": "p", "gap": 16, "axis": "vertical" }
  ],
  "issues": [
    {
      "rule": "spacing.below-heading",
      "severity": "warn",
      "message": "h1 → p gap 8px, expected >= 12px",
      "selector": "h1"
    }
  ],
  "issue_count": 1,
  "fetched_at": "2026-06-24T12:00:00+00:00",
  "error": null
}
```

## extract a11y

```json
{
  "command": "extract",
  "mode": "a11y",
  "nodes": [{ "role": "button", "name": "Submit", "nodeId": "42" }],
  "node_count": 120,
  "issues": [
    {
      "rule": "a11y.name.missing",
      "severity": "error",
      "message": "Interactive element role=\"button\" has no accessible name",
      "selector": null
    }
  ],
  "issue_count": 1,
  "fetched_at": "2026-06-24T12:00:00+00:00",
  "error": null
}
```

## cdp emulate

```json
{
  "command": "cdp",
  "action": "emulate",
  "session_id": "a1b2c3d4",
  "width": 375,
  "height": 667,
  "device_scale_factor": 1.0,
  "mobile": false,
  "error": null
}
```

## cdp screenshot

```json
{
  "command": "cdp",
  "action": "screenshot",
  "session_id": "a1b2c3d4",
  "path": "/tmp/page.png",
  "format": "png",
  "base64": null,
  "size_bytes": 45230,
  "error": null
}
```

## audit

```json
{
  "command": "audit",
  "url": "http://localhost:5173/",
  "viewports": ["375x667", "1280x720"],
  "viewport_results": [],
  "issues": [
    {
      "rule": "overflow.horizontal",
      "severity": "error",
      "message": "Horizontal overflow detected",
      "selector": null,
      "viewport": "375x667"
    }
  ],
  "issue_count": 1,
  "error_count": 1,
  "warn_count": 0,
  "passed": false,
  "error": null
}
```
