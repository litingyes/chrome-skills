---
name: chrome
description: Runs local headless Chrome via composable cdp commands, session-based extract, and search/fetch recipes. Use when the user invokes /chrome, asks for browser CDP automation, page extraction, Google search, or structured content from a URL.
disable-model-invocation: true
---

# Chrome

Composable local Chrome automation for agents. Four top-level commands:

| Command | Layer | Purpose |
|---------|-------|---------|
| `cdp` | L1 atomic | Launch, navigate, wait, evaluate, snapshot, close |
| `extract` | L2 compose | Extract structured data from the **current** page (`article`, `serp`) |
| `search` | L3 recipe | Google search one-shot |
| `fetch` | L3 recipe | Single-URL article extraction one-shot |

## Prerequisites

- Google Chrome or Chromium installed locally
- Python 3.10+
- Install once:

```bash
skills/chrome/scripts/setup
```

This installs Python dependencies into `skills/chrome/scripts/vendor/`.

Optional: set `CHROME_PATH` to override Chrome binary discovery.

## Routing

1. Parse the first token after `/chrome`: `cdp`, `extract`, `search`, or `fetch`.
2. Read **only** `skills/chrome/references/<token>.md` for workflow details.
3. Run the matching script under `skills/chrome/scripts/`.
4. Scripts print JSON to stdout. Summarize for the user; keep the JSON for reasoning.

Script paths (run from repo root):

```bash
skills/chrome/scripts/cdp <action> [options]
skills/chrome/scripts/extract <mode> --session <id>
skills/chrome/scripts/search "<query>"
skills/chrome/scripts/fetch "<url>"
```

## When to use which layer

- **One URL, article content** → `fetch`
- **Google search** → `search`
- **Multiple pages in one browser** → `cdp launch` → `navigate` + `extract` (repeat) → `cdp close`
- **Custom JS or debugging** → `cdp evaluate`
- **CAPTCHA / bot check on Google** → see `references/search.md`; retry with `cdp launch --headed --user-data-dir <profile>`

## Command index

### `cdp` actions

`launch` · `navigate` · `wait` · `evaluate` · `snapshot` · `close`

Details: [references/cdp.md](references/cdp.md)

### `extract` modes

`article` · `serp`

Requires `--session`. Details: [references/extract.md](references/extract.md)

### Recipes

- `search "<query>"` — [references/search.md](references/search.md)
- `fetch "<url>"` — [references/fetch.md](references/fetch.md)

JSON schemas: [references/output-schemas.md](references/output-schemas.md)

## Additional resources

- [examples.md](examples.md) — copy-paste flows
- [references/cdp-patterns.md](references/cdp-patterns.md) — agent-browser concept mapping
