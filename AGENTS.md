# Agent Instructions

## Project overview

**chrome-skills** extracts, normalizes, and maintains agent skills from Chrome capabilities. The goal is to give coding agents reliable workflows for browser automation, DevTools, and Chrome platform APIs.

This repo contains **skills and documentation** — not a Chrome extension, browser app, or MCP server implementation.

## Repository map

| Path | Purpose |
|------|---------|
| `skills/<skill-name>/SKILL.md` | Canonical, committed, publishable skills — **only** edit skills here |
| `skills-lock.json` | Locked references to vendored tooling skills (e.g. `skill-creator`); do not hand-edit hashes |
| `.agents/skills/` | Local Cursor/runtime copies — gitignored, not source of truth |
| `.claude/skills/` | Local Claude Code copies — gitignored, not source of truth |
| `README.md` | Human-facing overview; link here instead of duplicating marketing copy |

When adding or changing a skill, work in `skills/`. Never treat `.agents/skills/` or `.claude/skills/` as the canonical location.

## Skill authoring conventions

Each skill lives at `skills/<skill-name>/SKILL.md` with required YAML frontmatter:

```markdown
---
name: skill-name
description: Third-person WHAT + WHEN triggers (max ~1024 chars)
---

# Skill Title

## Instructions
...
```

Rules:

- **`name`** — lowercase letters, numbers, hyphens only; max 64 characters
- **`description`** — third person; include both capabilities and trigger terms (agents under-trigger skills without explicit WHEN clauses)
- **`disable-model-invocation: true`** — default unless ambient auto-trigger is intentional
- Keep `SKILL.md` lean; put depth in `references/`, `examples.md`, or `scripts/`
- No secrets, API keys, or credentials in skill files

Optional bundled resources:

```text
skills/<skill-name>/
├── SKILL.md
├── references/       # Detailed docs, API notes
├── examples.md       # Usage examples
└── scripts/          # Validation or helper scripts
```

## Chrome capability domains

Skills in this repo fall into one or more of these domains. Stay within scope; verify APIs against current docs.

### CDP / browser automation

Navigation, element interaction, form filling, screenshots, data extraction. Prefer stable CLI or MCP patterns (e.g. agent-browser, CDP clients) over ad-hoc shell one-liners. List Chrome/Chromium and CLI prerequisites upfront.

### Chrome DevTools MCP

Performance audits (Core Web Vitals), network debugging, accessibility checks, trace analysis. Document required MCP server setup and which tools the agent should call. Do not assume DevTools MCP is enabled by default.

### Extension / Platform APIs

Distill official Chrome documentation into agent workflows. Put Chrome doc URLs in `references/`, not in the `SKILL.md` body. Do not invent APIs — verify against [Chrome for Developers](https://developer.chrome.com/) or Context7 before writing.

## Creating or editing skills

1. Read the bundled `skill-creator` skill when authoring from scratch: `.agents/skills/skill-creator/SKILL.md` (local copy from `skills-lock.json`)
2. Draft `SKILL.md` with frontmatter and step-by-step instructions
3. Test with representative prompts; iterate the `description` for better triggering
4. Validate frontmatter:

```bash
python .agents/skills/skill-creator/scripts/quick_validate.py skills/<skill-name>
```

5. Commit only under `skills/` — not under `.agents/skills/` or `.claude/skills/`

## Code change principles

- Smallest correct diff; no unrelated refactors
- Match structure and tone of existing skills as the catalog grows
- Comments only for non-obvious Chrome, CDP, or MCP behavior
- No build tooling, `package.json`, or CI unless explicitly requested

## Verification before claiming done

- [ ] `SKILL.md` has valid `name` and `description` frontmatter
- [ ] Workflow steps are executable (commands are copy-pasteable)
- [ ] Prerequisites listed (Chrome/Chromium, MCP servers, CLI tools, extensions)
- [ ] No invented APIs — verified against official or Context7 docs
- [ ] Changes are under `skills/`, not gitignored runtime directories

## What not to do

- Do not commit `.agents/skills/` or `.claude/skills/` as canonical skills
- Do not duplicate README content in AGENTS.md — keep this file operational
- Do not hand-edit hashes in `skills-lock.json`
- Do not add tests, CI, or package scaffolding unless explicitly requested
