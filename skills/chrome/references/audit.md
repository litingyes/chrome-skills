# Audit command

L3 recipe for UI layout verification on a dev URL. Composes `cdp launch` → `navigate` → `emulate` (per viewport) → `extract layout` → optional `screenshot` / `extract a11y` → `cdp close`.

## When to use

- After changing CSS/components on a local dev server (`http://localhost:<port>`)
- Before claiming UI work is done — **never trust CSS alone**
- When spacing, alignment, overflow, or touch-target issues are suspected

## Command

```bash
skills/chrome/scripts/audit "http://localhost:5173/" \
  --viewports 375,768,1280 \
  --selectors "main,[data-testid=hero],nav" \
  --rules spacing,alignment,overflow,touch-target
```

### Options

| Flag | Default | Purpose |
|------|---------|---------|
| `--viewports` | `375,1280` | Comma-separated widths (`375`) or `WxH` pairs (`375x667`) |
| `--selectors` | built-in landmarks | Limit element probes |
| `--rules` | all layout rules | `spacing`, `alignment`, `overflow`, `touch-target`, `blank` |
| `--include-screenshot` | off | Save PNG per viewport for visual review |
| `--include-a11y` | off | Run `extract a11y` on last viewport |
| `--wait-selector` | none | Wait for SPA content (e.g. `#root main`) |
| `--headed` | off | Show browser window |
| `--timeout-ms` | 25000 | Navigation and wait timeout |

## Output

Returns aggregated `issues[]` across viewports. Each issue has:

- `rule` — machine-readable rule id (e.g. `spacing.below-heading`)
- `severity` — `error`, `warn`, or `info`
- `message` — human-readable explanation
- `selector` — element path when applicable
- `viewport` — e.g. `375x667`

Top-level fields: `passed` (no errors), `issue_count`, `error_count`, `warn_count`, `viewport_results`.

## Agent workflow

1. Change CSS/components on dev server
2. Run `audit` with mobile + desktop viewports
3. If `issues` non-empty → fix by `selector` + `rule`, re-run
4. When layout `issues` clear → optional `--include-screenshot` for visual polish review
5. For LCP / CLS / first-paint metrics → future `extract perf` (see [extension-roadmap.md](extension-roadmap.md))

## Equivalent manual steps

```bash
SESSION=$(skills/chrome/scripts/cdp launch --viewport 1280x720 | python3 -c "import sys,json; print(json.load(sys.stdin)['session_id'])")
skills/chrome/scripts/cdp navigate --session "$SESSION" --url "http://localhost:5173/" --wait networkidle
skills/chrome/scripts/cdp emulate --session "$SESSION" --width 375 --height 667
skills/chrome/scripts/extract layout --session "$SESSION" --rules spacing,overflow
skills/chrome/scripts/cdp emulate --session "$SESSION" --width 1280 --height 720
skills/chrome/scripts/extract layout --session "$SESSION"
skills/chrome/scripts/cdp close --session "$SESSION"
```

## Principles

- **Never trust CSS alone** — always verify rendered layout
- **Always multi-viewport** — spacing bugs often appear only on mobile
- **Issues are facts** — prefer `issues[]` over reading `outerHTML`
- **Close sessions** — audit closes automatically; manual flows need `cdp close`

## Errors

| Code | Meaning |
|------|---------|
| `audit` | Navigation, timeout, or extraction failure |
| `timeout` | Page did not load in time |
| `session` | Browser session invalid |
