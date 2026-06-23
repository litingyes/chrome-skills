# Extract commands

L2 commands extract structured data from the **current page** in an existing session. They do not navigate.

## Modes

### article

```bash
skills/chrome/scripts/extract article --session <id>
```

Output: article JSON (title, description, content_markdown, headings, word_count). Same schema as `fetch`.

Use after `cdp navigate` when building multi-page flows.

### serp

```bash
skills/chrome/scripts/extract serp --session <id> --limit 10
```

Output: Google SERP results array. Use when the current page is a Google search results page.

Detects CAPTCHA / bot-check pages and returns `error.code=captcha` with remediation hints.

## Multi-page workflow

```bash
SESSION=$(skills/chrome/scripts/cdp launch | python3 -c "import sys,json; print(json.load(sys.stdin)['session_id'])")
skills/chrome/scripts/cdp navigate --session "$SESSION" --url "https://a.example" --wait networkidle
skills/chrome/scripts/extract article --session "$SESSION"
skills/chrome/scripts/cdp navigate --session "$SESSION" --url "https://b.example" --wait networkidle
skills/chrome/scripts/extract article --session "$SESSION"
skills/chrome/scripts/cdp close --session "$SESSION"
```

## vs `cdp evaluate`

| Tool | When |
|------|------|
| `extract` | Built-in, schema-stable extraction (`article`, `serp`) |
| `cdp evaluate` | Custom JS, prototyping, one-off selectors |

## Errors

| Code | Meaning |
|------|---------|
| `captcha` | Google bot-check page (serp mode) |
| `parse` | Page loaded but no results parsed |
| `extract` | Runtime failure during extraction |
