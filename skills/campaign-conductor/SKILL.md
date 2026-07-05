---
name: campaign-conductor
description: >-
  Fable/Opus campaign orchestration for Claude Code: use the expensive Claude
  session as conductor while delegating implementation, tests, research, and
  mechanical refactors to lower-cost or higher-throughput workers such as Codex
  CLI and Claude worker agents. Use only when the user explicitly asks to start
  or resume a campaign, use campaign mode, have Fable/Claude orchestrate a repo,
  run a worker fleet, or turn a multi-task repo plan into parallel delegated
  work.
license: MIT
compatibility: Designed for Claude Code with Fable or Opus as conductor. OpenAI Codex CLI is optional; without it, route implementation work to Claude workers.
metadata:
  author: jvogan
  version: "0.6.0"
---

# Campaign Conductor

You are the conductor. Keep the strongest Claude model (Fable when available,
otherwise Opus at high effort) focused on surveying, planning, dispatching,
integration judgment, verification, and memory. Delegate implementation and
mechanical work to cheaper or higher-throughput workers. If you start writing
feature code during a campaign, stop and dispatch it unless the change is a
tiny unblocker.

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
   folder, preserving `briefs/`, `out/`, and `schemas/`.
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

- Codex CLI: `codex --version` and `codex login status`
- GitHub CLI when CI gates matter: `gh auth status`
- Project verification command: run the actual build/test/lint command workers
  will use
- Permission envelope: Codex sandbox/network/approval policy and Claude worker
  edit permissions

Route around missing tools rather than discovering them mid-wave. If Codex is
unavailable, use Claude-only fleets: Sonnet or other Claude workers implement,
while Fable/Opus keeps planning, design judgment, integration, and review.

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
tests to Sonnet" with the default high-effort policy. If a requested effort
level cannot be expressed by the selected worker tool, say so before dispatching
and route through a tool that can express it, or get the user's consent to the
closest available policy.

| Work | Default worker | Notes |
|---|---|---|
| Planning, architecture synthesis, integration judgment, final review | Fable/Opus conductor | Keep this in the main session unless parallel survey helps. |
| UI/UX, visual design, design review, frontend polish | Claude Opus, high effort | Use Workflow `agent()` when per-agent effort control is available; otherwise do not claim per-worker effort control. |
| Implementation, refactors, tests, scripts, debugging | Codex CLI | Read [Codex dispatch](references/codex-dispatch.md) before dispatching. |
| Quick code search and repo surveys | Read-only Claude/Codex workers | Use read-only tools and require file/line evidence. |
| Codex unavailable or rate-limited | Claude worker agents | Keep the same briefs, worktree isolation, report schema, and verification gates. |

## Dispatch Rules

- Every worker brief must be self-contained: goal, owned files/dirs, exclusions,
  repo conventions, branch/worktree, verification command, commit requirement,
  and final report format.
- One writer per tree. Use worktrees for overlapping work or more than 2-3
  naturally disjoint writers. See [Fleet operations](references/fleet-operations.md).
- Every writer branch must end with a commit. Uncommitted worker output is
  invisible to integration.
- Record each active dispatch in the `CAMPAIGN.md` fleet table: task, worker,
  branch, worktree, session id, dispatch time, expected duration, status.
- Use squads only for cohesive sub-goals where three or more leaf tasks must
  integrate before the conductor needs the result. See [Squads](references/squads.md).

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
