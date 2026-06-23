# Chrome skill examples

Run from the repository root unless noted.

## One-shot fetch

```bash
skills/chrome/scripts/fetch "https://example.com"
```

## One-shot Google search

```bash
skills/chrome/scripts/search "python asyncio" --limit 5
```

## Multi-page session

```bash
SESSION=$(skills/chrome/scripts/cdp launch | python3 -c "import sys,json; print(json.load(sys.stdin)['session_id'])")
skills/chrome/scripts/cdp navigate --session "$SESSION" --url "https://example.com" --wait networkidle
skills/chrome/scripts/extract article --session "$SESSION"
skills/chrome/scripts/cdp navigate --session "$SESSION" --url "https://www.iana.org/domains/example" --wait load
skills/chrome/scripts/extract article --session "$SESSION"
skills/chrome/scripts/cdp close --session "$SESSION"
```

## Manual Google SERP (headed + profile)

```bash
SESSION=$(skills/chrome/scripts/cdp launch --headed --user-data-dir "$HOME/Library/Application Support/Google/Chrome" | python3 -c "import sys,json; print(json.load(sys.stdin)['session_id'])")
skills/chrome/scripts/cdp navigate --session "$SESSION" --url "https://www.google.com/search?q=python" --wait networkidle
skills/chrome/scripts/extract serp --session "$SESSION" --limit 10
skills/chrome/scripts/cdp close --session "$SESSION"
```

## Custom JavaScript

```bash
skills/chrome/scripts/cdp evaluate --session "$SESSION" --expr "document.title"
```

## Cleanup stale sessions

```bash
skills/chrome/scripts/cdp close --all
```
