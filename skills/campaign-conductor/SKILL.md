---
name: campaign-conductor
description: Run a project as an orchestrated campaign — Claude as conductor dispatching a mixed fleet of workers: Claude (Opus) agents for UI/UX and design judgment, OpenAI Codex CLI workers for implementation and everything else. Use whenever the user says "start a campaign", "campaign mode", "orchestrate this", "use the fleet", "mix of agents", "send out workers", "codex workers", or asks Claude to run a multi-task project by delegating to parallel agents rather than implementing directly. Also use when resuming work in a repo whose CLAUDE.md points at a campaign-hq folder.
license: MIT
compatibility: Designed for Claude Code (uses the Agent and Workflow tools). OpenAI Codex CLI (github.com/openai/codex) is optional; without it, route all work to Claude agents.
metadata:
  author: jvogan
  version: "0.4.0"
---

# Campaign Conductor

You are the conductor. During a campaign your context window is the scarcest
resource in the system — spend it on surveying, planning, dispatching,
verifying, and recording, and let workers spend theirs on implementation. If
you catch yourself writing feature code inline mid-campaign, stop and dispatch
it.

The skill exists to bootstrap; the campaign folder is the source of truth.
After bootstrap, everything a future session needs lives in the repo, so this
skill never has to load again for this project.

## Bootstrap (first trigger in a project)

If the project already has a campaign folder (check CLAUDE.md for a pointer),
skip bootstrap: read CAMPAIGN.md, LEARNINGS.md, and preferences.md, then resume.

Otherwise create the folder — default `docs/campaign-hq/`, or another name if
that path already holds unrelated content (e.g. `docs/<project>-campaign/`).
Any name works; the CLAUDE.md pointer is what makes it discoverable. Create
three files (skeletons at the bottom of this document):

- `CAMPAIGN.md` — the plan: goal, phases, task list with status
- `LEARNINGS.md` — running log of outcomes, worker quirks, decisions
- `preferences.md` — the worker-routing table for this project

`briefs/` and `schemas/` grow under the same folder from the first dispatch
that needs them.

Then add this block to the project's CLAUDE.md (create the file if missing):

```markdown
## Active Campaign
Campaign state lives in `docs/campaign-hq/`. Before doing project work, read
CAMPAIGN.md (plan), LEARNINGS.md (history), and preferences.md (worker
routing). Act as orchestrator: dispatch workers per preferences.md rather than
implementing directly. Doctrine: the campaign-conductor skill.
```

This pointer frees the user from ever re-invoking this skill — every future
session in the repo auto-discovers the campaign.

## Worker routing

Defaults (written into preferences.md at bootstrap so the user can edit them):

| Work | Worker | How |
|---|---|---|
| UI/UX, visual design, design review, frontend polish | Claude Opus, high effort | Workflow `agent()` with `model:'opus', effort:'xhigh'`; or Agent tool `model:"opus"` (inherits session effort — see below) |
| Implementation, refactors, tests, scripts, debugging, research | Codex CLI (highest reasoning) | `codex exec` headless (pattern below) |
| Quick code search / codebase questions | Native Explore / general-purpose subagent | Agent tool |

Precedence: **what the user just said > preferences.md > these defaults.**
When the user expresses any routing preference ("use sonnet for tests", "no
opus this week"), update preferences.md in the same turn — that persistence is
what makes the preference outlive the session. Don't ask permission to record
it.

Effort mechanics: the Agent tool has no per-agent effort parameter (spawns
inherit the session's effort), while Workflow's `agent()` accepts
`effort:'xhigh'`. For guaranteed-high-effort Claude workers, dispatch through
Workflow — this skill's instruction counts as the explicit opt-in Workflow
requires. Codex effort is pinned in its own config (set
`model_reasoning_effort` in `~/.codex/config.toml`), so codex workers run at
their configured effort on every dispatch.

## Kickoff: size the campaign to the project

Auto-decide; don't make the user choose.

- **Small or familiar** (roughly: you can hold the architecture in your head, or
  the user handed you a concrete task list): write CAMPAIGN.md yourself in a few
  minutes and start dispatching.
- **Large or unfamiliar**: fan out 2–4 parallel survey agents (native
  subagents — architecture, conventions, risk/debt, test story), synthesize
  their reports into CAMPAIGN.md, and get the user's sign-off on the plan
  before dispatching workers. The survey cost pays for itself in better worker
  briefs — most worker failures trace back to a brief that misdescribed the
  codebase.

## Dispatching Codex workers

Codex CLI is OpenAI's headless coding agent; install and authentication are
documented at <https://github.com/openai/codex>. A ChatGPT subscription login
gives flat-rate workers, which makes wide fan-out economical. If the user has
no Codex CLI, route implementation work to Claude agents instead.

Codex workers are **fire-and-collect**: while a run is in flight there is no
steering and no follow-up questions (a finished session can be resumed with
corrections — see Steering below). That constraint dictates the brief. Every
dispatch must be self-contained: goal, relevant files/dirs, constraints and
conventions to follow, how the worker should verify its own work (command to
run), and what to put in the final message. If you can't write that brief,
the task isn't scoped yet — scope it first.

```bash
# one worker: run in background Bash, collect out.txt on exit
codex exec --json --skip-git-repo-check -s workspace-write -C <dir> \
  -o /path/to/out-taskname.txt "<self-contained brief>"

# a wave: N workers, each in its own worktree, all running concurrently.
# Launch as a single background Bash call; each worker's -o file is its
# collection point.
for task in palette highlight ranking budget; do
  git -C <repo> worktree add "../wt-$task" -b "campaign/$task"
  codex exec --json --skip-git-repo-check -s workspace-write \
    -C "<repo>/../wt-$task" -o "/tmp/out-$task.txt" \
    - < "docs/campaign-hq/briefs/$task.md" &
done
wait

# if the user has a second Codex account, split the wave across both
CODEX_HOME="$HOME/.codex-account2" codex exec --json --skip-git-repo-check \
  -s workspace-write -C <dir> -o /path/to/out-taskname2.txt "<brief>"
```

- Each `codex exec` is an independent OS process; the CLI imposes no
  concurrency ceiling. The practical limits are machine resources and your
  verification bandwidth when the wave lands. Ten or more concurrent workers
  is routine for read-only analysis; hold writer waves to the verifiable cap
  in the waves section below.
- Write each brief to a file (`docs/campaign-hq/briefs/<task>.md`) rather
  than inlining it in the loop; briefs are reviewable, reusable on retry, and
  keep the dispatch command short (`codex exec ... - < briefs/<task>.md`
  reads the brief from stdin). Keep proven brief shapes per task type there
  and instantiate from them; a repeated brief fix becomes a template edit.
- Sandbox: `read-only` for analysis/review tasks, `workspace-write` for
  implementation. Never `danger-full-access` without the user asking.
- Subscription-authenticated Codex accounts have no metered per-token cost —
  fan out freely; with multiple accounts, split tasks across them.
- Size tasks to one sitting (~15–60 min of agent work) with a verifiable
  output. Bigger than that, split it; the orchestrator owns sequencing.

### Codex worker capabilities

Codex workers carry more than code editing; route these into campaigns:

| Capability | Invocation | Campaign use |
|---|---|---|
| Model + effort per call | `-m <model> -c model_reasoning_effort=<level>` | effort policy, below |
| Structured report | `--output-schema docs/campaign-hq/schemas/worker-result.json` | machine-checkable collection |
| Live web search | `--search` | read-only research scouts for volatile facts: framework APIs, advisories, current versions |
| Image input | `-i current.png -i target.png` | UI fixes from screenshots and mocks; visual bug reproduction |
| Image generation | prompt the built-in `image_gen` tool | asset generation; the tool saves under `~/.codex/generated_images/<session>/`, so the brief must tell the worker to copy the file into the repo and verify it exists |
| Review mode | `codex exec review --base <ref>` (read-only) | cross-model review gates; post-integration regression sweeps |
| Session continuation | `codex exec resume <session-id> "<correction>"` | steering, below |
| Native subagents | prompt the built-in `multi_agent_v1` tools (`spawn_agent`, `wait_agent`, `send_input`, `close_agent`) | a codex worker fans out its own parallel subagents inside one workspace; see Squads |

Default every worker to the strongest configuration: Claude workers at high
effort, codex workers at the strongest model and reasoning the user's config
provides (e.g. gpt-5.5 at xhigh). Subscription auth prices strong and cheap
workers identically, so a downgrade buys latency only, and a cheap model on
a real task produces rework. Downshift a task type
(`-m gpt-5.4-mini -c model_reasoning_effort=low`) only when the user asks
for it or preferences.md records it; record any such request in
preferences.md in the same turn so it persists. Architecture, debugging, and
judging always run at highest effort. Per-call flags leave the user's config
untouched.

**Steering.** A finished codex session resumes with its context intact:
`codex exec resume <session-id> "<correction>"`. Capture each worker's
session id from the `--json` event stream at dispatch and record it in the
fleet table. Resume when the output is mostly right (missed convention, one
failing test) — the worker keeps its established model of the branch.
Redispatch from zero when the approach itself was wrong. `codex fork
<session-id>` explores an alternative from the same context without
disturbing the original.

OpenAI also ships a Codex plugin for Claude Code —
<https://github.com/openai/codex-plugin-cc> — adding `/codex:review`,
`/codex:adversarial-review`, and background-delegation commands
(`/codex:rescue`, `/codex:status`, `/codex:result`). Those commands suit
single interactive tasks the user runs themselves; use the headless `codex
exec` pattern above for fleet dispatch, where the conductor owns many workers
at once.

Claude workers (Agent tool or Workflow) accept mid-run steering — use
SendMessage to redirect a running native agent instead of killing and
respawning.

## Permissions

Workers need their full power for the whole wave — a permission prompt
raised mid-run stalls that worker and everything downstream of it. Default
to a powerful envelope, state it in one line at kickoff, record it in
preferences.md, and tighten it only when the user asks (regulated repo,
production credentials, offline requirement).

The default envelope:

- **Codex: `workspace-write` with network on and approvals off.** The
  sandbox covers implementation including commits inside linked worktrees,
  but codex ships it with network disabled (DNS fails inside the sandbox)
  and `codex exec` cannot answer approval prompts. Dispatch with
  `-c sandbox_workspace_write.network_access=true -c approval_policy=never`
  (or set both in `~/.codex/config.toml` once) so workers can install
  dependencies and never stall. Use `read-only` for scouts and reviewers;
  `danger-full-access` when the user asks for it.
- **Claude workers: edits pre-accepted.** They inherit the session's
  permission mode, and in approve-as-you-go mode a background worker blocks
  at its first prompt — the wave silently loses a member. Run campaign
  sessions with edits pre-accepted or an allowlist covering the build and
  verify commands; the Agent tool's `mode` parameter adjusts the envelope
  per spawn.

## Parallel fleets: isolation, integration, waves

One writer in the tree at a time is the invariant. How you keep it depends on
fan-out size:

- **2–3 writers, naturally disjoint files** (docs vs backend vs CI): shared
  tree is fine. State each worker's file boundary in its brief and say the
  boundary exists because siblings are running.
- **Anything larger, or overlapping territory**: one git worktree + branch per
  worker. Native agents get this free (`isolation: 'worktree'` on Agent/
  Workflow). For codex workers, create it yourself before dispatch and point
  `-C` at it:

  ```bash
  git -C <repo> worktree add ../wt-<task> -b campaign/<task>
  codex exec ... -C <repo>/../wt-<task> -o out-<task>.txt "<brief>"
  ```

Fleet hygiene:

- Start each wave from a clean `git status` on a known base commit; every
  brief for a worktree worker must end with "commit your work on this branch
  with message `campaign/<task>: <summary>`". Uncommitted worktree output is
  invisible to integration.
- Record every dispatch in CAMPAIGN.md's fleet table (task, worker, branch,
  worktree path, session id, dispatch time, status). With 10+ codex workers
  out, this table is the only reliable picture of the fleet — `git worktree
  list` tells you what exists, but nothing about purpose or status.
- Remove worktrees (`git worktree remove`) and delete merged branches after
  integration; stale worktrees produce misleading `git status` output later.
- Record dispatch time and expected duration in the fleet table. A worker
  whose output file is still empty past ~3x its expected duration is stalled:
  kill it, inspect its worktree, then resume or redispatch. One stuck leaf
  otherwise blocks collection for the whole wave.

**Route integration like any other work.** Merging N branches involves real
judgment calls:

- **1–3 branches, small diffs**: merge them yourself sequentially, running
  tests between merges.
- **Many branches or semantic overlap** (two workers touched the same
  subsystem): dispatch an **integration worker** with a brief listing the
  branches, the merge order (dependency-first), the conflict-resolution
  intent ("worker A's schema wins; adapt B's callers"), and the full
  verification command. Route by the nature of the conflicts — Claude Opus
  when resolution needs design judgment (and you may want to steer
  mid-merge), codex when the reconciliation is mechanical at scale.
- Verify the merged result yourself (full test suite on the integrated
  branch) before merging to the campaign's main line.

**Structure big campaigns as waves**: dispatch → collect → integrate →
verify → next wave. Each wave's workers branch from the *integrated* result
of the last — stacking new work on un-integrated branches compounds conflicts
quadratically. Cap concurrent writers at what you can actually verify when
they land (≈4–6 codex workers per wave is a sane default; raise it only for
genuinely independent tasks like per-module migrations). Analysis/review
workers are read-only and don't count against the cap — fan those out as wide
as useful.

While verifying wave N — serial conductor work during which writers idle —
dispatch the wave N+1 tasks whose base does not depend on N's outcome.
Anything downstream of a task that might fail waits.

## Squads: nested delegation

A squad is one subagent acting as squad lead: it dispatches its own workers,
integrates, verifies the integrated result, and returns one structured
report. The squad absorbs the intermediate integration and per-worker diff
reads that would otherwise land in the conductor's context. Any worker that
can dispatch, integrate, and verify can lead; compose whatever shape the
sub-goal calls for. Two worked examples:

- A **Claude lead** (Opus or Sonnet) dispatching codex workers via `codex
  exec`, one worktree per leaf. A natural fit when the sub-goal needs design
  judgment or mid-flight steering of the squad itself.
- A **Codex lead** fanning out its native `multi_agent_v1` subagents
  (`spawn_agent`, `wait_agent`, `send_input`, `close_agent`), which share
  its single workspace. A natural fit for mechanical fan-outs in one
  worktree, with the brief assigning disjoint files to each subagent.

The rules below hold for every shape.

Dispatch a squad when a phase contains a cohesive sub-goal of **three or more
codex tasks that must integrate with each other** before the conductor needs
the result, or when verification is expensive enough (long suite, domain
harness) that it should run once at the sub-goal boundary. For independent
tasks that land directly on the main line, use flat dispatch; without
intermediate integration a squad only adds a report seam.

Rules, each preventing a specific failure:

- **Depth caps at two.** Conductor → squad lead → leaves. A squad lead
  dispatches leaf workers only and never spawns another lead. Leaf briefs
  must forbid spawning: codex workers carry native `multi_agent_v1` spawn
  tools (nested `codex exec` processes are blocked by the sandbox, but the
  native tools are not), so the rule has to be stated, and a hard cap on
  concurrent leaves goes in every lead's brief. Without both limits, each
  layer can multiply workers geometrically with no single owner of the
  result.
- **Namespaces are exclusive.** The conductor assigns each squad a prefix:
  integration branch `campaign/<squad>`, leaf branches
  `campaign/<squad>/<subtask>`, worktrees `../wt-<squad>-<subtask>`. The
  brief forbids branches or paths outside the prefix. Concurrent squads with
  disjoint prefixes cannot cross-contaminate worktree state.
- **Verification splits at the seam.** The squad lead runs the integrated
  verify command in its worktree before reporting; the conductor re-runs it
  when merging the squad's integration branch to the main line. The squad
  never merges to main; the conductor never dispatches into a squad's
  namespace.
- **One fleet-table row per squad** (`squad:opus (4 codex)`), tracking the
  integration branch. The squad keeps its own sub-table for its leaves;
  tracking leaves at the conductor level cancels the context savings that
  justified the squad.
- **Reports enumerate every leaf** with status and evidence (commit sha,
  verify output tail). Reject a squad report that claims success without
  per-leaf evidence.
- **Squads live one wave.** Branch all concurrent squads from the same
  integrated base and merge them in the same wave. The brief requires the
  squad to remove its leaf worktrees before reporting and to list any it
  could not remove; sweep for the squad's prefix afterward as the second
  net.

The squad-lead brief carries: sub-goal and file boundary (including what
sibling squads own), base commit, namespace prefix, the decomposition or
explicit authority to decompose, the leaf cap, the verify command, the
stop-at-integration-branch rule, worktree cleanup, and the report schema.
Squad leads orchestrate; they may resolve a small merge conflict inline and
must not write feature code.

## Worker reports and review gates

**Structured reports.** Every brief ends by requiring a fixed-schema report:
`status`, `branch`, `commit`, `files_changed`, `verify_cmd`, `verify_result`
(pass/fail plus output tail), `blockers`. Codex workers: pass
`--output-schema` with the schema file. Claude workers: require a fenced JSON
block as the final message. Collection then means parsing records instead of
reading prose, and a missing `verify_result` mechanically marks a task
incomplete. Keep the schema in `docs/campaign-hq/schemas/`.

**Cross-model review.** The reviewing model catches what the author's model
cannot see in itself. After a codex worker lands a high-risk diff (auth, data
migration, shared state), dispatch a Claude reviewer; after a Claude worker
lands one, run `codex exec review --base <ref>` read-only against the
branch. After each wave's integration, a codex review of the merged result
catches semantic conflicts that appear only after individually valid
branches combine. Keep author and reviewer separate in every gate: the
agent that changed the code never supplies the only evidence that it works.

**Bake-offs.** For a high-stakes task with uncertain solution shape (tricky
algorithm, design-sensitive component), dispatch the identical brief to two
workers in separate worktrees — codex vs opus, or the two codex accounts —
and have a judge pick against criteria written into the brief before
dispatch, correctness first. Give the judge artifacts (diffs, verify output,
screenshots) rather than the workers' own summaries. A bake-off costs double
the worker spend plus a judge; reserve it for tasks where rework would cost
more.

## Verify, record, check in

The conductor owns correctness.

- After each worker returns: read the diff, run the verification command from
  the brief (tests, build, lint). Treat every worker report as a claim to
  check; mark a CAMPAIGN.md task done only after your own verification run
  passes. Re-verify at every seam — after each merge to the main line and
  after each squad hands back its integration branch.
- Log every dispatch outcome in LEARNINGS.md — one line minimum: date, task,
  worker, result, lesson. The lessons compound: "codex ignored our import
  ordering; add it to briefs" saves every subsequent dispatch. This file is
  the campaign's memory; future sessions read it instead of rediscovering.
- Where the project has CI, push worker branches and read the check results
  (`gh pr checks`, `gh run list`) as a second verification layer — CI runs
  the full matrix without occupying conductor context. Still run the
  decisive suite yourself before merging to the main line.
- Update task status in CAMPAIGN.md as you go, so a cold session can resume
  from the file alone.
- Check in with the user at phase boundaries and on plan-changing surprises,
  rather than per task. The user delegated so they wouldn't have to
  supervise.

**Fold in feedback as it happens, and keep the files lean.** When the user
corrects you or a dispatch goes sideways mid-session, record it in the same
turn — feedback about *routing* ("stop using opus for tests") goes to
preferences.md; feedback about *process* ("your briefs are too vague",
"integrate more often") goes to LEARNINGS.md. Don't wait for a wrap-up pass
that may never come.

These files earn their keep only while they're cheap to read at session
start, so compact as you write:

- Keep LEARNINGS.md as distilled rules. When a lesson repeats or the log
  passes ~40 lines, promote the durable lessons to a short **Standing rules**
  list at the top and delete the raw entries they came from.
- preferences.md stays under one screen. Overwrite stale preferences; don't
  append history.
- A lesson that's true for *any* project (not just this one) belongs in the
  skill itself — offer to fold it into the user's installed copy of this
  skill, replacing or tightening existing text rather than appending, so the
  doctrine improves without growing.

## File skeletons

`CAMPAIGN.md`
```markdown
# Campaign: <name>
Goal: <one sentence>
Status: <phase N of M — one line>

## Phases
### Phase 1 — <name>
- [ ] <task> — worker: <routing> — verify: <command>

## Fleet (active dispatches)
| Task | Worker | Branch | Worktree | Session | Dispatched | Status |
|---|---|---|---|---|---|---|
```

`LEARNINGS.md`
```markdown
# Campaign Learnings
<!-- newest first: date | task | worker | outcome | lesson -->
- 2026-07-04 | example task | codex | done, tests pass | briefs need explicit import-order rule
```

`preferences.md`
```markdown
# Worker Routing Preferences
<!-- Precedence: user's live instruction > this file > skill defaults.
     Update this file whenever the user states a preference. -->
- UI/UX, design: claude opus, high effort
- Implementation, tests, research: codex CLI, highest reasoning
- Quick search: native subagents
- Check-in cadence: phase boundaries
- Permission envelope: codex workspace-write, network on for dependency
  tasks; claude workers with edits pre-accepted
```
