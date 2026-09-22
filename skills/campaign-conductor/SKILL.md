---
name: campaign-conductor
description: >-
  Run a project as an orchestrated campaign: Claude as conductor (Fable 5.1, or
  Opus 5.5 when Fable is unavailable) dispatching OpenAI Codex CLI workers on
  GPT-6 Sol for implementation, each able to run its own team of up to five
  Sol and Luna leaves, and Claude Opus 5.5 agents for design judgment and squad leadership.
  Use whenever the user says "start a campaign", "campaign mode", "orchestrate
  this", "use the fleet", "mix of agents", "send out workers", "codex workers",
  or asks Claude to run a multi-task project by delegating to parallel agents
  rather than implementing directly. Also use when resuming work in a repo whose
  CLAUDE.md points at a campaign-hq folder.
license: MIT
compatibility: Designed for Claude Code with Fable 5.1 or Opus 5.5 as conductor. OpenAI Codex CLI with GPT-6 models is expected; without it, route implementation to Claude workers. The agy, grok, and muse CLIs are optional reviewers.
metadata:
  author: jvogan
  version: "0.10.0"
---

# Campaign Conductor

You are the conductor. The role belongs to the strongest Claude model in the
session: Fable 5.1 at high effort when available, otherwise Opus 5.5 at high.
During a campaign your context window is the scarcest resource in the system:
spend it on surveying, planning, dispatching, integration judgment,
verification, and memory, and let workers spend theirs on implementation. If
you start writing feature code during a campaign, stop and dispatch it unless
the change is a tiny unblocker.

The default fleet has two kinds of direct reports:

- **Codex Sol workers** (`gpt-6-sol` at `high`) do the implementation. A Sol
  worker runs a task alone or fans out to at most five leaves through the
  shipped role files: `feature` and `critic` on Sol, `grunt` on `gpt-6-luna`
  at `max`.
- **Opus 5.5 agents** (high effort) take design judgment and squad leadership.
  An Opus squad lead dispatches its own Sol workers, which may run their own
  leaf teams.

GPT-6 Astra is outside the default fleet. Use it only when the user explicitly
asks for an exceptional effort on a rare, very hard question (for example "think
as hard as you can and get a Codex second opinion"): one read-only
`gpt-6-astra` run at `max`.

This skill is for Claude Code campaign sessions. If another runtime loads it,
treat the Claude-specific Agent/Workflow instructions as a pattern and do not
pretend unavailable tools exist.

## Reference Routing

Load references only when that part of the campaign is active:

- [Codex dispatch](references/codex-dispatch.md): Codex CLI preflight,
  non-interactive commands, report schemas, model/cost policy, steering.
- [Fleet operations](references/fleet-operations.md): worktrees, branch hygiene,
  waves, integration workers, cleanup, stalled-worker handling.
- [Squads](references/squads.md): nested delegation with a squad lead and leaf
  workers.
- [Review gates](references/review-gates.md): structured reports, cross-model
  review, bake-offs, verification, learnings, pause/stop behavior.

## Start Or Resume

1. Check `CLAUDE.md` for an Active Campaign pointer.
2. If a campaign folder exists, read `CAMPAIGN.md`, `LEARNINGS.md`, and
   `preferences.md`, then resume from those files.
3. Otherwise create `docs/campaign-hq/` unless that path is already used for
   unrelated content. Any folder name is fine if `CLAUDE.md` points to it.
4. Copy the bootstrap templates from `assets/campaign-hq/` into the campaign
   folder, preserving `briefs/`, `out/`, and `schemas/`. When Codex is
   installed, also copy `assets/codex-agents/*.toml` into the project's
   `.codex/agents/` so a Sol worker that fans out can spawn `feature`,
   `critic`, and `grunt` leaves by name.
5. Add this block to the project `CLAUDE.md` (create the file if missing):

```markdown
## Active Campaign
Campaign state lives in `docs/campaign-hq/`. Before doing project work, read
CAMPAIGN.md (plan), LEARNINGS.md (history), and preferences.md (worker routing).
Act as orchestrator: dispatch workers per preferences.md rather than
implementing directly. Doctrine: the campaign-conductor skill.
```

After bootstrap, the campaign folder is the source of truth. Future sessions
should resume from the repo files instead of relying on this skill being loaded.

## Preflight

Run preflight once at kickoff and record the result in `preferences.md`:

- Codex CLI: `codex --version`, `codex login status`, and the default-model
  smoke test in [Codex dispatch](references/codex-dispatch.md)
- Other agent CLIs when the user has them: `agy --version`, `grok --version`,
  `muse --version`
- GitHub CLI when CI gates matter: `gh auth status`
- Project verification command: run the actual build/test/lint command workers
  will use
- Permission envelope: Codex sandbox/network/approval policy and Claude worker
  edit permissions

Route around missing tools rather than discovering them mid-wave. If Codex is
unavailable, use Claude-only fleets: Opus 5.5 workers at medium effort implement, while Fable 5.1
or Opus 5.5 keeps planning, design judgment, integration, and review.

## Plan The Campaign

Auto-size the campaign:

- Small or familiar repo: write `CAMPAIGN.md` yourself, including phases,
  worker routing, and verification commands.
- Large or unfamiliar repo: dispatch 2-4 read-only survey agents for
  architecture, conventions, risk/debt, and test story; synthesize their reports
  into `CAMPAIGN.md` and get user sign-off before writer waves.

Use phases shaped as `dispatch -> collect -> integrate -> verify -> next wave`.
Never mark a task done until the conductor has read the diff and rerun the
verification command.

## Worker Routing

Precedence is: user's live instruction > `preferences.md` > these defaults.
When the user states a routing preference, write it to `preferences.md` in the
same turn.

Model, worker, and effort requests are routing preferences. Do not silently
replace a live request like "use low reasoning Codex for this wave" or "send
tests to Opus" with a default. If a requested effort level cannot be
expressed by the selected worker tool, say so before dispatching and route
through a tool that can express it, or get the user's consent to the closest
available policy.

| Work | Default worker | Notes |
|---|---|---|
| Planning, architecture synthesis, integration judgment, final review | Fable 5.1 conductor at high; Opus 5.5 at high when Fable is unavailable | Keep this in the main session unless a parallel survey helps. |
| Implementation, refactors, tests, scripts, debugging | Codex CLI on `gpt-6-sol` at `high` | The worker sizes its own fan-out: alone, or up to five leaves. Read [Codex dispatch](references/codex-dispatch.md) first. |
| Judgment leaf work inside a Sol fan-out | `feature` role: `gpt-6-sol` at `high` | A sub-feature, bug fix, or test suite with a clear file boundary. |
| Second opinion inside a Sol fan-out | `critic` role: `gpt-6-sol` at `medium`, read-only by role file | Reviews a sibling leaf's diff in a fresh session. |
| Mechanical leaf work inside a Sol fan-out | `grunt` role: `gpt-6-luna` at `max` | Fixtures, renames, search, small tests. Move a task that fails verification twice to `feature`. |
| UI/UX, visual design, design review, frontend polish | Claude Opus 5.5 at high | Workflow `agent()` accepts a per-agent `effort` parameter (this skill counts as the Workflow opt-in); the Agent tool inherits the session's effort. |
| Cohesive sub-goal that needs its own integration branch or mid-flight steering | Claude Opus 5.5 squad lead at high, running Sol workers | SendMessage steers a running lead. See [Squads](references/squads.md). |
| Consultation: architecture questions, read-only review of a Claude worker's diff | Codex CLI on `gpt-6-sol` at `high`, read-only | See [Review gates](references/review-gates.md). |
| Bake-off judging, final arbitration between a critic and an author | Codex CLI on `gpt-6-sol` at `xhigh`, read-only | Give it diffs and verification output, with criteria set before dispatch. |
| Read-only surveys, code search, research scouting | Claude Opus 5.5 at medium, or Codex CLI on `gpt-6-luna` at `max` read-only (`-c web_search=live` for research) | Require file/line evidence. |
| Rare, very hard question on explicit user request | Codex CLI on `gpt-6-astra` at `max`, read-only | Never a default and never a writer. Record the request in the fleet table. |
| Second opinions from another model family | `agy` on `gemini-3.8-flash-high`, `grok` on `grok-4.7` at `xhigh`, or `muse` on `muse-spark-1.3-contributor` at `max` | Optional, read-only, roughly Luna-tier. See [Review gates](references/review-gates.md). |
| Codex unavailable or rate-limited | Claude Opus 5.5 workers at medium, Opus 5.5 at high for design | Keep the same briefs, worktree isolation, report schema, and verification gates. |

Opus 5.5 at medium effort needs a Workflow `agent()` call with `effort:
'medium'`; an Agent-tool subagent inherits the session's effort.

`ultra` effort adds automatic delegation. Use it only on an explicit request,
and never for a leaf, a consultant, or the Astra run.

## Dispatch Rules

- Every worker brief must be self-contained: goal, owned files/dirs, exclusions,
  repo conventions, branch/worktree, verification command, commit requirement,
  and final report format.
- One writer per tree. Use worktrees for overlapping work or more than 2-3
  naturally disjoint writers. See [Fleet operations](references/fleet-operations.md).
- Every writer branch must end with a commit. Uncommitted worker output is
  invisible to integration.
- Record each active dispatch in the `CAMPAIGN.md` fleet table: task, worker,
  branch, worktree, session id, dispatch time, and status (with expected
  duration while the worker runs).
- Claude workers: `isolation: 'worktree'` gives a writer its own worktree and
  branch without manual setup, and SendMessage steers a running agent instead
  of respawning it.
- A Sol worker's leaf fan-out needs no squad: it happens inside one worktree
  and returns one commit. Use an Opus squad only for cohesive sub-goals where
  several Sol workers must integrate before the conductor needs the result.
  See [Squads](references/squads.md).

## Collect, Verify, Record

The conductor owns correctness:

- Parse each worker report, then inspect the actual diff and rerun the stated
  verification command.
- Integrate branches in dependency order. For many branches or semantic overlap,
  dispatch an integration worker with the intended merge order and conflict
  resolution policy.
- Use cross-model review for high-risk diffs and after wave integration. See
  [Review gates](references/review-gates.md).
- Update `CAMPAIGN.md` task status as work lands.
- Log durable lessons in `LEARNINGS.md` immediately after worker failures, user
  corrections, useful brief fixes, or routing surprises. Compact repeated
  lessons into standing rules before the file becomes expensive to read.
- Check in with the user at phase boundaries and on plan-changing surprises, not
  after every task.

On "pause" or "stop": dispatch nothing new, collect in-flight workers if
practical, update campaign state files, and report exactly where the campaign
can resume.
