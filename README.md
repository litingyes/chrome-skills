# chrome-skills

Agent skills that expose Chrome capabilities to AI agents.

## What this is

**chrome-skills** is a curated collection of [Agent Skills](https://cursor.com/docs/skills) distilled from the Chrome ecosystem. Each skill encodes reliable workflows — triggers, steps, and guardrails — so agents can use Chrome capabilities without wading through raw documentation.

Long-term scope:

- **Browser automation** — CDP-based workflows (navigation, snapshots, forms, screenshots; patterns aligned with tools like agent-browser)
- **Chrome DevTools MCP** — performance audits, debugging, network inspection, accessibility checks
- **Chrome Extension / Platform APIs** — distilled knowledge from official Chrome docs, structured for agent use

## Why

Agents need version-aware, actionable workflows — not doc dumps. Skills bridge that gap: they tell an agent *when* to act, *what* to run, and *how* to handle common failure modes.

## Repository layout

```text
chrome-skills/
├── skills/                  # Canonical, versioned skills (committed)
│   └── <skill-name>/
│       └── SKILL.md
├── skills-lock.json         # Locked third-party / tooling skill refs
├── AGENTS.md                # Instructions for coding agents
└── .agents/skills/          # Local runtime copies (gitignored)
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

Each skill is a directory with a `SKILL.md` file. Agents discover skills via the `description` field in the YAML frontmatter.

Install UX may evolve as the catalog grows; for now, manual copy/symlink is sufficient.

## Available skills

| Skill | Description | Status |
|-------|-------------|--------|
| — | No Chrome skills published yet | Planned |

**Roadmap domains:** browser automation (CDP), Chrome DevTools MCP, Extension / Platform APIs.

> **Note:** `skill-creator` (from [anthropics/skills](https://github.com/anthropics/skills)) is internal dev tooling for authoring skills. It is tracked in `skills-lock.json` but is not a published Chrome skill.

## Contributing

1. Add a new skill under `skills/<skill-name>/` with a `SKILL.md` file.
2. Follow the authoring conventions in [AGENTS.md](AGENTS.md).
3. Open a pull request with:
   - Valid `name` and `description` frontmatter (third-person, includes trigger terms)
   - Tested, copy-pasteable workflow steps
   - Prerequisites listed if the skill depends on Chrome, MCP servers, or CLI tools

Keep changes focused. Match the structure of existing skills when the catalog grows.

## License

Apache License 2.0 — see [LICENSE](LICENSE).
