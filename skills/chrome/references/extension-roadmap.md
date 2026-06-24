# Extension roadmap (chrome-only)

All Chrome capabilities live inside the `chrome` hub skill. This repo does **not** use or document external MCP servers (e.g. chrome-devtools-mcp). New needs are added as `cdp` actions, `extract` modes, or recipes.

## Implemented

| Layer | Command | Purpose |
|-------|---------|---------|
| L2 | `extract layout` | Spacing, alignment, overflow, touch-target rules |
| L2 | `extract a11y` | Accessibility tree + basic a11y issues |
| L1 | `cdp emulate` / `screenshot` | Multi-viewport + visual capture |
| L3 | `audit` | Multi-viewport layout verification recipe |

## Planned extensions (add when needed)

| Capability | Suggested layer | CDP / browser API |
|------------|-----------------|-------------------|
| FCP / LCP / TTFB | L2 `extract perf` | `Performance` API via `Runtime.evaluate` + post-load wait |
| CLS / INP | L2 `extract perf` or L1 `cdp trace` | `PerformanceObserver` or CDP `Tracing` |
| Render-blocking resources | L2 `extract network` | `Network.enable` + `performance.getEntriesByType('resource')` |
| Design token validation | L2 `extract styles` | `getComputedStyle` + token JSON |

Future recipe: `audit --include-perf` to combine layout + first-paint metrics in one dev loop.

## Trade-offs

**Advantages:** no MCP setup, one `/chrome` entry point, composable with existing `audit` workflow.

**Cost:** deep diagnostics (LCP element breakdown, CLS culprit attribution) require custom trace parsing — accepted; implement incrementally inside `skills/chrome/scripts/lib/` when needed.

## How to extend

Follow [AGENTS.md](../../../AGENTS.md): pick layer (L1/L2/L3), implement in `scripts/lib/`, update `references/<command>.md` and `output-schemas.md`.
