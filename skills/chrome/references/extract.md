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

### layout

```bash
skills/chrome/scripts/extract layout --session <id>
skills/chrome/scripts/extract layout --session <id> \
  --selectors "main,nav,button,[data-testid]" \
  --rules spacing,alignment,overflow,touch-target
```

Output: viewport metrics, element boxes/styles, spacing pairs, and `issues[]` from built-in UI rules.

**Rules:** `spacing`, `alignment`, `overflow`, `touch-target`, `blank`

Use after `cdp navigate` on a dev URL to verify rendered layout. Prefer the `audit` recipe for multi-viewport sweeps.

### a11y

```bash
skills/chrome/scripts/extract a11y --session <id>
```

Output: flattened accessibility tree nodes and `issues[]` (missing names, missing main landmark, etc.).

## UI verification workflow

```bash
SESSION=$(skills/chrome/scripts/cdp launch --viewport 1280x720 | python3 -c "import sys,json; print(json.load(sys.stdin)['session_id'])")
skills/chrome/scripts/cdp navigate --session "$SESSION" --url "http://localhost:5173/" --wait networkidle
skills/chrome/scripts/extract layout --session "$SESSION" --rules spacing,overflow,touch-target
skills/chrome/scripts/cdp close --session "$SESSION"
```

Or use the one-shot `audit` recipe — see [audit.md](audit.md).

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
| `extract` | Built-in, schema-stable extraction (`article`, `serp`, `layout`, `a11y`) |
| `cdp evaluate` | Custom JS, prototyping, one-off selectors |

## Errors

| Code | Meaning |
|------|---------|
| `captcha` | Google bot-check page (serp mode) |
| `parse` | Page loaded but no results parsed |
| `extract` | Runtime failure during extraction |
