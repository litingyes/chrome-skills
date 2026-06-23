# Fetch recipe

One-shot article extraction from a URL. Equivalent manual composition:

```bash
SESSION=$(skills/chrome/scripts/cdp launch | python3 -c "import sys,json; print(json.load(sys.stdin)['session_id'])")
skills/chrome/scripts/cdp navigate --session "$SESSION" --url "https://example.com" --wait networkidle
skills/chrome/scripts/extract article --session "$SESSION"
skills/chrome/scripts/cdp close --session "$SESSION"
```

## CLI

```bash
skills/chrome/scripts/fetch "https://example.com"
skills/chrome/scripts/fetch "https://example.com" --timeout-ms 30000
skills/chrome/scripts/fetch "https://example.com" --headed --user-data-dir "/path/to/profile"
```

## Output

See [output-schemas.md](output-schemas.md#fetch).

## Edge cases

| Case | Behavior |
|------|----------|
| Timeout | `error.code=fetch` with timeout message |
| Empty body | `content_markdown` may be empty; check `word_count` |
| JS-heavy SPA | Uses `networkidle` wait; increase `--timeout-ms` if needed |
| Auth required | Use `cdp launch --user-data-dir` and compose manually |

## When to prefer `fetch` vs manual `extract`

- **Single URL** → `fetch`
- **Several URLs in one browser** → `cdp launch` + repeated `navigate` + `extract article` + `cdp close`
