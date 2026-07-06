---
name: tpm-artifacts
description: Templates and scaffolds for product management deliverables — PRDs, one-pagers, RFCs, RICE prioritization, roadmap entries, sliced epics with acceptance criteria, and experiment designs. Load when a structured TPM artifact is needed.
license: MIT
compatibility: opencode
metadata:
  audience: product-managers
  workflow: tpm
---

# tpm-artifacts

Reusable templates for Technical Product Manager deliverables. Load this skill when asked to produce a structured PM artifact. Pick the matching template, fill it in, and keep every section — empty sections stay with `TBD` rather than being deleted (they flag unresolved decisions).

## When to load
- "Write a PRD for …"
- "Prioritize these with RICE …"
- "Draft an RFC / one-pager / design review …"
- "Slice this epic into tickets …"
- "Design an A/B test for …"
- "Add this to the roadmap …"

## Output rules (apply to every artifact)
1. Cite evidence with `file:line` when grounding claims in the code or docs.
2. Never present one option. Minimum two, ideally three, with rejected alternatives listed.
3. Estimates are ranges: `optimistic / likely / pessimistic` + confidence %.
4. Every artifact ends with **"Decisions still needed"** and **"Next concrete step"** sections.
5. Empty fields stay as `TBD` with a one-line note on who can resolve them.

---

## Template A — Product Requirements Document (PRD)
Use when: owning a single decision for a new feature, behavior change, or integration.

```
# PRD: <title>
Status: Draft | In review | Approved | Shipped
Owner: <name>          Reviewers: <names>
Last updated: <date>   Decision needed by: <date>

## 1. Problem
- User & persona:
- Pain (in their words):
- Evidence (research, tickets, metrics, file:line):
- Today's workaround:
- Cost of inaction:

## 2. Hypothesis
We believe that <doing X> for <user Y> will result in <measurable outcome Z>.
We will know we are right when <observable signal>.

## 3. Goals / Non-goals
Goals:
- (measurable)
Non-goals (explicitly out of scope):
-

## 4. Options considered
| # | Option | Pros | Cons | Est. effort | Risk |
|---|--------|------|------|-------------|------|
| A | | | | opt/lik/pess | |
| B | | | | opt/lik/pess | |
| C | | | | opt/lik/pess | |
Rejected: A-variant — reason; …

## 5. Recommendation & rationale
Recommendation: Option _
Why this one (1 paragraph):
Why not the others:

## 6. User stories & acceptance criteria
US-1: As a <persona>, I want <capability>, so that <value>.
  Given <context> / When <action> / Then <observable outcome>
US-2: …

## 7. Slicing (ship in this order)
Slice 1 (smallest shippable): … — acceptance: … — rollback: …
Slice 2: …
Slice 3: …

## 8. Metrics & experiment
- Leading metric to move:
- Guardrail metric to protect:
- Entrance criterion: | Exit criterion:
- Experiment design: A/B vs holdout, duration, population, power:

## 9. Dependencies & risks
| Dependency | Owner | Status | Risk if late |
|------------|-------|--------|--------------|
| | | | |

## 10. Open questions
1. … (owner, needed-by)

## Decisions still needed
-
## Next concrete step
-
```

---

## Template B — One-pager (single bet)
Use when: proposing a small experiment or scoped bet before investing in a full PRD.

```
# One-pager: <title>
Owner: <name>   Date: <date>   Status: Draft | Approved | Killed

## Bet
One sentence: if we do X, then Y will happen.

## Why now
- Trigger / evidence (file:line where applicable):

## What we'll do
- Smallest thing we can ship to test the bet:

## What we won't do
-

## Success signal
- Observable metric, threshold, window:

## Failure signal
- Kill criterion (explicit):

## Cost & confidence
Effort: opt / lik / pess   Confidence in bet: ___%   Confidence in impact: ___%

## Decisions still needed
-
## Next concrete step
-
```

---

## Template C — RICE prioritization
Use when: ranking a list of candidate features or bets.

```
# RICE: <initiative name>
| # | Item | Reach (per period) | Impact (0.25/0.5/1/2/3) | Confidence (%) | Effort (person-weeks) | RICE score | Notes |
|---|------|--------------------|--------------------------|------------------|-----------------------|------------|-------|
| 1 | | | | | | (R×I×C)/E = | |
| 2 | | | | | | = | |

Ranking (highest score first):
1.
2.

Rejected / parked (with reason):
- Item — reason

Assumptions baked into Reach / Impact / Confidence (spell them out):
-
```

Scoring guide:
- **Reach** — number of people/accounts affected per period (be specific about the period).
- **Impact** — 3 = massive, 2 = high, 1 = medium, 0.5 = low, 0.25 = nominal.
- **Confidence** — 100% = measured, 80% = qualitative strong, 50% = gut, 20% = wild guess. Discount impact accordingly.
- **Effort** — total person-weeks across all functions (include review, infra, rollout, not just eng).
- **Score = (Reach × Impact × Confidence) / Effort**.

---

## Template D — RFC / Design review
Use when: the decision is technical and needs engineering sign-off before building.

```
# RFC: <title>
Owner:    Reviewers:    Status: Draft | Review | Approved | Rejected
Created: <date>   Decided-by: <date>

## Context & problem
-

## Goals / Non-goals
-

## Current state (evidence, file:line)
-

## Proposed design
- High-level:
- Key components / data flow:
- Interfaces:

## Alternatives considered (2 minimum)
| # | Alt | Pros | Cons | Why not |
|---|-----|------|------|---------|
| A | | | | |
| B | | | | |

## Risks & mitigations
- Risk → mitigation:

## Migration / rollout plan
- Phase 1: (with rollback)

## Open questions
-

## Decisions still needed
-
## Next concrete step
-
```

---

## Template E — Epic with sliced tickets
Use when: a PRD/RFC is approved and needs to become executable work.

```
# Epic: <title>
Parent PRD: <link>   Owner: <name>   Status: Planned

## Outcome
Epic moves <leading metric> from X → Y by <date>.

## Sliced tickets
Each ticket must ship independently, verify its own acceptance, and be rollback-safe.

### <Epic>-1: <slice title>
- Goal:
- Acceptance (Given/When/Then):
- Definition of done:
- Effort: opt/lik/pess
- Dependencies:
- Rollback / rollback trigger:

### <Epic>-2: …

## Out of scope (explicit)
-

## Decisions still needed
-
## Next concrete step
-
```

---

## Template F — Experiment design
Use when: every feature with a hypothesis needs a measurable test before full rollout.

```
# Experiment: <name>
Hypothesis: if X, then Y.
Owner: <name>   Platform: <analytics>   Status: Draft | Running | Analyzed | Shipped

## Design
- Type: A/B / A/B/n / holdout / before-after
- Population: <segment, % of eligible>
- Duration: <min days for power>   Power: ___%   MDE: ___
- Variant assignment: <randomization key>

## Metrics
- Primary: <leading> — direction: ↑
- Guardrails: <metric 1, metric 2> — direction: protected (both)
- Secondary: <exploratory>

## Entrance criterion
-

## Exit criteria
- Ship if:
- Kill if:
- Iterate if:

## Threats to validity & mitigations
- Threat: → mitigation:

## Decisions still needed
-
## Next concrete step
-
```

---

## Template G — Roadmap entry
Use when: communicating committed and exploratory work to stakeholders.

```
# Roadmap entry: <theme / quarter>

## Now (committed, ≤ next 2 weeks)
| Item | Owner | Exit signal | Confidence |
|------|-------|-------------|------------|
| | | | % |

## Next (committed, 2–6 weeks)
| Item | Owner | Exit signal | Confidence |
|------|-------|-------------|------------|
| | | | % |

## Later (exploratory, ≥ 6 weeks)
| Bet | Next checkpoint (what we need to learn) | Owner |
|-----|-----------------------------------------|-------|
| | | |

## Recently shipped (signals we read)
| Item | Outcome vs. hypothesis | Note |
|------|------------------------|------|
| | | |

## Decisions still needed
-
## Next concrete step
-
```

---

## Anti-patterns to refuse
- "PRD" with 12 goals — it's a roadmap. Split it.
- "Epic" with no acceptance criteria — it's a wish. Refuse to ship it.
- Point estimate with no confidence band — ask for the range.
- "Launch the feature" metric plan without a guardrail — block until defined.
- Recommendation with no rejected alternatives — send back for the criteria.
