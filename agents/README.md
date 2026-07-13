# TPM Agent Directory

This directory contains the specialized PM agent definitions for the pm-agent-harness-kit harness. Each agent has a focused domain, a consistent persona, and a defined role in the product development pipeline.

## Quick Reference: Which Agent When?

| User says... | Agent | Mode |
|-------------|-------|------|
| "What's our churn rate?" | `pm-lead` | Lightweight advisory |
| "Should I prioritize X or Y?" | `pm-lead` | Lightweight advisory |
| "Research our churn problem" | `pm-lead` → `pm-explorer` | Pipeline (research only) |
| "Run full discovery on checkout abandonment" | `pm-lead` → `pm-explorer` | Pipeline stage 1 |
| "Build the strategy for entering Europe" | `pm-lead` → `pm-explorer` → `pm-strategist` | Full pipeline (strategic) |
| "Write the PRD for payment v2" | `pm-lead` → `pm-explorer` → `pm-builder` | Pipeline (non-strategic) |
| "Review this spec before I send it to engineering" | `pm-lead` → `pm-reviewer` | Pipeline (review only) |
| "Am I ready for a Director role?" | `pm-coach` | Standalone |
| "Create a new skill for accessibility audits" | `pm-smith` | Standalone (maintainer) |

---

## Pipeline Architecture

The PM harness follows a 5-stage pipeline, modeled on AHK's agent roles but specialized for product management:

```
                    PM HARNESS PIPELINE
                    
  ┌──────────┐
  │ pm-lead  │  Decomposes product initiatives.
  │          │  Routes to specialist agents.
  │          │  Handles lightweight queries directly.
  └────┬─────┘
       │
       ▼
  ┌──────────┐
  │pm-explorer│  Researches users, markets, problems.
  │          │  Produces structured evidence.
  │          │  NEVER proposes solutions. Read-only.
  └────┬─────┘
       │
       ▼ (conditional — strategic initiatives only)
  ┌──────────┐
  │pm-strate-│  Advises on positioning, sizing, moats.
  │  gist    │  Consumes Explorer's evidence.
  │          │  Output feeds Builder's constraints.
  └────┬─────┘
       │
       ▼
  ┌──────────┐
  │pm-builder│  Builds specifications: PRDs, stories, ACs.
  │          │  Only agent that produces specs.
  │          │  Does NOT write code.
  └────┬─────┘
       │
       ▼
  ┌──────────┐
  │pm-reviewer│ Validates evidence quality, metrics, rigor.
  │          │  Only agent that can approve or block.
  │          │  Does NOT rewrite — identifies flaws.
  └──────────┘
```

### Pipeline Agents

| Agent | Role | AHK Parallel | Mode | Tab | @ mention | Delegation | Skills |
|-------|------|-------------|------|-----|-----------|------------|--------|
| `pm-lead` | Orchestrator | `lead` | `primary` | ✅ | - | - | 8 |
| `pm-explorer` | Discovery | `explorer` | `all` | ✅ | ✅ | ✅ | 15 |
| `pm-strategist` | Strategy advisory | `consultant` | `subagent` | ❌ | ✅ | ✅ | 10 |
| `pm-builder` | Spec creation | `builder` | `all` | ✅ | ✅ | ✅ | 12 |
| `pm-reviewer` | Quality validation | `reviewer` | `subagent` | ❌ | ✅ | ✅ | 13 |

`pm-strategist` and `pm-reviewer` are **subagent-only** — they're invoked by `pm-lead` via the Task tool or manually with `@pm-reviewer`. They don't appear in the Tab bar because they're rarely used standalone and the pipeline enforces correct ordering.

### Auxiliary Agents (outside the pipeline)

| Agent | Role | Mode | Tab | Skills | When to use |
|-------|------|------|-----|--------|-------------|
| `pm-coach` | Career coach | `all` | ✅ | 5 | Career transitions, interview prep, leadership readiness |
| `pm-smith` | Skill authoring | `subagent` | ❌ | 2 | Creating/maintaining PM skills (maintainer tool — invoke with @pm-smith) |

---

## Agent Boundaries

Each agent has hard boundaries. Crossing them produces bad output and confuses the pipeline.

### pm-lead boundaries

- **DO**: Classify requests, decompose initiatives, route to specialists, answer lightweight queries
- **DON'T**: Write PRDs, conduct research, validate specs, make strategic recommendations
- **Handoff rule**: If the request requires structured PM work → route. If it's a question → answer directly.

### pm-explorer boundaries

- **DO**: Research users, markets, competitors. Produce evidence. Surface assumptions. Label confidence.
- **DON'T**: Propose solutions. Write any specification. Recommend what to build.
- **Handoff rule**: Output = problem statement + evidence summary. Hand off to Strategist or Builder.

### pm-strategist boundaries

- **DO**: Advise on positioning, sizing, tradeoffs, moats. Challenge assumptions.
- **DON'T**: Write specs. Do discovery research. Make final build decisions.
- **Handoff rule**: Output = advisory document with tradeoffs and assumptions. Hand off to Builder.

### pm-builder boundaries

- **DO**: Write PRDs, user stories, acceptance criteria, story maps. Define metrics and rollback triggers.
- **DON'T**: Do discovery. Set strategy. Write code. Validate own work.
- **Handoff rule**: Output = engineering-ready specification. Hand off to Reviewer.

### pm-reviewer boundaries

- **DO**: Validate evidence quality, metric readiness, experiment design. Approve or block with specific reasons.
- **DON'T**: Rewrite deliverables. Do discovery. Write specs. Make strategic recommendations.
- **Handoff rule**: Approved → back to Lead for synthesis. Blocked → back to originating agent with fix instructions.

---

## Relationship to the Skills Library

Agents are **thin wrappers** around the 59+ skills in this repo. Agents provide:

- **Persistent persona** — consistent behavioral bias across interactions
- **Domain-specific operating principles** — rules that would bloat a generalist agent
- **Boundary enforcement** — what this agent will and won't do
- **Pipeline role** — where this agent fits in the product development sequence

Skills provide the actual domain knowledge, workflows, and templates. An agent loads skills when it needs to produce structured output. If a skill doesn't exist for a task, the agent tells the user — it doesn't invent one.

### Which skills does each agent own?

See each agent's `## Skill Library` section for the full mapping. Most skills are assigned to a single agent. A small number of skills are **dual-assigned** where the same skill serves a different role in a different pipeline stage (e.g., `pestel-analysis` is used by Explorer for market research AND by Strategist for external force analysis). The agent's persona determines how the skill is applied, not the skill itself.

| Agent | Skill count |
|-------|-------------|
| `pm-lead` | 8 |
| `pm-explorer` | 15 |
| `pm-strategist` | 10 |
| `pm-builder` | 12 |
| `pm-reviewer` | 13 |
| `pm-coach` | 5 |
| `pm-smith` | 2 |

---

## Coexistence with AHK (Agent Harness Kit)

If your project also uses the [agent-harness-kit](https://github.com/enmanuelmag/agent-harness-kit) for software development, both harnesses can coexist. The `pm-` prefix prevents name collisions:

| AHK Agent | PM Harness Agent | Collision? |
|-----------|-----------------|------------|
| `lead` | `pm-lead` | No — prefix differentiates |
| `explorer` | `pm-explorer` | No |
| `consultant` | `pm-strategist` | No |
| `builder` | `pm-builder` | No — prefix + description clarifies `pm-builder` builds specs, not code |
| `reviewer` | `pm-reviewer` | No |

AHK's `lead` orchestrates code development. `pm-lead` orchestrates product development. They share the same pipeline pattern but operate on different artifacts.

---

## Migration from `tpm.md`

The original `agents/tpm.md` was a monolithic generalist agent (218 lines, 59 skills). It has been decomposed into this 7-agent system and **archived** as `tpm.md.archived`. Use `pm-lead` as the primary entry point for all new work.

---

## FAQ

### What's the difference between `pm-builder` and `pm-smith`?

They build different things for different audiences:

| | `pm-builder` | `pm-smith` |
|---|---|---|
| **Builds** | Product artifacts: PRDs, user stories, specs, story maps | Library artifacts: skill files (SKILL.md, template.md, examples) |
| **Audience** | PMs doing product work | Maintainers extending the pm-agent-harness-kit library |
| **Output is for** | Engineering teams, stakeholders | The pm-agent-harness-kit repo itself |
| **Analogy** | A carpenter building furniture | A toolmaker forging the carpenter's tools |
| **Pipeline role** | Stage 4 — produces the deliverable | Standalone — not in the pipeline |

Think of it this way: `pm-builder` builds the PRD for your checkout redesign. `pm-smith` builds the skill file that teaches other PMs how to build PRDs.

### Why are some skills assigned to multiple agents?

Skills like `pestel-analysis`, `tam-sam-som-calculator`, `prioritization-advisor`, and `pol-probe-advisor` serve different purposes in different pipeline stages. An Explorer uses PESTEL to research market conditions; a Strategist uses the same skill to assess strategic risks. The skill is the same; the context and question it answers are different.

---

## Contributing

To add a new agent or modify an existing one:

1. Follow the existing format: YAML frontmatter + markdown body
2. Assign skills from the library — do not create overlapping ownership
3. Update this README with the agent's role and skill count
4. Run validation: `./scripts/test-a-skill.sh --agent <name>`

For creating new skills, use `pm-smith`.

See [docs/ROADMAP.md](../docs/ROADMAP.md) for future development phases including cross-compatibility with GitHub Copilot, Claude Code, and Codex.
