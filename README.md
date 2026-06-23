# chrome-skills

Agent skills that expose Chrome capabilities to AI agents.

## What this is

**chrome-skills** is a curated collection of [Agent Skills](https://cursor.com/docs/skills) distilled from the Chrome ecosystem. The catalog uses a **hub skill** model: a single `chrome` skill carries Chrome automation capabilities, and sub-capabilities are exposed as internal commands (`/chrome <command>`) rather than separate skills. This keeps agent context lean while still supporting composable workflows.

**v1** ships CDP-based browser automation inside `chrome` — `cdp` atoms, `extract` modes, and `search` / `fetch` recipes.

Long-term scope (not all implemented yet):

- **Browser automation** — CDP workflows inside `chrome` (navigation, extraction, search; patterns aligned with tools like agent-browser)
- **Chrome DevTools MCP** — performance audits, debugging, network inspection, accessibility checks
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
│       │   └── fetch.md
│       └── scripts/            # CLI entrypoints (cdp / extract / search / fetch)
├── skills-lock.json            # Locked third-party / tooling skill refs
├── AGENTS.md                   # Instructions for coding agents
└── .agents/skills/             # Local runtime copies (gitignored)
```

- **`skills/`** — source of truth for published skills
- **`AGENTS.md`** — conventions and workflows for agents editing this repo (see [AGENTS.md](AGENTS.md))
- **`.agents/skills/`**, **`.claude/skills/`** — local copies for agent runtimes; not committed

## Using skills

Copy or symlink skills into your agent's skill directory:

| Runtime | Typical path |
|---------|--------------|
| Cursor (project) | `.agents/skills/<skill-name>/` |
| Cursor (personal) | `~/.cursor/skills/<skill-name>/` |
| Claude Code | `.claude/skills/<skill-name>/` |

Agents discover skills via the `description` field in each skill's YAML frontmatter. The `chrome` skill uses `disable-model-invocation: true` — invoke it explicitly with `/chrome`.

### Quick start (`chrome`)

1. Symlink or copy the skill into your runtime:

   ```bash
   ln -s ../../skills/chrome .agents/skills/chrome
   ```

2. Install script dependencies (once):

   ```bash
   skills/chrome/scripts/setup
   ```

3. Invoke via `/chrome` in your agent, for example:
   - `/chrome fetch https://example.com`
   - `/chrome search python asyncio`
   - `/chrome cdp launch` (then compose `navigate`, `extract`, `close`)

### Command layers

| Command | Layer | Purpose |
|---------|-------|---------|
| `cdp` | L1 atomic | `launch` · `navigate` · `wait` · `evaluate` · `snapshot` · `close` |
| `extract` | L2 compose | Extract from current page: `article` · `serp` |
| `search` | L3 recipe | Google search one-shot |
| `fetch` | L3 recipe | Single-URL article extraction one-shot |

Workflow details: [skills/chrome/SKILL.md](skills/chrome/SKILL.md) and [skills/chrome/examples.md](skills/chrome/examples.md).

## Available skills

| Skill | Description | Status |
|-------|-------------|--------|
| `chrome` | Hub skill for local Chrome automation via composable commands (`cdp`, `extract`, `search`, `fetch`) | Available |

New Chrome capabilities should be added as **internal commands** inside `chrome` rather than new top-level skills — unless they belong to a fully separate domain (e.g. a future DevTools MCP skill).

**Roadmap domains:** browser automation (CDP, in `chrome` today), Chrome DevTools MCP, Extension / Platform APIs.

> **Note:** `skill-creator` (from [anthropics/skills](https://github.com/anthropics/skills)) is internal dev tooling for authoring skills. It is tracked in `skills-lock.json` but is not a published Chrome skill.

## Contributing

Follow [AGENTS.md](AGENTS.md) for agent-oriented conventions. In short:

### Default path — extend `chrome` with a new command

Work in [skills/chrome/](skills/chrome/):

| Layer | What to add |
|-------|-------------|
| L1 atomic | New `cdp` action in `scripts/cdp` + update `references/cdp.md` |
| L2 compose | New `extract` mode in `scripts/extract` + `lib/extract_*.py` + `references/extract.md` |
| L3 recipe | New recipe script + `lib/recipes.py` + `references/<name>.md` |

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
