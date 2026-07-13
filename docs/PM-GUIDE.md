# Product Management with AI Agents: A Step-by-Step Guide

> **Who this is for:**
> - **New PMs** — follow the stages in order. Each stage tells you what to say and why.
> - **Experienced PMs** — jump to any section. Every skill has a one-liner cheat code.
> - **Curious makers** — no PM experience? Start at Discover. You'll learn PM by doing it.

---

## The 60-second start

Open your AI tool, select `pm-lead`, and say:

> "Write a PRD for [feature]"

That's it. `pm-lead` classifies your request, invokes research agents, writes the spec, and validates it. You don't need to know which skill does what — the agents decide for you.

But if you want to **drive the agents yourself** or learn PM craft, this guide shows you every skill, when to use it, and what to say.

---

## The PM workflow lifecycle

Every product initiative follows 5 stages. Skills are grouped by stage:

```
Discover  →  Strategize  →  Specify  →  Validate  →  Communicate
  problem      position       PRD        metrics       stakeholders
  users        market         stories     experiments   alignment
  evidence     roadmap        ACs         probes        comms
```

**Pro tip:** Start with the compound commands — they chain multiple skills. Use individual skills when you need just one thing.

---

## Stage 1: Discover — Understand the problem

> *Don't build until you know who you're building for and what problem they have.*

### 🟢 Daily skills (every PM should know these)

**`/problem-statement`** — Define who is blocked, what they're trying to do, and why it matters.

```bash
# Inexperienced: let the agent ask questions (interactive mode)
/problem-statement

# Experienced: give context and get a draft
/problem-statement "Clinic schedulers double-book exam rooms because the calendar doesn't show equipment availability"
```

The agent uses this framework: *I am [user], trying to [goal], but [blocker], because [root cause], which makes me feel [emotion].* This is your north star — everything you build should trace back to this statement.

---

**`/proto-persona`** — Create a working hypothesis of your target user. **Now interactive** with 8 assumption rounds.

```bash
# Interactive mode (guided, one question at a time with progress bar)
/proto-persona

# Fast path: best guess mode — infer, label assumptions, you review
```
Say "3" for best guess and you get a complete persona tagged `[ASSUMED]`. Say "change assumption 4" to fix one thing.

---

### 🔵 Weekly skills (every initiative should start here)

**`/discovery-interview-prep`** — Plan Mom Test-style customer interviews. Don't ask "would you use this?" — ask about their last three attempts to solve the problem.

**`/jobs-to-be-done`** — Uncover what the user is *really* trying to accomplish. "I don't want a drill, I want a hole in the wall."

**`/opportunity-solution-tree`** — Teresa Torres method: start with an outcome, branch into opportunities, then solutions. Prevents solution-jumping.

---

### 🟡 Monthly/Quarterly (strategic discovery)

**`/discovery-process`** — Full discovery cycle (3-4 weeks). Use for new products or major pivots. Chains framing → interviews → synthesis → validation.

**`/company-intel`** — Research competitors with 7 analytical lenses. "What is Competitor X's pricing strategy?"

**`/customer-journey-map`** — Map every touchpoint from awareness to advocacy. **Now interactive** with 7 stages and progress bar.

---

### The new PM's discovery checklist

1. Write a `/problem-statement` — you can't solve what you can't articulate
2. Create a `/proto-persona` — who are you building for?
3. Run `/discovery-interview-prep` — plan 5 user interviews
4. Do the interviews (not an AI skill — talk to humans!)
5. Return with evidence and refine your problem statement

---

## Stage 2: Strategize — Decide what to build and why

> *Strategy is what you say no to. Everything else is just a list.*

### 🟡 Monthly/Quarterly (strategic cycles)

**`/strategy`** (compound command) — Full strategy arc: positioning → discovery → roadmap.

**`/positioning-statement`** — Geoffrey Moore format. **Now interactive** with 6 elements. "For [target customer] who [need], [product] is a [category] that [benefit]. Unlike [alternatives], we [differentiation]."

```bash
# Interactive: one positioning element at a time
/positioning-statement

# Fast: best guess → review → adjust
# Say "3" at entry, then "change assumption 2" to fix one element
```

**`/plan-roadmap`** (compound command) — Epics → prioritize → sequence → communicate. Use when you have multiple initiatives and need to decide order.

**`/prioritize`** (compound command) — RICE, ICE, or Kano. "Which of these 5 features should we build first?"

---

### Individual strategy skills

**`/tam-sam-som-calculator`** — Size your market with explicit assumptions. "What's the TAM for a SaaS project management tool for construction?"

**`/pestel-analysis`** — Political, Economic, Social, Technological, Environmental, Legal. Use before entering a new geography or regulated market.

**`/roadmap-planning`** — Inputs → epics → prioritize → sequence → communicate.

**`/prioritization-advisor`** — Choose RICE (Reach × Impact × Confidence ÷ Effort), ICE (Impact × Confidence × Ease), or Kano (delighters vs. basics).

**`/feature-investment-advisor`** — Build/don't build decision with ROI modeling.

**`/strategy-canvas`** — 9-section single-artifact strategy: vision, segments, value props, tradeoffs, metrics, growth, capabilities, defensibility.

---

### The experienced PM's strategy shortcut

> "Build the strategy for entering [market] with [product]"

Said to `pm-lead`, this invokes pm-explorer (research) → pm-strategist (positioning, sizing, tradeoffs) → pm-builder (roadmap). One sentence, full strategic analysis.

---

## Stage 3: Specify — Write the spec

> *If it's not written down, it doesn't exist. If there's no acceptance criteria, it's not done.*

### 🔵 Weekly skills

**`/write-prd`** (compound command) — Full PRD: problem → users → solution → success criteria.

```bash
# Let pm-lead run the pipeline
# It invokes pm-explorer (research) → pm-builder (spec) → pm-reviewer (validation)
# Just say:
"Write a PRD for checkout v2"
```

**`/user-story`** — Mike Cohn format + Gherkin acceptance criteria. Every story gets Given/When/Then.

```bash
/user-story "As a returning customer, I want to reorder my last purchase so that I don't have to search again"
```

**`/epic-hypothesis`** — Frame an epic as a testable hypothesis. **Now interactive** with 5 assumption rounds.

```bash
# Interactive: guided assumption clarification
/epic-hypothesis "Add JWT authentication"

# Fast: best guess → review
# Agent asks: target user, expected outcome, validation method, success threshold, timeline
```

**`/user-story-splitting`** — Break large stories into shippable slices. "This story is too big — split it by workflow."

---

### Individual spec skills

**`/prd-development`** — 8-phase structured PRD (2-4 days). Deeper than the compound `/write-prd`.

**`/user-story-mapping`** — Activities → steps → tasks → release slices. Visualize the entire user journey as stories.

**`/epic-breakdown-advisor`** — Richard Lawrence's 9 patterns for breaking down epics.

**`/tpm-artifacts`** — Quick templates: PRD, one-pager, RICE, RFC, epic, experiment, roadmap.

**`/storyboard`** — 6-frame visual narrative. **Now interactive** with progress bar. "Create a storyboard for the onboarding flow."

**`/lean-ux-canvas`** — Frame a business problem, surface assumptions, define learning goals.

---

### The new PM's spec checklist

1. Have a validated `/problem-statement` (from Discover)
2. Load `/prd-development` — follow the 8 phases
3. Use `/user-story` for each feature in the PRD
4. Use `/epic-breakdown-advisor` if any story is too large
5. Every story must have Given/When/Then acceptance criteria

---

## Stage 4: Validate — Design experiments and measure success

> *If you're not measuring it, you're guessing. If you can't roll it back, don't ship it.*

### 🟡 Monthly/Quarterly (experiment cycles)

**`/experiment-designer`** — A/B test with power analysis, sample size calculation. "Design an A/B test for our new checkout flow."

**`/pol-probe-advisor`** — Choose the right validation method before building. "Should I run a fake door test or a concierge test for this feature?"

**`/pol-probe`** — Lightweight validation experiment template. Cheapest way to test a hypothesis.

**`/derisk-measurement-advisor`** — Scan for internal (DUFV) and external (PESTEL) risks before launch.

---

### Metrics skills

**`/business-health-diagnostic`** — SaaS health across growth, retention, efficiency, capital. "How healthy is our business right now?"

**`/saas-revenue-growth-metrics`** — MRR, ARR, churn, NRR. "Calculate our net revenue retention for Q2."

**`/saas-economics-efficiency-metrics`** — CAC, LTV, payback, Rule of 40. "What's our LTV:CAC ratio?"

**`/finance-metrics-quickref`** — Formulas and benchmarks. "What's the industry benchmark for SaaS churn?"

**`/finance-based-pricing-advisor`** — Model pricing changes. "What happens to ARPU if we raise prices 15%?"

---

### The experienced PM's validation workflow

1. **Before building:** `/pol-probe-advisor` → choose the cheapest test
2. **During build:** metrics defined in every user story
3. **Before launch:** `/experiment-designer` → powered A/B test
4. **After launch:** `/business-health-diagnostic` → check metrics weekly

---

## Stage 5: Communicate — Align stakeholders

> *A good decision without buy-in is just an opinion. A mediocre decision with alignment ships.*

### 🟢 Daily

**`/stakeholder-identification`** — Who needs to know? "Map stakeholders for the checkout v2 launch."

**`/stakeholder-mapping`** — Power × Interest grid. Who has power? Who cares?

---

### 🔵 Weekly

**`/stakeholder-engagement-advisor`** — Per-stakeholder engagement plan. "How should I engage our CTO about the checkout redesign?"

---

### 🔴 Launch/comms artifacts

**`/press-release`** — Amazon Working Backwards PR/FAQ. Write the press release before writing the code.

**`/eol-message`** — End-of-life announcement. "Write the sunset notice for our legacy API v1."

**`/storyboard`** — 6-frame narrative for stakeholder buy-in. "Show the checkout v2 story from the user's perspective."

---

## Specialized skills

### Career & Growth

**`/altitude-horizon-framework`** — Understand what changes when you move from PM to Director.

**`/director-readiness-advisor`** — Assess your readiness for a Director role.

**`/product-sense-interview-answer`** — Structure answers to PM interview questions.

**`/executive-onboarding-playbook`** — 30-60-90 day plan for new VP/CPO roles.

---

### Growth & Channels

**`/growth-plg-advisor`** — Product-led growth: activation, virality, freemium conversion.

**`/organic-growth-advisor`** — McKinsey Growth Pyramid: diagnose where your growth constraint lives.

**`/acquisition-channel-advisor`** — Evaluate channels by unit economics.

---

### AI & Agent Orchestration

**`/ai-shaped-readiness-advisor`** — Is your product AI-first or AI-shaped? Assess maturity.

**`/context-engineering-advisor`** — Diagnose context stuffing vs. context engineering.

**`/agent-orchestration-advisor`** — Design multi-agent workflows.

**`/recommendation-canvas`** — Evaluate AI product ideas.

---

### Meta / Authoring (maintainers only)

**`/skill-authoring-workflow`** — Turn raw notes into a compliant PM skill.

**`/pm-skill-creator`** — Design a new skill via guided conversation.

---

## The agent pipeline: When to let the agents drive

If you don't want to think about which skill to use, just use the pipeline:

```
You → pm-lead → pm-explorer (research) → pm-builder (spec) → pm-reviewer (validate) → You
```

| What you say | What happens |
|-------------|-------------|
| "Write a PRD for X" | Full pipeline: research → spec → validation |
| "Research our churn problem" | Explorer only — evidence, no spec |
| "Build the strategy for entering Europe" | Full pipeline with strategist (positioning, sizing) |
| "Review this experiment design" | Reviewer only — validates and returns blockers |
| "Am I ready for a Director role?" | Coach — career assessment |

---

## Cheat sheets

### Daily PM (60 seconds to start your day)

1. Check `/prioritize` — what should I work on today?
2. If writing specs: `/user-story` or `/write-prd`
3. If blocked: `/problem-statement` to reframe

### Weekly PM (Monday morning ritual)

1. `/business-health-diagnostic` — how's the business?
2. `/stakeholder-identification` — who needs updates this week?
3. `/write-prd` — for any feature entering development

### Monthly PM (Planning week)

1. `/strategy` or `/positioning-statement` — are we still on track?
2. `/plan-roadmap` — what ships next?
3. `/experiment-designer` — for any A/B tests in flight

### Quarterly PM (Strategy offsite)

1. `/product-strategy-session` — full strategy arc
2. `/tam-sam-som-calculator` — is the market still the right size?
3. `/pestel-analysis` — has anything shifted externally?

---

## Interactive skills reference

These skills support entry modes (guided, context dump, best guess):

| Skill | Rounds | Entry modes |
|-------|--------|-------------|
| `proto-persona` | 8 | 1/2/3 |
| `positioning-statement` | 6 | 1/2/3 |
| `customer-journey-map` | 7 | 1/2/3 |
| `storyboard` | 6 | 1/2/3 |
| `epic-hypothesis` | 5 | 1/2/3 |
| All `*-workshop` skills | varies | 1/2/3 |
| All `*-advisor` skills | varies | 1/2/3 |

All use the `[■■■■□□□□]` progress bar and A/B/C/D/Other option pattern.

---

## Compound commands reference

| Command | Chains | Use when |
|---------|--------|----------|
| `/prioritize` | 5 skills | "What should we work on next?" |
| `/write-prd` | 5 skills | "Write the spec for [feature]" |
| `/discover` | 5 skills | "Research and validate [problem]" |
| `/strategy` | 5 skills | "Build strategy for [market/product]" |
| `/plan-roadmap` | 5 skills | "Sequence [initiatives] into a roadmap" |
| `/leadership-transition` | 4 skills | "Am I ready for [next role]?" |

---

## Learning path: from zero to agent-powered PM

**Week 1 — Learn the basics:**
1. Read the problem-statement framework (I am / Trying to / But / Because)
2. Use `/proto-persona` (best guess mode) to define your first user
3. Use `/user-story` to write your first story

**Week 2 — Get evidence:**
1. Use `/discovery-interview-prep` to plan 3 interviews
2. Do the interviews
3. Use `/problem-statement` with your new evidence

**Week 3 — Build a spec:**
1. Say "Write a PRD for [feature]" to pm-lead
2. Watch the pipeline: explorer → builder → reviewer
3. Review the output — the reviewer will flag gaps

**Week 4 — Think strategically:**
1. Use `/positioning-statement` to define your product's market position
2. Use `/prioritize` to rank your backlog
3. Use `/experiment-designer` for your first A/B test
