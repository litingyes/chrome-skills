# chrome-skills

Agent skills that expose Chrome capabilities to AI agents.

## What this is

**chrome-skills** is a curated collection of [Agent Skills](https://cursor.com/docs/skills) distilled from the Chrome ecosystem. The catalog uses a **hub skill** model: a single `chrome` skill carries Chrome automation capabilities, and sub-capabilities are exposed as internal commands (`/chrome <command>`) rather than separate skills. This keeps agent context lean while still supporting composable workflows.

**v1** ships CDP-based browser automation inside `chrome` — `cdp` atoms, `extract` modes (`article`, `serp`, `layout`, `a11y`), and `search` / `fetch` / `audit` recipes. The `audit` recipe and `extract layout` / `extract a11y` modes support multi-viewport UI layout verification on dev URLs.

Long-term scope (not all implemented yet):

- **Browser automation** — CDP workflows inside `chrome` (navigation, extraction, search, UI audit; patterns aligned with tools like agent-browser)
- **Performance & debugging** — future `chrome` commands (`extract perf`, `extract network`; see `skills/chrome/references/extension-roadmap.md`)
- **Chrome Extension / Platform APIs** — distilled knowledge from official Chrome docs, structured for agent use

## Why

Agents need version-aware, actionable workflows — not doc dumps. Skills bridge that gap: they tell an agent *when* to act, *what* to run, and *how* to handle common failure modes. A hub skill with internal commands avoids loading many skill files into context for every task.

## Repository layout

```text
chrome-skills/
├── skills/
│   └── chrome/                 # Current published Chrome skill (hub)
│       ├── SKILL.md            # Command router + index (keep lean)
│       ├── examples.md
│       ├── references/         # Per-command docs (progressive disclosure)
│       │   ├── cdp.md
│       │   ├── extract.md
│       │   ├── search.md
│       │   ├── fetch.md
│       │   ├── audit.md
│       │   ├── output-schemas.md
│       │   ├── cdp-patterns.md
│       │   └── extension-roadmap.md
│       └── scripts/            # CLI entrypoints (cdp / extract / search / fetch / audit)
├── website/                    # Project landing page (Vite + React, en / zh-CN)
├── PRODUCT.md                  # Brand and product principles (website copy reference)
├── skills-lock.json            # Locked third-party / tooling skill refs
├── AGENTS.md                   # Instructions for coding agents
└── .agents/skills/             # Local runtime copies (gitignored)
```

- **`skills/`** — source of truth for published skills
- **`website/`** — marketing landing page; not part of skill runtime
- **`AGENTS.md`** — conventions and workflows for agents editing this repo (see [AGENTS.md](AGENTS.md))
- **`.agents/skills/`**, **`.claude/skills/`** — local copies for agent runtimes; not committed

## Using skills

Agents discover skills via the `description` field in each skill's YAML frontmatter. The `chrome` skill uses `disable-model-invocation: true` — invoke it explicitly with `/chrome`.

### Quick start (`chrome`)

1. Add the skill with Skills CLI (primary path):

   ```bash
   npx skills add litingyes/chrome-skills
   ```

   Or symlink from a clone into your runtime:

   | Runtime | Typical path |
   |---------|--------------|
   | Cursor (project) | `.agents/skills/<skill-name>/` |
   | Cursor (personal) | `~/.cursor/skills/<skill-name>/` |
   | Claude Code | `.claude/skills/<skill-name>/` |

   ```bash
   ln -s ../../skills/chrome .agents/skills/chrome
   ```

2. Install script dependencies once (requires Chrome or Chromium and Python 3.10+):

   ```bash
   skills/chrome/scripts/setup
   ```

3. Invoke via `/chrome` in your agent, for example:
   - `/chrome fetch https://example.com`
   - `/chrome search python asyncio`
   - `/chrome audit "http://localhost:5173" --viewports 375,1280`
   - `/chrome cdp launch` (then compose `navigate`, `extract`, `close`)

### Command layers

| Command | Layer | Purpose |
|---------|-------|---------|
| `cdp` | L1 atomic | `launch` · `navigate` · `wait` · `evaluate` · `snapshot` · `emulate` · `resize` · `screenshot` · `close` |
| `extract` | L2 compose | Extract from current page: `article` · `serp` · `layout` · `a11y` |
| `search` | L3 recipe | Google search one-shot |
| `fetch` | L3 recipe | Single-URL article extraction one-shot |
| `audit` | L3 recipe | Multi-viewport UI layout verification on a dev URL |

Workflow details: [skills/chrome/SKILL.md](skills/chrome/SKILL.md) and [skills/chrome/examples.md](skills/chrome/examples.md).

## Available skills

| Skill | Description | Status |
|-------|-------------|--------|
| `chrome` | Hub skill for local Chrome automation via composable commands (`cdp`, `extract`, `search`, `fetch`, `audit`) — including layout/a11y extraction and UI audit recipes | Available |

New Chrome capabilities should be added as **internal commands** inside `chrome` rather than new top-level skills — unless they belong to a fully separate domain (e.g. Chrome Extension Platform APIs).

**Roadmap domains:** browser automation (in `chrome` today), performance & network (future `chrome` commands), Extension / Platform APIs.

> **Note:** `skill-creator` (from [anthropics/skills](https://github.com/anthropics/skills)) is internal dev tooling for authoring skills. It is tracked in `skills-lock.json` but is not a published Chrome skill.

## Website

The [website/](website/) directory is the project landing page (architecture overview, command reference, install steps). Local development:

```bash
cd website && pnpm install && pnpm dev
```

Brand and copy principles: [PRODUCT.md](PRODUCT.md).

## Contributing

Follow [AGENTS.md](AGENTS.md) for agent-oriented conventions. In short:

### Default path — extend `chrome` with a new command

Work in [skills/chrome/](skills/chrome/):

| Layer | What to add |
|-------|-------------|
| L1 atomic | New `cdp` action in `scripts/cdp` + update `references/cdp.md` |
| L2 compose | New `extract` mode in `scripts/extract` + `lib/extract_*.py` + `references/extract.md` |
| L3 recipe | New recipe script + `lib/recipes.py` (or dedicated lib, e.g. `layout_probe.py` for `audit`) + `references/<name>.md` |

Also update `SKILL.md` command index and `references/output-schemas.md`.

### Exception — new top-level skill

Only for a genuinely independent domain (e.g. Chrome Extension Platform APIs). Create `skills/<skill-name>/SKILL.md` as usual.

### Pull request checklist

- Valid `name` and `description` frontmatter where applicable
- Copy-pasteable CLI commands; JSON output documented
- Prerequisites listed (Chrome/Chromium, Python, `scripts/setup`)
- Smoke-tested commands; do **not** commit `scripts/vendor/` or `__pycache__/`

## License

Apache License 2.0 — see [LICENSE](LICENSE).
