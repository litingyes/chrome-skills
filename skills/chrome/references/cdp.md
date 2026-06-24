# CDP atomic commands

L1 commands drive a persistent browser session. All actions except `launch` require `--session`.

## Session lifecycle

```bash
skills/chrome/scripts/cdp launch
# → { "session_id": "a1b2c3d4", ... }

skills/chrome/scripts/cdp close --session <id>
skills/chrome/scripts/cdp close --all
```

Sessions are stored in `~/.cache/chrome-skill/sessions/`. Stale sessions (>24h) are cleaned on launch.

## Actions

### launch

```bash
skills/chrome/scripts/cdp launch
skills/chrome/scripts/cdp launch --headed
skills/chrome/scripts/cdp launch --user-data-dir "/path/to/profile"
skills/chrome/scripts/cdp launch --viewport 1280x720
```

### navigate

```bash
skills/chrome/scripts/cdp navigate --session <id> --url "https://example.com"
skills/chrome/scripts/cdp navigate --session <id> --url "https://example.com" --wait networkidle
skills/chrome/scripts/cdp navigate --session <id> --url "https://example.com" --wait none
```

`--wait`: `load` (default), `networkidle`, `none`

### wait

```bash
skills/chrome/scripts/cdp wait --session <id> --load
skills/chrome/scripts/cdp wait --session <id> --networkidle
skills/chrome/scripts/cdp wait --session <id> --selector "#main"
skills/chrome/scripts/cdp wait --session <id> --text "Success"
```

At least one condition flag is required.

### evaluate

```bash
skills/chrome/scripts/cdp evaluate --session <id> --expr "document.title"
cat script.js | skills/chrome/scripts/cdp evaluate --session <id>
```

Use for custom extraction when `extract` modes are not enough.

### snapshot

```bash
skills/chrome/scripts/cdp snapshot --session <id>
skills/chrome/scripts/cdp snapshot --session <id> --include-html
```

Returns title, url, and html length (or full html with `--include-html`). Not a substitute for `extract article`.

### emulate

```bash
skills/chrome/scripts/cdp emulate --session <id> --width 375 --height 667
skills/chrome/scripts/cdp emulate --session <id> --width 1280 --height 720 --mobile
```

Sets viewport via `Emulation.setDeviceMetricsOverride`. Use between layout extractions for responsive checks.

### resize

```bash
skills/chrome/scripts/cdp resize --session <id> --width 1280 --height 720
```

Alias for `emulate` without mobile/scale options.

### screenshot

```bash
skills/chrome/scripts/cdp screenshot --session <id> --path /tmp/page.png
skills/chrome/scripts/cdp screenshot --session <id> --path /tmp/full.png --full-page
```

Captures PNG via `Page.captureScreenshot`. Use for visual review or vision-model polish checks.

### close

```bash
skills/chrome/scripts/cdp close --session <id>
skills/chrome/scripts/cdp close --all
```

## Composition pattern

```bash
SESSION=$(skills/chrome/scripts/cdp launch | python3 -c "import sys,json; print(json.load(sys.stdin)['session_id'])")
skills/chrome/scripts/cdp navigate --session "$SESSION" --url "https://example.com"
skills/chrome/scripts/cdp evaluate --session "$SESSION" --expr "document.title"
skills/chrome/scripts/cdp close --session "$SESSION"
```

## Errors

Failures return JSON with `error.code` and `error.message`. Common codes: `timeout`, `session`, `cdp`.
