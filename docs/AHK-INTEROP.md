# AHK Interop Guide

> Running PM-AHK alongside [agent-harness-kit](https://github.com/enmanuelmag/agent-harness-kit) (AHK) in the same project.
>
> **The short version:** PM-AHK produces specs and decisions. AHK produces code. They complement each other. The `pm-` prefix prevents agent name collisions. Nothing breaks — they don't touch the same files.

---

## Why run both harnesses?

In a product team, PMs and engineers work on the same project but produce different artifacts:

| Artifact | Who owns it | Harness |
|----------|------------|---------|
| Problem statement, evidence, personas | PM | PM-AHK (pm-explorer) |
| PRDs, user stories, acceptance criteria | PM | PM-AHK (pm-builder) |
| Experiment design, metrics validation | PM | PM-AHK (pm-reviewer) |
| Architecture, implementation code | Engineer | AHK (explorer, builder) |
| Code review, tests | Engineer | AHK (reviewer) |

The two harnesses are **complementary pipeline stages**:

```
PM-AHK: pm-lead → pm-explorer → pm-builder → pm-reviewer
                                                        ↓  handoff
AHK:    lead → explorer → builder → reviewer
```

pm-builder produces a spec → AHK builder implements it. That's the interop point.

---

## What collides? Nothing.

### Agent names

PM-AHK uses the `pm-` prefix convention. AHK uses bare names (`lead`, `explorer`, etc.). They coexist in the same project without collision:

| Tab bar (opencode) | PM-AHK agents | AHK agents |
|-------------------|---------------|------------|
| Tab → pm-lead, pm-explorer, pm-builder, pm-coach | ✅ | — |
| Tab → lead, explorer, builder, reviewer | — | ✅ |
| @ mention → pm-reviewer, pm-strategist, pm-smith | ✅ | — |
| @ mention → consultant, general, scout | — | ✅ |

### File paths

| Harness | Config root | Agents |
|---------|------------|--------|
| PM-AHK | `~/.config/opencode/` (global) or `.opencode/` (project) | `agents/pm-*.md` |
| AHK | `.claude/agents/` or `.opencode/agents/` | `lead.md`, `explorer.md`, etc. |

They read from different directories. No file conflicts.

### MCP / state

| Harness | Database | CLI |
|---------|----------|-----|
| PM-AHK | `.harness/harness.db` | `pm-ahk serve/status` |
| AHK | `.harness/harness.db` | `ahk serve/status` |

They share the same `.harness/` directory if both are project-scoped. This is intentional — they're complementary backlogs. But the database schemas are different:

- PM-AHK: `initiatives`, `actions`, `criteria`
- AHK: `tasks`, `actions`, `sections`

They don't read each other's tables. They coexist in the same `.harness/` directory without conflict.

---

## The handoff: PM spec → engineering implementation

This is the core interop pattern. Here's the full flow:

### Step 1: PM-AHK produces a spec

```bash
# PM says:
"Write a PRD for authentication v2"

# pm-lead runs the pipeline:
#   pm-explorer → researches auth pain points (evidence)
#   pm-builder → writes PRD with stories, ACs, metrics
#   pm-reviewer → validates, returns blockers
```

### Step 2: Export as initiative in the shared backlog

The PM creates a shared initiative that both harnesses can reference:

```bash
# pm-ahk initiative add
# Title: Implement auth v2
# Description: PRD from pm-builder with 3 user stories, 2-week timeline
```

### Step 3: Engineer imports into AHK

The engineer picks up the initiative:

```bash
# AHK side:
ahk task add --title "Implement JWT auth v2" \
  --description "See initiative #1 in pm-ahk backlog. PRD in .harness/actions."
ahk task claim 1
```

AHK's lead then runs the engineering pipeline:

```
AHK lead → explorer (maps codebase) → builder (implements) → reviewer (code review)
```

### Step 4: Circle back

After engineering delivers, the PM marks the initiative as done:

```bash
pm-ahk initiative done 1
```

---

## Practical setup for a monorepo

### With opencode

1. Install PM-AHK globally:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/DIAL-Studio/pm-agent-harness-kit/main/install.sh | bash
   ```

2. Install AHK per-project:
   ```bash
   cd your-monorepo
   npx @cardor/agent-harness-kit init
   ```

3. Verify both harnesses in the Tab bar:
   ```
   Tab → pm-lead  (PM-AHK)
   Tab → lead     (AHK)
   ```

### With Claude Code

```bash
# Install PM-AHK for claude-code
curl .../install.sh | TPM_TOOLS_RUNTIME=claude-code bash

# AHK generates its own .claude/agents/ during ahk init
cd your-monorepo && npx ahk init
```

Claude Code discovers agents from `.claude/agents/` — both `pm-*.md` and `lead.md` coexist.

### With VS Code / GitHub Copilot

```bash
# PM-AHK (project-scoped)
curl .../install.sh | TPM_TOOLS_SCOPE=project bash

# Install AHK
npx @cardor/agent-harness-kit init
```

Both live in different config directories — no conflicts.

---

## CI/CD quality gate across harnesses

For teams that want to enforce the handoff in CI:

```yaml
# .github/workflows/pm-engineering-gate.yml
name: PM → Engineering Gate
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  check-handoff:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Check PM initiative has evidence
        run: |
          python3 ~/.config/opencode/pm-ahk.py initiative list --status discovery
          # If initiatives are in discovery without a "spec" status → warn
          
      - name: Check PR references a PM initiative
        run: |
          if ! echo "${{ github.event.pull_request.body }}" | grep -q "Initiative #"; then
            echo "⚠️ This PR doesn't reference a PM initiative. Link one: /pm-ahk initiative list"
          fi
```

---

## Anti-patterns to avoid

| Anti-pattern | Why it fails | Fix |
|-------------|-------------|-----|
| Installing both harnesses globally without project scope | Agent files from both harnesses mix in the same `~/.config/opencode/agents/` | Use `--scope project` for one of them, or rely on the `pm-` prefix to differentiate |
| Engineer picks up initiative without reading the spec | Builder codes without knowing acceptance criteria, resulting in rework | AHK's lead should include `handoff_read(initiative_id)` output in the builder's prompt |
| PM doesn't mark done after delivery | Backlog fills with completed-but-unmarked initiatives | Set a team convention: close the initiative in the same standup where the PR is merged |
| Two people claim the same initiative | Double work | Both harnesses use atomic claiming — the second caller gets `already_claimed` error |

---

## Reference: agent name map

| PM-AHK | AHK | Purpose |
|--------|-----|---------|
| `pm-lead` | `lead` | Orchestrator |
| `pm-explorer` | `explorer` | Research & mapping |
| `pm-strategist` | `consultant` | Conditional advisory |
| `pm-builder` | `builder` | Produces the deliverable |
| `pm-reviewer` | `reviewer` | Validates quality |
| `pm-coach` | — | Career coaching (PM-AHK only) |
| `pm-smith` | — | Skill authoring (PM-AHK only) |
| — | `scout` | External research (AHK only) |
| — | `general` | Multi-step tasks (AHK only) |

---

## Quick checklist

- [ ] PM-AHK installed (global or project)
- [ ] AHK installed (per-project)
- [ ] Both appear in the Tab bar / agent menu
- [ ] `pm-ahk initiative add` creates a backlog item
- [ ] Engineer references the initiative ID in their PR
- [ ] PM marks `initiative done` after delivery
- [ ] CI gate checks for initiative references (optional)
