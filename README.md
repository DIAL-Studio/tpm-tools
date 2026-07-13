# pm-agent-harness-kit

> **PM-AHK — Agent Harness Kit for Product Managers.**  
> 7 specialized PM agents in a pipeline + 59 skills. Modeled on [agent-harness-kit](https://github.com/enmanuelmag/agent-harness-kit).  
> Ships opencode support today; Claude Code integration in progress (beta tester available).

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-59-informational?style=flat-square)](catalog/comparison-analysis.md)
[![Agents](https://img.shields.io/badge/agents-7-informational?style=flat-square)](agents/README.md)

## What's inside

| Path | Type | Runtime | What it does |
|------|------|---------|--------------|
| `agents/*.md` | Agents (7) | opencode | Specialized PM agents in a harness pipeline — Lead, Explorer, Strategist, Builder, Reviewer + Coach, Smith. See [agents/README.md](agents/README.md). |
| `skills/*/SKILL.md` | Skills (59) | opencode+ | Full PM skill library — PRDs, user stories, strategy, RICE, experiments, metrics, stakeholder, AI agents, career, and more |
| `.well-known/skills.json` | Manifest | opencode | Discoverable skill listing for `skills.urls`. |

### The PM-AHK Pipeline

```
pm-lead → pm-explorer → pm-strategist (conditional) → pm-builder → pm-reviewer
    ↑           ↑               ↑                        ↑             ↑
 Orchestrator  Discovery    Strategy advisor         Spec creation   Validation
```

Start with `pm-lead` for any PM task. It classifies your request and either answers directly (lightweight queries) or routes you through the specialist pipeline. Full documentation: [docs/PM-AHK.md](docs/PM-AHK.md).

## Full Skill Library (59 skills)

### Artifacts & Docs (13)
| Skill | Description |
|-------|-------------|
| `tpm-artifacts` | Quick templates: PRD, one-pager, RICE, RFC, epic, experiment, roadmap |
| `prd-development` | 8-phase structured PRD (2-4 days) |
| `user-story` | Mike Cohn + Gherkin acceptance criteria |
| `user-story-mapping` | Activities → steps → tasks → release slices |
| `user-story-mapping-workshop` | Facilitated story mapping |
| `user-story-splitting` | 8 split patterns for large stories |
| `epic-hypothesis` | Frame epic as testable hypothesis |
| `epic-breakdown-advisor` | Richard Lawrence's 9 patterns |
| `press-release` | Amazon Working Backwards PR/FAQ |
| `eol-message` | End-of-life announcement |
| `proto-persona` | Assumption-based persona |
| `customer-journey-map` | End-to-end journey map |
| `customer-journey-mapping-workshop` | Facilitated journey mapping |

### Strategy & Discovery (12)
| Skill | Description |
|-------|-------------|
| `product-strategy-session` | Full strategy arc workflow (2-4 weeks) |
| `strategy-canvas` | **New** — 9-section single-artifact strategy canvas (vision → defensibility) |
| `discovery-process` | Complete discovery cycle (3-4 weeks) |
| `discovery-interview-prep` | Mom Test-style interview planning |
| `opportunity-solution-tree` | Teresa Torres OST |
| `problem-framing-canvas` | MITRE problem framing |
| `problem-statement` | User-centered problem statement |
| `positioning-statement` | Geoffrey Moore positioning |
| `positioning-workshop` | Facilitated positioning workshop |
| `jobs-to-be-done` | JTBD format |
| `pestel-analysis` | PESTEL framework |
| `company-intel` | 7-lens company/competitor research |
| `company-research` | Company profile brief |

### Prioritization & Roadmapping (3)
| Skill | Description |
|-------|-------------|
| `prioritization-advisor` | Framework selection (RICE/ICE/Kano) |
| `roadmap-planning` | Inputs → epics → prioritize → sequence |
| `feature-investment-advisor` | Build/don't build ROI |

### Metrics & Finance (8)
| Skill | Description |
|-------|-------------|
| `business-health-diagnostic` | SaaS health diagnostic |
| `saas-revenue-growth-metrics` | MRR, ARR, churn, NRR |
| `saas-economics-efficiency-metrics` | CAC, LTV, payback, Rule of 40 |
| `finance-metrics-quickref` | Formulas & benchmarks |
| `finance-based-pricing-advisor` | Pricing change impact |
| `acquisition-channel-advisor` | Channel evaluation |
| `tam-sam-som-calculator` | Market sizing |

### Stakeholder & Alignment (3)
| Skill | Description |
|-------|-------------|
| `stakeholder-identification` | Brainstorm + equity lens |
| `stakeholder-mapping` | Power×Interest + Impact×Power grids |
| `stakeholder-engagement-advisor` | Per-stakeholder engagement planning |

### AI & Agent Orchestration (5)
| Skill | Description |
|-------|-------------|
| `ai-shaped-readiness-advisor` | AI-first vs AI-shaped maturity |
| `context-engineering-advisor` | Context stuffing vs engineering |
| `agent-orchestration-advisor` | Multi-agent workflow design |
| `recommendation-canvas` | AI product idea evaluation |
| `derisk-measurement-advisor` | DUFV + PESTEL de-risking |

### Validation & Experimentation (4)
| Skill | Description |
|-------|-------------|
| `experiment-designer` | **New** — A/B test with power analysis, sample size calculation |
| `pol-probe-advisor` | Choose proof-of-life probe type |
| `pol-probe` | Lightweight validation experiment |
| `derisk-measurement-advisor` | Shared w/ AI section |

### Growth (3)
| Skill | Description |
|-------|-------------|
| `growth-plg-advisor` | **New** — PLG readiness, activation, viral loops, freemium conversion |
| `organic-growth-advisor` | McKinsey Growth Pyramid |
| `acquisition-channel-advisor` | Shared w/ Metrics |

### Workshops & Facilitation (4)
| Skill | Description |
|-------|-------------|
| `workshop-facilitation` | Generic facilitation protocol |
| `lean-ux-canvas` | Lean UX Canvas v2 |
| `storyboard` | 6-frame storyboard |
| Various shared workshop skills (positioning, OST, journey mapping, story mapping) |

### Career & Leadership (5)
| Skill | Description |
|-------|-------------|
| `altitude-horizon-framework` | PM-to-Director mental model |
| `director-readiness-advisor` | PM→Director transition coaching |
| `vp-cpo-readiness-advisor` | Director→VP/CPO coaching |
| `executive-onboarding-playbook` | 30-60-90 day playbook |
| `product-sense-interview-answer` | PM interview answer structure |

### Meta / Authoring (2)
| Skill | Description |
|-------|-------------|
| `skill-authoring-workflow` | Create repo-compliant skills |
| `pm-skill-creator` | Design skills via conversation |

### Agent Pipeline
| Agent | Role | Skills | Docs |
|-------|------|--------|------|
| `pm-lead` | Orchestrator + lightweight queries | 8 | [agents/pm-lead.md](agents/pm-lead.md) |
| `pm-explorer` | Discovery & research | 15 | [agents/pm-explorer.md](agents/pm-explorer.md) |
| `pm-strategist` | Strategy advisory (conditional) | 10 | [agents/pm-strategist.md](agents/pm-strategist.md) |
| `pm-builder` | Spec & artifact creation | 12 | [agents/pm-builder.md](agents/pm-builder.md) |
| `pm-reviewer` | Quality validation (approve/block) | 13 | [agents/pm-reviewer.md](agents/pm-reviewer.md) |
| `pm-coach` | Career transitions (auxiliary) | 5 | [agents/pm-coach.md](agents/pm-coach.md) |
| `pm-smith` | Skill authoring (auxiliary) | 2 | [agents/pm-smith.md](agents/pm-smith.md) |

See [agents/README.md](agents/README.md) for full pipeline documentation, agent boundaries, and the FAQ.

## Supported runtimes

| Runtime | Status | Config root | Notes |
|---------|--------|-------------|-------|
| `opencode` | ✅ supported | `~/.config/opencode` | Default. Agents + skills auto-discovered. |
| `claude-code` | ✅ supported | `~/.claude` | Phase 1 complete. See [docs/INSTALL-CLAUDE-CODE.md](docs/INSTALL-CLAUDE-CODE.md). |
| `copilot` | 🟡 planned | `~/.github/copilot` | Phase 2. Prompt format under validation. |
| `codex` | 🟡 planned | `~/.codex` | Phase 3. TOML agent format. |
| `cursor` | 🟡 planned | `~/.cursor` | Spec TBD. |

Track progress: [docs/ROADMAP.md](docs/ROADMAP.md)

## Install

### Interactive (default — recommended for new users)

Run without flags. The installer detects your environment and prompts for runtime and path:

```bash
curl -fsSL https://raw.githubusercontent.com/DIAL-Studio/pm-agent-harness-kit/main/install.sh | bash
```

**After install:** Restart your AI runtime and open `pm-lead` to start.

### Project-local install (single project only)

Installs to `.opencode/` in the current directory instead of globally. Agents and skills only affect this project.

```bash
curl -fsSL https://raw.githubusercontent.com/DIAL-Studio/pm-agent-harness-kit/main/install.sh | TPM_TOOLS_SCOPE=project bash
```

The TUI prompts for scope before path. Silence mode: `TPM_TOOLS_SCOPE=project TPM_TOOLS_RUNTIME=opencode`. Add `.opencode/` to your `.gitignore`.

### Silent (for scripts or when you know your runtime)

**opencode:**

```bash
curl -fsSL https://raw.githubusercontent.com/DIAL-Studio/pm-agent-harness-kit/main/install.sh | TPM_TOOLS_RUNTIME=opencode bash
```

**Claude Code:**

```bash
curl -fsSL https://raw.githubusercontent.com/DIAL-Studio/pm-agent-harness-kit/main/install.sh | TPM_TOOLS_RUNTIME=claude-code bash
```

**Pin a specific release:**

```bash
curl -fsSL https://raw.githubusercontent.com/DIAL-Studio/pm-agent-harness-kit/main/install.sh | TPM_TOOLS_BRANCH=v1.3.0 TPM_TOOLS_RUNTIME=opencode bash
```

**List available runtimes:**

```bash
curl -fsSL https://raw.githubusercontent.com/DIAL-Studio/pm-agent-harness-kit/main/install.sh | bash -s -- --list-runtimes
```

### Uninstall

```bash
curl -fsSL https://raw.githubusercontent.com/DIAL-Studio/pm-agent-harness-kit/main/uninstall.sh | bash
```

### Update notifications

Three ways you'll know when a new version is available:

**1. Automatic — `pm-lead` tells you (recommended)**

When you start a session with `pm-lead`, it reads a local flag file (`pm-ahk.update-available`). If an update is available, `pm-lead` mentions it in its first response with the update command. The flag file is updated daily by a background check script (installed automatically with the agents). No network calls from pm-lead, no delays.

**2. Manual check**

```bash
curl -fsSL https://raw.githubusercontent.com/DIAL-Studio/pm-agent-harness-kit/main/scripts/check-update.sh | bash
```

For scripts and CI, use `--json`:

```bash
curl -fsSL https://raw.githubusercontent.com/DIAL-Studio/pm-agent-harness-kit/main/scripts/check-update.sh | bash -s -- --json
```

**3. GitHub — watch the repo**

Star or watch [github.com/DIAL-Studio/pm-agent-harness-kit](https://github.com/DIAL-Studio/pm-agent-harness-kit) to receive release notifications.

### Update to latest

```bash
curl -fsSL https://raw.githubusercontent.com/DIAL-Studio/pm-agent-harness-kit/main/update.sh | bash
```

The installer backs up existing files before overwriting. After updating, restart your AI runtime for changes to take effect.

### Windows

Windows native shells (PowerShell, Git Bash, Cygwin) are **not supported**. Use WSL (Windows Subsystem for Linux) — the installer works there natively. Run the `curl | bash` command from your WSL terminal.

### Remote discovery (optional, for advanced users)

If you prefer to keep skills remote rather than vendored locally:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "skills": {
    "urls": [
      "https://raw.githubusercontent.com/DIAL-Studio/pm-agent-harness-kit/main/.well-known/skills.json"
    ]
  }
}
```

Then install the agents locally (opencode has no remote-agent channel):

```bash
for agent in pm-lead pm-explorer pm-strategist pm-builder pm-reviewer pm-coach pm-smith; do
  curl -fsSL "https://raw.githubusercontent.com/DIAL-Studio/pm-agent-harness-kit/main/agents/${agent}.md" \
    -o "${HOME}/.config/opencode/agents/${agent}.md"
done
```

### Verify

- Press **Tab** → `pm-lead` appears as a selectable primary agent.
- Ask it anything — it classifies your request and either answers directly or routes to specialist agents.
- Try: "Write a PRD for checkout v2" — `pm-lead` routes to `pm-explorer` → `pm-builder` → `pm-reviewer`.

## How the pipeline works

The 7-agent harness follows a fixed pipeline, modeled on [agent-harness-kit](https://github.com/enmanuelmag/agent-harness-kit):

| Stage | Agent | What happens |
|-------|-------|-------------|
| 1 | `pm-lead` | Classifies the request. Lightweight query → answers directly. Product initiative → writes decomposition plan and routes. |
| 2 | `pm-explorer` | Researches users, markets, problems. Produces evidence summary with confidence levels. Does NOT propose solutions. |
| 3 | `pm-strategist` | (Conditional) Advises on positioning, sizing, tradeoffs. Invoked only for strategic initiatives — skipped for routine features. |
| 4 | `pm-builder` | Writes PRDs, user stories, acceptance criteria. Only agent that produces engineering-ready specs. Does NOT write code. |
| 5 | `pm-reviewer` | Validates evidence quality, metric readiness, experiment design. Only agent that can approve or block a deliverable. |

Two auxiliary agents sit outside the pipeline: `pm-coach` (career transitions, interview prep) and `pm-smith` (skill authoring for maintainers).

## Permissions model

Each agent has scoped permissions matching its pipeline role:

| Agent | Edit | Writes specs? | Approves? |
|-------|------|--------------|-----------|
| `pm-lead` | ask | No | Routes |
| `pm-explorer` | ask | No (evidence only) | No |
| `pm-strategist` | ask | No (advisory only) | No |
| `pm-builder` | allow | Yes (specs only) | No |
| `pm-reviewer` | ask | No (reviews only) | Yes (approve/block) |
| `pm-coach` | ask | No | No |
| `pm-smith` | allow | No (skill files only) | No |

Boundaries are enforced by persona instructions, not just technical permissions. Even if `pm-explorer` *could* write a spec, it won't — its operating principles forbid proposing solutions.

## Skill origins

This library is a curated consolidation of battle-tested PM frameworks:

| Source | Contribution | License |
|--------|-------------|---------|
| [`deanpeters/Product-Manager-Skills`](https://github.com/deanpeters/Product-Manager-Skills) | 55 core skills (all categories) | CC BY-NC-SA 4.0 |
| [`alirezarezvani/claude-skills`](https://www.skills.sh/alirezarezvani/claude-skills/product-skills) | Inspiration for `experiment-designer` | Reference |
| [`phuryn/pm-skills`](https://www.skills.sh/phuryn/pm-skills/product-strategy) | Inspiration for `strategy-canvas` | Reference |
| [`digidai/product-manager-skills`](https://www.skills.sh/digidai/product-manager-skills/product-manager-skills) | Inspiration for `growth-plg-advisor`, coaching patterns | Reference |
| DIAL-Studio original | PM-AHK agent architecture (7 agents), `tpm-artifacts`, install/uninstall scripts, transformation tooling | MIT |

See [`catalog/comparison-analysis.md`](catalog/comparison-analysis.md) for the full gap analysis.

## Roadmap

See [docs/ROADMAP.md](docs/ROADMAP.md) for the full PM-AHK development plan, including:

- **Phase 1 (current)**: Claude Code integration (beta tester available), validation, docs
- **Phase 2**: GitHub Copilot integration
- **Phase 3**: Codex (OpenAI) integration
- **Phase 4**: Commands ↔ agents integration
- **Phase 5**: Full harness infrastructure (backlog, audit trail, quality gate, dashboard)
- **Phase 6+**: AHK interop guide, ecosystem expansion

## Contributing

PRs welcome. Skill format:

- Frontmatter: `name`, `description`, `compatibility`, `metadata` (opencode); `argument-hint` (Claude)
- Body: Purpose, Input, Key Concepts, Application, Examples, Common Pitfalls, References
- Name is lowercase kebab-case, matches folder name
- No `$ARGUMENTS` — use plain-language `## Input` section instead

## License

`pm-agent-harness-kit` original content: MIT.  
Content adapted from `deanpeters/Product-Manager-Skills`: CC BY-NC-SA 4.0.  
See [`catalog/comparison-analysis.md`](catalog/comparison-analysis.md) for full attribution.
