# CDP patterns (agent-browser reference)

This skill does **not** invoke `agent-browser`. Use this table to map concepts when reading agent-browser docs or debugging.

| chrome skill | agent-browser equivalent | Notes |
|--------------|-------------------------|-------|
| `cdp launch` | `agent-browser open` (starts session) | Default headless; `--headed` shows window |
| `cdp navigate` | `agent-browser open <url>` | Reuses existing session |
| `cdp wait --load` | `agent-browser wait --load domcontentloaded` | Polls `document.readyState` |
| `cdp wait --networkidle` | `agent-browser wait --load networkidle` | Heuristic idle detection |
| `cdp wait --selector` | `agent-browser wait @ref` / `wait <selector>` | CSS selector |
| `cdp wait --text` | `agent-browser wait --text "..."` | Substring match |
| `cdp evaluate` | `agent-browser eval --stdin` | Custom JS |
| `cdp snapshot` | `agent-browser snapshot` (metadata only) | Full a11y tree not in v1 |
| `extract article` | `agent-browser get text` + structuring | Fixed article JSON schema |
| `extract serp` | Manual eval on Google SERP | Built-in selectors + captcha detect |
| `fetch` | open + wait + extract | One-shot recipe |
| `search` | open Google + fill/search + extract | One-shot recipe |

## Launch args borrowed from automation practice

- `--headless=new`
- `--disable-blink-features=AutomationControlled`
- `--remote-debugging-port=<port>`
- `--user-data-dir=<dir>` for profile/cookie reuse

## Waiting guidance

Prefer explicit waits over fixed sleeps:

1. After navigate: `--wait load` or `networkidle`
2. Before extract: `cdp wait --networkidle` if page is SPA-heavy
3. Use `cdp evaluate` only when built-in extract modes are insufficient

## Further reading

- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [agent-browser repository](https://github.com/vercel-labs/agent-browser) for workflow inspiration
