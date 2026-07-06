# tpm-tools

Reusable **Technical Product Manager** agent + skills for AI coding runtimes. Today ships opencode support; designed to grow into Claude Code, Cursor, and others.

## What's inside

| Path | Type | Runtime | What it does |
|------|------|---------|--------------|
| `skills/tpm-artifacts/SKILL.md` | Skill | opencode | Templates & scaffolds for PM deliverables: PRD, one-pager, RICE, RFC, sliced epic, experiment design, roadmap entry. |
| `agents/tpm.md` | Agent | opencode | Primary agent. Translates ambiguity into crisp requirements, prioritizes rigorously (RICE), orchestrates engineering work without writing code itself. |
| `.well-known/skills.json` | Manifest | opencode | Discoverable skill listing consumed by `skills.urls`. |

## Install (opencode)

### 1. Add the skill via `skills.urls`

Edit (or create) `~/.config/opencode/opencode.json`:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "skills": {
    "urls": [
      "https://raw.githubusercontent.com/DIAL-Studio/tpm-tools/main/.well-known/skills.json"
    ]
  }
}
```

opencode will fetch the manifest and register `tpm-artifacts` as an available skill that any agent can load on demand via the `skill` tool.

### 2. Install the TPM agent

Agents in opencode are file-based (no remote URL channel exists in the schema yet), so download the markdown file directly:

```bash
mkdir -p ~/.config/opencode/agents
curl -fsSL https://raw.githubusercontent.com/DIAL-Studio/tpm-tools/main/agents/tpm.md \
  -o ~/.config/opencode/agents/tpm.md
```

### 3. Restart opencode

opencode reads its config once at startup. Quit and reopen the session so the skill URL and the agent file are picked up.

### 4. Verify

- Press **Tab** → `tpm` should appear as a selectable primary agent.
- In `tpm` mode, ask it to write a PRD / RFC / RICE ranking — it will load the `tpm-artifacts` skill automatically.

## What the agent does

The `tpm` agent owns the bridge between business intent and engineering execution:

- Starts from the **problem**, not the solution — inverts solutions into underlying user pains.
- Makes ambiguity **explicit**: numbered assumptions, open-question lists.
- Uses **RICE** (Reach × Impact × Confidence × Effort) before recommending priority.
- One decision per artifact — a PRD owns a single decision, a one-pager testes a single bet.
- Slices work into **smallest-shippable** increments, each with Given/When/Then acceptance and rollback triggers.
- Every recommendation lists **2–3 options** plus rejected alternatives.
- Estimates are **ranges** (optimistic / likely / pessimistic) with confidence %.
- Every feature ships with a **leading metric**, a **guardrail metric**, and entrance/exit thresholds.

## Skill templates

`tpm-artifacts` ships seven templates:

- **A — PRD** (single decision for a new feature)
- **B — One-pager** (small scoped bet before investing in a full PRD)
- **C — RICE prioritization** (ranking candidates)
- **D — RFC / Design review** (technical sign-off)
- **E — Epic with sliced tickets** (PRD/RFC → executable work)
- **F — Experiment design** (A/B / holdout with power, MDE, guardrails)
- **G — Roadmap entry** (Now / Next / Later + Recently shipped)

Every template ends with **"Decisions still needed"** and **"Next concrete step"** sections.

## Permissions posture

`tpm.md` is read-only by design:

- `edit: ask` — must confirm any file write
- `bash: ask` for everything except read-only git/gh/rg/ls
- `task: allow` — delegates to `@explore` and `@general` subagents
- `skill: tpm-artifacts` and `skill: graphify` allowed

## Roadmap

- [x] opencode agent + skill
- [ ] Claude Code adapter (`SKILL.claude.md`)
- [ ] Cursor adapter
- [ ] More skills under `skills/` (metrics-kit, stakeholder-brief)

## Contributing

PRs welcome. Keep `SKILL.md` frontmatter fields (`name`, `description`, `license`, `compatibility`, `metadata`) — opencode filters out skills without `name` + `description`. Skill names must be lowercase hyphen-separated and match the folder name.

## License

MIT — see [LICENSE](./LICENSE).