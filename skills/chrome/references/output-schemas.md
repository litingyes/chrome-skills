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
