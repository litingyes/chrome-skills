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

## UI layout audit (dev server)

After CSS/component changes on a local app:

```bash
skills/chrome/scripts/audit "http://localhost:5173/" \
  --viewports 375,768,1280 \
  --selectors "main,nav,button,[data-testid]" \
  --rules spacing,alignment,overflow,touch-target
```

Fix issues from `issues[]` until `passed: true`. For visual polish:

```bash
skills/chrome/scripts/audit "http://localhost:5173/" --include-screenshot --include-a11y
```

## Manual layout extract

```bash
SESSION=$(skills/chrome/scripts/cdp launch --viewport 1280x720 | python3 -c "import sys,json; print(json.load(sys.stdin)['session_id'])")
skills/chrome/scripts/cdp navigate --session "$SESSION" --url "http://localhost:5173/" --wait networkidle
skills/chrome/scripts/extract layout --session "$SESSION" --rules spacing,overflow
skills/chrome/scripts/cdp emulate --session "$SESSION" --width 375 --height 667
skills/chrome/scripts/extract layout --session "$SESSION"
skills/chrome/scripts/cdp screenshot --session "$SESSION" --path /tmp/ui-375.png
skills/chrome/scripts/cdp close --session "$SESSION"
```

## Screenshot for visual review

```bash
skills/chrome/scripts/cdp screenshot --session "$SESSION" --path /tmp/page.png
```
