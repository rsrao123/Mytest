# Offline Superpowers — Full Design

A complete design for the skill system that ships in `skills/`. This is the
local replacement for the `obra/superpowers` Claude Code plugin: a small,
composable library of behavior-shaping prompts that get welded onto agent
backstories at runtime to make each agent better at the specific kind of
work it does.

This document is the source of truth for **what each skill is for, when to
load it, and how skills compose**. The skill `.md` files themselves are
deliberately terse and prescriptive; the *why* and the *how* live here.

---

## 1. Goals & non-goals

### Goals
- **Composable behavior change** — drop a skill into an agent's backstory
  and the agent's outputs measurably shift on a fixed eval set.
- **Self-contained** — each skill is one file, one concern, no cross-imports.
- **Local-only** — no network calls, no SaaS plugin registry, no auth.
- **Reviewable** — skills are markdown, ≤ ~40 lines each. A human can read
  the whole library in 30 minutes.
- **Versioned with the codebase** — skills live in git, ship with the repo,
  and roll back atomically.
- **Deliberate, not reflexive** — every skill leads with a `## Think first`
  block that forces the agent to surface assumptions and choose before
  reaching for the imperative rules. Pattern-matching is the failure mode
  these skills exist to prevent.
- **Reasoning shown, not implied** — every skill also ships a
  `## Reasoning` block: a short, domain-specific inference procedure the
  agent must produce as written output before acting. This makes the
  skill's logic auditable in the agent's response, not just in its
  outcome.
- **Plan committed, not improvised** — every skill closes with a
  `## Plan` block: an ordered work program with stop-gates, an explicit
  definition of done, and a rollback condition. The agent commits to
  the plan *before* touching the work product, so deviations are
  visible.

### Non-goals
- Replacing fine-tuning. Skills bias behavior; they don't change capability.
- Hard guardrails. A skill is a strong nudge, not a runtime constraint —
  enforce hard rules in the LangGraph merge gate (`crews/merge_gate.py`),
  not in skills.
- Per-user personalization. Skills are global to the project; user-specific
  preferences belong in CLAUDE.md / CONVENTIONS.md.
- Multi-shot example libraries. Skills are principles; canonical examples
  live alongside the eval suite in `promptfooconfig.yaml`.

---

## 2. Architecture

```
┌──────────────────────┐                  ┌─────────────────────────┐
│  skills/<name>.md    │  ◄── authored by │  contributors           │
│  (markdown prompt)   │                  │  (one-PR-per-skill)     │
└─────────┬────────────┘                  └─────────────────────────┘
          │
          │ load(name)               ┌─────────────────────────┐
          ▼                          │  CrewAI Agent           │
┌──────────────────────┐    inject() │   role, goal, llm,      │
│  skills.loader       │ ───────────►│   tools, +skills appended│
│   load(*names) → str │             │   to backstory at boot  │
│   inject(agent, *n)  │             └─────────────────────────┘
└──────────────────────┘                          │
                                                  ▼
                                  ┌─────────────────────────┐
                                  │  vLLM (Qwen3-Coder-Next │
                                  │   or Devstral Small 2)  │
                                  └─────────────────────────┘
```

The loader is intentionally trivial (`offline-ai-stack/skills/loader.py`):
- `load("foo", "bar") → str` — concatenates `foo.md` and `bar.md` with a
  blank line between.
- `inject(agent, *names) → agent` — appends `load(*names)` to
  `agent.backstory` and returns the same agent.

That's it. No registries, no plugin manager, no lifecycle hooks. The
filesystem *is* the registry.

### 2.0 Anatomy of a skill file

Every skill file has four sections in a fixed order — **deliberate →
reason → plan → act**:

```
# Skill: <Name>

## Think first
- <reflective question that surfaces an assumption>
- <reflective question that names a tradeoff>
- <reflective question that catches a common failure>

## Reasoning
<one-line statement of when this procedure runs>:
1. <inference step 1 — observe>
2. <inference step 2 — classify or hypothesize>
3. <inference step 3 — check or experiment>
4. <inference step 4 — conclude with a named choice>

## Plan
<one-line statement of when this work program runs>:
1. <ordered action with exit criterion>
2. <ordered action with exit criterion>
3. Stop and <verify gate>: <what must be confirmed before continuing>
4. <ordered action with exit criterion>
Definition of done: <observable end state>.
Rollback if: <named condition> — <what to do>.

1. <imperative rule>
2. <imperative rule>
…
```

| Layer | Purpose | Form | Output the agent produces |
|---|---|---|---|
| `## Think first` | Metacognition: surface assumptions and tradeoffs before acting. | 3–4 reflective questions specific to the skill's domain. | None directly — the questions reshape the agent's plan. |
| `## Reasoning` | Inference: a domain-specific procedure for figuring out what's right. | 3–5 numbered steps; observe → hypothesize → check → conclude. | A written reasoning trace inline in the agent's response. |
| `## Plan` | Execution program: ordered actions with gates, definition of done, and rollback. | 3–5 numbered actions, ≥ 1 stop-gate, "Definition of done", "Rollback if". | A committed work program, posted before the work product appears. |
| Numbered rules | Action: imperative checklist for the actual work. | Action-first sentences. | The work product (diff, review, plan, etc.). |

All four layers are enforced by `tests/test_skills_loader.py`:

- `test_each_skill_has_think_first_section` — ≥ 3 reflective prompts.
- `test_each_skill_has_reasoning_section` — ≥ 3 numbered inference steps.
- `test_each_skill_has_plan_section` — ≥ 3 numbered actions, plus
  "Definition of done" and "Rollback if" markers.
- `test_skill_section_order` — `## Think first` → `## Reasoning` →
  `## Plan` order is mandatory.

Rationale: the rule layer alone is easy to pattern-match without
deliberation, especially under time pressure. The thinking layer
forces the agent to surface what it's assuming. The reasoning layer
forces the agent to *show its work* (auditable from the response, not
just the outcome). The plan layer forces the agent to commit to a
*sequence* with explicit gates, a named end state, and a rollback —
so a deviation is loud, not silent. Empirically (see
`promptfooconfig.yaml` baselines), the four-layer structure improves
rule adherence on ambiguous cases more than longer rule lists do, and
makes review by humans or downstream agents tractable.

#### Reasoning vs. Plan — why both?

Reasoning answers *"given this situation, what's the right thing?"*.
Plan answers *"given the right thing, how do I execute with checkpoints
and a rollback?"*. The same skill needs both because the agent fails
in two distinct ways: by reaching a wrong conclusion (a reasoning
failure) or by the right conclusion drifting during execution (a
planning failure). Splitting them keeps each section tight and lets
tests assert against each independently.

### 2.1 Why backstory injection, not system-prompt injection?

CrewAI prepends backstory + role + goal into the system prompt itself, so
"backstory injection" is just a controlled way of writing into the system
prompt without overriding the agent's role/goal. This:

- Keeps role/goal authoritative ("you are the Backend Developer") with
  skills as supporting principles, not competing instructions.
- Lets the same skill apply to many roles without contradicting any of
  their goals.
- Survives CrewAI's internal prompt construction without us reaching into
  private fields.

### 2.2 Failure modes

| Failure | Cause | Mitigation |
|---|---|---|
| Skill never fires | Agent ignored the instruction | Move the rule to LangGraph merge gate (deterministic check) |
| Skills contradict | Two skills disagree on a rule | Document the conflict in this file; pick one for the role |
| Backstory bloat | Too many skills loaded | Cap at ~5 per agent; if you need more, the role is too broad — split it |
| Skill drift | Skill rewritten without updating eval | Every skill PR must touch `promptfooconfig.yaml` if it changes behavior |

---

## 3. Skill catalog

Each entry below covers: **purpose**, **load triggers** (when an agent
benefits), **inverse triggers** (when loading hurts), **signals it's
working**, and **canonical companions** (skills that compose well).

### 3.1 Planning

#### `brainstorming`
- **Purpose:** force divergence before convergence on open-ended product or
  technical questions.
- **Load when:** the input is a problem statement, not a solution
  statement. CEO, product, architect roles.
- **Inverse:** narrow execution tasks (writing tests, applying a known
  patch). Divergence wastes tokens here.
- **Working signal:** outputs include ≥ 5 distinct directions before
  recommending one, with effort/impact/reversibility scoring.
- **Companions:** `writing-plans`, `architecture-decision-record`.

#### `writing-plans`
- **Purpose:** make plans rejectable. Every plan has a goal, acceptance
  criteria, ordered steps with verify + rollback, and an explicit
  out-of-scope.
- **Load when:** any agent that produces a multi-step plan another agent
  will execute. Architect, planner, release manager.
- **Inverse:** single-shot edits. Don't write a plan for a one-line fix.
- **Working signal:** a plan you can hand to a new contributor at 9 PM.
- **Companions:** `executing-plans` (for the receiving agent).

#### `executing-plans`
- **Purpose:** prevent silent deviation from a plan during execution.
- **Load when:** an executor agent (backend_dev, frontend_dev) is given a
  plan from a planner.
- **Inverse:** exploratory work where the plan is meant to evolve.
- **Working signal:** failures are reported with state, not improvised
  around.
- **Companions:** `commit-discipline`, `making-changes-incrementally`.

#### `architecture-decision-record`
- **Purpose:** capture *why* a non-trivial architectural choice was made,
  separately from *what* the diff did.
- **Load when:** architect role, especially when a change introduces a
  new module, swaps a dependency, or changes a wire protocol.
- **Inverse:** routine bug fixes; ADRs are infrastructure, not paperwork
  for every change.
- **Working signal:** PR descriptions link an ADR; context, decision,
  consequences, alternatives all present.
- **Companions:** `writing-plans`, `explaining-changes`.

### 3.2 Implementation

#### `test-driven-development`
- **Purpose:** force a failing test before any production-code change so
  you can prove the test fails for the right reason.
- **Load when:** behavior-changing code on a tested codebase.
- **Inverse:** prototype/spike code with no intent to ship; pure-typing
  refactors.
- **Working signal:** commit log shows red → green → refactor.
- **Companions:** `writing-tests`, `commit-discipline`,
  `making-changes-incrementally`.

#### `writing-tests`
- **Purpose:** raise the floor on test quality independent of TDD discipline.
- **Load when:** QA agent; any agent producing test diffs.
- **Inverse:** never alone — pair with `test-driven-development` or the
  agent will write tests *after* code that already passes them.
- **Working signal:** AAA structure visible, name encodes scenario, and
  the test fails when you mutate the production code (audit by hand on a
  sample).
- **Companions:** `avoiding-mocks`, `avoiding-flaky-tests`.

#### `avoiding-mocks`
- **Purpose:** push tests toward real components and hand-written fakes
  rather than `mock.patch` chains that couple to implementation.
- **Load when:** any test-writing agent on a codebase where mocks already
  proliferate.
- **Inverse:** integration tests where the *real* dep is genuinely
  untestable in CI (paid SaaS API). Use `handling-failures-and-retries`
  instead to drive the mock at the boundary.
- **Working signal:** new tests use fixtures over patches; assertions are
  on observable behavior, not call counts.
- **Companions:** `writing-tests`.

#### `avoiding-flaky-tests`
- **Purpose:** prevent the most common flakiness sources before they
  ship.
- **Load when:** any test-writing agent. Especially valuable on async or
  time-dependent code.
- **Inverse:** rare. Maybe in throwaway research notebooks.
- **Working signal:** new tests freeze time, seed randomness, isolate
  state, never sleep > 100ms.
- **Companions:** `writing-tests`, `avoiding-mocks`.

#### `yagni`
- **Purpose:** kill premature abstraction and speculative options.
- **Load when:** generative tasks (new features, new modules) where the
  agent tends to over-engineer.
- **Inverse:** library code that legitimately needs extension points;
  framework-level work.
- **Working signal:** diffs are smaller; helpers and flags appear only
  when a real caller needs them.
- **Companions:** `making-changes-incrementally`, `commit-discipline`.

#### `making-changes-incrementally`
- **Purpose:** keep diffs small, sequenceable, and bisectable.
- **Load when:** large-scope work (rewrites, migrations).
- **Inverse:** single-file fixes — the principle is implicit.
- **Working signal:** branch contains many small commits, each
  compiling and testing green.
- **Companions:** `commit-discipline`, `refactoring`.

#### `defensive-programming-discipline`
- **Purpose:** stop defensive checks where they don't earn their keep
  (internal calls, validated inputs).
- **Load when:** code-review agents and senior implementer roles. Most
  useful where the codebase is already over-validated.
- **Inverse:** security-critical input parsing — defensive checks are
  the *job* there. Use `security-review` instead.
- **Working signal:** fewer redundant `is None` guards; fewer
  catch-and-log blocks; failures crash loudly when they should.
- **Companions:** `security-review` (for the boundary case).

### 3.3 Debugging

#### `systematic-debugging`
- **Purpose:** replace speculation with falsifiable hypotheses.
- **Load when:** any bug-fix or incident-response work.
- **Inverse:** fixes already verified by reproducer + test; the
  discipline costs tokens you don't need to spend.
- **Working signal:** every reported finding has expected vs observed,
  hypothesis, and the experiment that proved/disproved it.
- **Companions:** `root-cause-tracing`, `handling-uncertainty`.

#### `root-cause-tracing`
- **Purpose:** prevent fixes-at-the-wrong-layer. Forces ≥ 3 levels of
  "why" before declaring a cause.
- **Load when:** the bug is non-trivial (not a typo or a missing import).
- **Inverse:** trivial fixes; production incidents in the
  *stabilize* phase (root-cause comes after stabilization).
- **Working signal:** the fix is at a different layer than the symptom,
  and the agent can name what other symptoms the same cause could
  produce.
- **Companions:** `systematic-debugging`, `incident-response`.

#### `handling-uncertainty`
- **Purpose:** make the agent surface confidence levels and stop inventing
  facts when knowledge is missing.
- **Load when:** every agent. This is closest to a default-on skill.
- **Inverse:** none meaningful.
- **Working signal:** outputs explicitly distinguish "I'm sure" / "I think"
  / "I'm guessing"; agent asks before guessing on file paths, APIs,
  versions.
- **Companions:** universal — pairs with anything.

#### `handling-failures-and-retries`
- **Purpose:** make retries safe (idempotent, bounded, jittered) and
  failures typed.
- **Load when:** code that calls external services, queues, or unreliable
  IO.
- **Inverse:** pure-function refactors. Adding retry skill there only
  invites speculative wrappers.
- **Working signal:** every retry path has a budget and a final-error
  type; logs include attempt #, delay, reason.
- **Companions:** `defensive-programming-discipline`, `writing-tests`.

### 3.4 Code understanding

#### `reading-code`
- **Purpose:** force "understand before change". The agent reads tests
  first, traces one path end-to-end, and matches the file's existing
  style.
- **Load when:** any agent touching a codebase it didn't author.
- **Inverse:** rare. Maybe greenfield where there is no existing code.
- **Working signal:** the diff matches local style; the PR description
  references the test file as the contract.
- **Companions:** `code-search`, `working-with-legacy-code`.

#### `code-search`
- **Purpose:** make the search itself disciplined (ripgrep first,
  definitions before call sites, narrow before reading).
- **Load when:** any agent that needs to find symbols. In practice, all
  implementer and reviewer roles.
- **Inverse:** none meaningful.
- **Working signal:** searches use word boundaries, narrow by file type,
  and rank results by proximity rather than alphabetic.
- **Companions:** `reading-code`.

#### `working-with-legacy-code`
- **Purpose:** characterize before changing; never bundle refactor + feature.
- **Load when:** code-review and implementer roles working on aging
  modules.
- **Inverse:** new code, library code without callers.
- **Working signal:** PR sequence is characterize → refactor → feature,
  not the reverse.
- **Companions:** `refactoring`, `making-changes-incrementally`,
  `writing-tests`.

#### `refactoring`
- **Purpose:** Tidy First. Behavior-preserving structural changes,
  isolated from feature commits.
- **Load when:** any agent explicitly tasked with restructuring; review
  agents flagging mixed-concern PRs.
- **Inverse:** review-only roles where the agent shouldn't be suggesting
  refactors at all (security-only review).
- **Working signal:** refactor commits and feature commits never share a
  commit; both pass the full test suite at every step.
- **Companions:** `making-changes-incrementally`, `commit-discipline`,
  `working-with-legacy-code`.

### 3.5 Collaboration

#### `pr-review`
- **Purpose:** baseline review checklist (correctness, tests, security,
  perf, style, docs) with explicit verdicts.
- **Load when:** review agents; especially the project-conventions
  compliance checker in `crews/code_review.py`.
- **Inverse:** implementer roles — they should be reviewing themselves
  via `requesting-code-review`, not playing reviewer.
- **Working signal:** each finding has a file:line anchor, and the
  output ends with APPROVE / REQUEST_CHANGES / BLOCK.
- **Companions:** `giving-code-review`, `security-review`.

#### `giving-code-review`
- **Purpose:** style of review (lead with what's good, suggest don't
  dictate, prefix nit/q/BLOCKER explicitly).
- **Load when:** any agent that posts review comments back to humans.
- **Inverse:** machine-only pipelines (merge gate) — bluntness is fine.
- **Working signal:** comments are scannable and authors don't go
  defensive.
- **Companions:** `pr-review`.

#### `requesting-code-review`
- **Purpose:** make the author's job include self-review and writing a
  good description so reviewers can pick it up cold.
- **Load when:** implementer roles that produce PRs (backend_dev,
  frontend_dev).
- **Inverse:** review-only or planner roles.
- **Working signal:** PR descriptions answer the reviewer's likely
  questions before they're asked.
- **Companions:** `explaining-changes`, `commit-discipline`.

#### `explaining-changes`
- **Purpose:** lead commit messages and PR descriptions with *why*, not
  *what*; surface caveats explicitly.
- **Load when:** any agent that writes a commit or PR description.
- **Inverse:** none meaningful.
- **Working signal:** future-you reading git blame at 2am understands the
  change without scrolling to the diff.
- **Companions:** `commit-discipline`, `requesting-code-review`.

#### `commit-discipline`
- **Purpose:** atomic, conventionally-formatted commits. No bundled
  refactor + feature; no debug prints.
- **Load when:** every implementer agent.
- **Inverse:** rebase-and-squash teams where individual commits are
  ephemeral. Even there, atomicity helps `git bisect`.
- **Working signal:** commits are reviewable in isolation;
  `type(scope): subject` format holds.
- **Companions:** `explaining-changes`, `making-changes-incrementally`.

### 3.6 Operations

#### `incident-response`
- **Purpose:** stabilize first, diagnose second; blameless postmortem
  with action items.
- **Load when:** an on-call or incident agent.
- **Inverse:** non-incident work; using this for normal bugs adds
  ceremony that doesn't earn its keep.
- **Working signal:** rollback or feature-flag flip happens before
  diagnosis; postmortem within 48h with owners on action items.
- **Companions:** `systematic-debugging` (for the diagnose phase),
  `handling-failures-and-retries`.

#### `dependency-hygiene`
- **Purpose:** pin, audit, schedule updates; one dep per PR; license
  justification on adds.
- **Load when:** the agent that opens dependency-update PRs and any
  reviewer of them.
- **Inverse:** application code where deps are inherited.
- **Working signal:** weekly audit cadence; new deps justified inline.
- **Companions:** `security-review`, `pr-review`.

#### `security-review`
- **Purpose:** structured audit against the OWASP-shaped checklist, with
  severity / file:line / exploit / fix per finding.
- **Load when:** the standalone security agent
  (`crews/security_review.py`) and the security_reviewer in
  `crews/dev_team.py`.
- **Inverse:** implementer roles — they shouldn't be auditing their own
  code in the same pass; that masks blind spots.
- **Working signal:** findings end with a triage recommendation
  (block / ship-with-followup).
- **Companions:** `pr-review`, `defensive-programming-discipline`.

### 3.7 Multi-agent coordination

#### `subagent-driven-development`
- **Purpose:** decompose tasks > ~50 LOC into focused subagent calls
  with tightly scoped contexts.
- **Load when:** the orchestrator role (architect, dev_team's planner).
- **Inverse:** small focused tasks — decomposition wastes tokens and
  flattens diffs.
- **Working signal:** subagent prompts contain only the files needed and
  return diff + rationale + self-review.
- **Companions:** `dispatching-parallel-agents`, `writing-plans`.

#### `dispatching-parallel-agents`
- **Purpose:** when to fan out concurrently and how to avoid write
  conflicts.
- **Load when:** orchestrator on a task with truly independent subtasks.
- **Inverse:** sequential dependencies — parallelism becomes a footgun.
- **Working signal:** explicit non-overlapping file scopes per agent;
  conflict-resolution handoff to the architect.
- **Companions:** `subagent-driven-development`.

#### `using-skills-effectively`
- **Purpose:** meta-skill on loading skills before tasks (not mid-stream),
  composing 2–3 narrowly, naming conflicts explicitly.
- **Load when:** every agent. The cheapest +1 skill you can add.
- **Inverse:** none.
- **Working signal:** the agent names which skills it's drawing on at
  the start of a task.
- **Companions:** universal.

#### `prompt-engineering`
- **Purpose:** raise the floor on prompts the agent itself writes (when
  it's authoring sub-prompts for tools or other agents).
- **Load when:** orchestrator and any role producing prompts for
  downstream agents.
- **Inverse:** consumers of prompts, not producers.
- **Working signal:** sub-prompts have a one-sentence task statement,
  examples, and an output schema.
- **Companions:** `subagent-driven-development`.

### 3.8 Frontend

#### `frontend-design`
- **Purpose:** force commitment to one aesthetic profile; ban the
  generic-AI-aesthetic anti-patterns; lock the component/styling/icons
  stack.
- **Load when:** the frontend_dev agent and the design_lead exec
  reviewer.
- **Inverse:** backend / infra agents.
- **Working signal:** outputs name the profile (LUXURY / REFINED /
  BRUTALIST / EDITORIAL) up front and stay within it.
- **Companions:** `yagni` (against speculative theming),
  `pr-review`.

---

## 4. Composition recipes per role

These are the canonical bundles for the agents in `crews/dev_team.py` and
`crews/code_review.py`. Treat them as defaults; tune per project.

```python
from skills import inject

# ---- Planning roles --------------------------------------------------
inject(product_planner,
       "brainstorming", "writing-plans", "handling-uncertainty",
       "using-skills-effectively")

inject(architect,
       "writing-plans", "architecture-decision-record",
       "subagent-driven-development", "dispatching-parallel-agents",
       "using-skills-effectively")

# ---- Implementer roles -----------------------------------------------
inject(backend_dev,
       "test-driven-development", "writing-tests", "avoiding-mocks",
       "yagni", "making-changes-incrementally",
       "commit-discipline", "explaining-changes",
       "reading-code", "code-search",
       "handling-uncertainty")

inject(frontend_dev,
       "frontend-design",
       "test-driven-development", "writing-tests", "avoiding-flaky-tests",
       "yagni", "commit-discipline", "explaining-changes",
       "reading-code", "handling-uncertainty")

# ---- Review roles ----------------------------------------------------
inject(bug_hunter,
       "systematic-debugging", "root-cause-tracing",
       "pr-review", "code-search")

inject(security_reviewer,
       "security-review", "pr-review",
       "defensive-programming-discipline")

inject(perf_reviewer,
       "pr-review", "systematic-debugging", "code-search")

inject(qa_engineer,
       "writing-tests", "avoiding-mocks", "avoiding-flaky-tests",
       "test-driven-development")

# ---- Process roles ---------------------------------------------------
inject(release_manager,
       "writing-plans", "incident-response", "dependency-hygiene",
       "explaining-changes", "handling-failures-and-retries")

inject(doc_writer,
       "explaining-changes", "architecture-decision-record",
       "reading-code")

# ---- Exec review (Stack-equivalent) ----------------------------------
inject(ceo,         "writing-plans", "yagni", "handling-uncertainty")
inject(eng_lead,    "writing-plans", "architecture-decision-record",
                    "yagni", "making-changes-incrementally")
inject(design_lead, "frontend-design")
inject(qa_lead,     "writing-tests", "avoiding-flaky-tests",
                    "incident-response")
inject(release_mgr, "incident-response", "handling-failures-and-retries",
                    "dependency-hygiene", "explaining-changes")
```

### 4.1 Heuristics for assembling a bundle

1. **Cap at five skills per agent.** Past that, behavior diverges and
   prompt budget hurts.
2. **Always include `using-skills-effectively`** for any agent loading
   ≥ 3 skills.
3. **Always include `handling-uncertainty`** for any agent that takes
   open-ended user input.
4. **Pair every "planner" with `writing-plans`** and every "executor"
   with `executing-plans` on the receiving end.
5. **Don't mix `defensive-programming-discipline` with `security-review`
   on the same agent.** They pull in opposite directions; route them to
   different agents.
6. **Don't load `incident-response` outside incident roles.** It adds
   ceremony that doesn't fit normal workflows.

---

## 5. Authoring new skills

### 5.1 Template

```markdown
# Skill: <Name>

## Think first
- <Domain-specific question that surfaces an assumption.>
- <Domain-specific question that forces a tradeoff to be named.>
- <Domain-specific question that tests for a common failure mode.>
- <Optional fourth question.>

## Reasoning
<One-line statement of when this procedure runs>:
1. <Observe — what facts to inventory.>
2. <Classify or hypothesize — what to label or guess.>
3. <Check or experiment — what to verify before concluding.>
4. <Conclude — what named choice to produce.>

## Plan
<One-line statement of when this work program runs>:
1. <Ordered action with an exit criterion.>
2. <Ordered action with an exit criterion.>
3. Stop and <verify gate>: <what must be confirmed before continuing>.
4. <Ordered action with an exit criterion.>
Definition of done: <observable end state>.
Rollback if: <named condition> — <what to do>.

1. <Imperative sentence>.
2. <Imperative sentence>.
3. <Imperative sentence>.
…
```

The four layers do different jobs:

- **`## Think first`** — 3-4 reflective questions in the agent's voice,
  specific to *this* skill's domain. Their job is to make the agent
  deliberate before acting: surface an assumption, name a tradeoff, or
  catch a common failure mode. Generic prompts ("think carefully") are
  rejected — questions must be checkable against the agent's eventual
  output.
- **`## Reasoning`** — 3-5 numbered inference steps the agent must
  produce as written output. The shape is observe → hypothesize/classify
  → check/experiment → conclude. Generic chain-of-thought ("think step
  by step") is rejected — the steps must encode the *specific* moves
  that this skill demands. The agent's written trace is the audit
  surface.
- **`## Plan`** — 3-5 numbered actions the agent commits to before
  touching the work product, plus at least one explicit stop-gate, a
  Definition of done (observable end state), and a Rollback if
  (named failure condition + recovery action). Plans without all three
  are rejected. The plan layer makes execution drift loud rather than
  silent.
- **Numbered rules** — imperative, action-first, one sentence each.
  This is the *do* layer that the deliberation, inference, and planning
  layers feed into.

Constraints:
- ≤ 70 lines total (Think first + Reasoning + Plan + rules).
- 3–4 thinking questions, 3–5 reasoning steps, 3–5 plan actions, ≤ 10
  imperative rules.
- One sentence per item, present tense, action-first for rules and plan;
  question form for `## Think first`; imperative form for `## Reasoning`
  steps.
- No anecdotes, no rationale paragraphs. Anecdotes go here in
  `SUPERPOWERS.md`.
- File name is kebab-case and matches the heading.
- Skill must be checkable: a reviewer can audit one output at a time
  against the thinking prompts, the reasoning trace, the plan
  commitments, and the rules.

### 5.2 Submission checklist

- [ ] File created at `skills/<kebab-name>.md`.
- [ ] Heading matches `# Skill: <Title Case>`.
- [ ] `## Think first` section present with ≥ 3 domain-specific questions.
- [ ] `## Reasoning` section present with ≥ 3 numbered inference steps.
- [ ] `## Plan` section present with ≥ 3 numbered actions, "Definition of done", and "Rollback if".
- [ ] Section order is `Think first` → `Reasoning` → `Plan` → numbered rules.
- [ ] Numbered rules section present.
- [ ] Added to `tests/test_skills_loader.py::REQUIRED_SKILLS`.
- [ ] `pytest tests/` passes (file exists, heading, all three sections, order, all counts and markers).
- [ ] Catalog entry added to §3 here, including triggers, inverse,
  working signal, companions.
- [ ] If the skill changes implementer behavior, add at least one new
  case to `promptfooconfig.yaml` that exercises it.

### 5.3 Anti-patterns to reject in review

- **Vague imperatives.** "Be careful with X" — not actionable.
- **Compound rules.** "Use a transaction and add a metric and write a
  test" — split into multiple skills.
- **Tooling-specific rules.** Skills are language- and stack-agnostic;
  put tooling rules in `CONVENTIONS.md`.
- **Aspirations dressed as rules.** "Ensure correctness" is a goal, not
  a skill.
- **Duplicate concerns.** If `yagni` already says it, don't write
  `dont-overengineer`.
- **Generic thinking prompts.** "Think carefully" or "Consider all
  options" in the `## Think first` section. The questions must be
  domain-specific and checkable against the agent's output — generic
  prompts add tokens and remove no errors.
- **Thinking-layer overlap with rules.** If a `## Think first` question
  has a 1:1 mapping with a numbered rule, drop one. The two layers
  should ask the agent to deliberate and then act, not say the same
  thing twice.
- **Generic reasoning chains.** "Think step by step" or "Break the
  problem down" in the `## Reasoning` section. The numbered steps must
  encode the *specific* moves that this skill demands — observe what,
  classify how, check against what, conclude with which named choice.
  If the steps would apply equally to a different skill, they're too
  generic.
- **Reasoning that doesn't terminate in a choice.** Every reasoning
  trace must end in a named, observable conclusion (a verdict, a
  classification, a chosen option, a typed error). Open-ended reasoning
  invites the agent to keep deliberating without acting.
- **Plans without stop-gates.** A `## Plan` that's just a numbered list
  with no explicit "Stop and …" pause is just a rule list with extra
  steps. The whole point of the plan layer is to surface drift; without
  a checkpoint, drift hides.
- **Plans without a Definition of done.** If the plan can't name the
  observable end state, the agent doesn't know when to stop. Tests
  reject any plan missing this marker.
- **Plans without a Rollback if.** If the plan can't name a failure
  condition + a recovery action, the agent will improvise on failure —
  which is exactly what `executing-plans` forbids. Tests reject any
  plan missing this marker.
- **Plans that duplicate the Reasoning section.** If the plan is just
  the reasoning trace re-numbered, the skill doesn't have a real
  execution program — the reasoning was masquerading as a plan. Add
  stop-gates, exit criteria, and rollback to make it a real plan, or
  collapse the two sections.

---

## 6. Eval & maintenance

### 6.1 Behavior must be measurable

Every skill that changes implementer behavior gets one or more
`promptfooconfig.yaml` cases whose `llm-rubric` would *fail* if the skill
were removed. The eval set in `promptfooconfig.yaml` already covers
many of these implicitly; explicit per-skill coverage is the long-term
goal.

### 6.2 Skill drift

Skills are versioned with the codebase. When a skill changes:

1. Re-run `promptfooconfig.yaml` against both vLLM models.
2. Diff scores against the pre-change baseline.
3. If any case regresses, either revert the skill change or update the
   case (with justification in the PR).

### 6.3 Sunset rule

If a skill hasn't been loaded by any agent for ≥ 3 months and isn't a
universal default (`handling-uncertainty`, `using-skills-effectively`),
delete it. Dead skills decay quietly because nobody re-reads them.

---

## 7. Mapping to Claude Code plugins

| Claude Code plugin / skill | Local equivalent |
|---|---|
| `obra/superpowers` (whole bundle) | `skills/` (32 markdown files) + `skills.loader` |
| `anthropic/frontend-design` | `skills/frontend-design.md` |
| `anthropic/security-guidance` | `skills/security-review.md` + `scripts/security_scan.sh` |
| `garytan/stack` (CEO/Eng/Design review) | `crews/exec_review.py` + the planning/yagni skill bundles |
| `claude-mem` | `scripts/claude_mem_local.py` (ChromaDB-backed) |
| `/code-review` (4 parallel agents) | `crews/code_review.py` with `pr-review`, `refactoring`, `systematic-debugging`, `code-search` skills loaded |

The key abstraction: in Claude Code, a "plugin" is a discoverable bundle
of skills, slash commands, and tools. Here, the plugin surface
decomposes into:

- **Skills** → `skills/*.md`
- **Slash commands** → `Makefile` targets
- **Tools** → CrewAI tools (`FileReadTool`, `DirectoryReadTool`,
  `GitTool`)
- **Agent definitions** → `crews/*.py` files

This decomposition is intentional. It means a project can adopt one
piece at a time (just the skills, just the merge-gate, just the eval
harness) without buying the whole framework.

---

## 8. Future work

- **Per-project skill overrides.** Allow `<project>/.skills/<name>.md`
  to shadow the global skill. Today the loader only reads the central
  directory.
- **Skill-aware eval matrix.** Auto-generate a promptfoo matrix that
  runs each case both with and without each skill, to measure marginal
  contribution.
- **CLAUDE.md compatibility.** Make the loader optionally read a
  project's `CLAUDE.md` and prepend it ahead of skills, so this stack
  can drop into a Claude Code repo without renaming.
- **Skill-of-skills.** A meta-loader that picks skills automatically
  from the task description. Risky — invites silent over-injection —
  so gated behind an explicit opt-in.

---

## 9. Quick reference

```
skills/
├── architecture-decision-record.md     planning
├── avoiding-flaky-tests.md             implementation
├── avoiding-mocks.md                   implementation
├── brainstorming.md                    planning
├── code-search.md                      code-understanding
├── commit-discipline.md                collaboration
├── defensive-programming-discipline.md implementation
├── dependency-hygiene.md               operations
├── dispatching-parallel-agents.md      multi-agent
├── executing-plans.md                  planning
├── explaining-changes.md               collaboration
├── frontend-design.md                  frontend
├── giving-code-review.md               collaboration
├── handling-failures-and-retries.md    debugging
├── handling-uncertainty.md             debugging
├── incident-response.md                operations
├── making-changes-incrementally.md     implementation
├── pr-review.md                        collaboration
├── prompt-engineering.md               multi-agent
├── reading-code.md                     code-understanding
├── refactoring.md                      code-understanding
├── requesting-code-review.md           collaboration
├── root-cause-tracing.md               debugging
├── security-review.md                  operations
├── subagent-driven-development.md      multi-agent
├── systematic-debugging.md             debugging
├── test-driven-development.md          implementation
├── using-skills-effectively.md         multi-agent (universal default)
├── working-with-legacy-code.md         code-understanding
├── writing-plans.md                    planning
├── writing-tests.md                    implementation
└── yagni.md                            implementation
```

32 skills, eight themes, one loader, no network.
