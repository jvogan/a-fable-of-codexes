# Squads

Read this only when a phase contains a cohesive sub-goal that needs nested
delegation.

## When To Use A Squad

A Sol worker's leaf fan-out is not a squad: it runs inside one worktree and
returns one commit, and the conductor dispatches it like any worker.

Use a squad when several Sol workers must integrate with each other before the
conductor needs the result, when the sub-goal needs design judgment or
mid-flight steering, or when verification is expensive enough that it should
run once at the sub-goal boundary.

Use flat dispatch when tasks can land directly on the campaign main line.
Without intermediate integration, a squad only adds reporting overhead.

## Shape

A squad is one Claude Opus 5.5 lead at high effort that:

1. Receives a sub-goal and namespace from the conductor.
2. Dispatches Sol workers with `codex exec`, one worktree each. Each Sol worker
   may fan out to at most five leaves inside its own worktree.
3. Integrates the Sol branches into one squad integration branch.
4. Runs the squad verification command.
5. Reports one structured result to the conductor.

The conductor merges the squad integration branch later. The squad never merges
to main.

Any worker that can dispatch, integrate, and verify can lead. Opus 5.5 is the
default because squad leads make integration and design calls; drop the lead
to medium effort for a mechanical sub-goal.

## Hard Rules

- Depth caps at three below the conductor: conductor -> Opus lead -> Sol
  workers -> leaves. A Sol worker the conductor dispatches directly has two
  levels: worker -> leaves.
- Only Sol workers spawn leaves. Leaf briefs and role files forbid further
  spawning; Codex workers carry the native spawn tools (nested `codex exec`
  processes are sandbox-blocked; the native tools are not), so the rule has to
  be stated.
- Every lead brief caps concurrent Sol workers, and every Sol brief caps
  concurrent leaves at five.
- Branches and worktrees stay inside the squad namespace.
- The squad lead verifies the integrated branch before reporting.
- The conductor reruns verification when merging the squad branch.
- One conductor fleet-table row tracks the squad integration branch.
- The squad report must enumerate every Sol worker with status, commit sha,
  leaf count, and verification evidence.
- Squads live for one wave and clean up worker worktrees before reporting.

## Namespaces

Assign an exclusive prefix:

- Squad integration branch: `campaign/<squad>`
- Sol worker branches: `campaign/<squad>/<subtask>`
- Sol worker worktrees: `../wt-<squad>-<subtask>`

The brief must forbid branches or paths outside the prefix.

## Squad Lead Brief

Include:

- Sub-goal
- Sibling squads and file boundaries
- Base commit
- Namespace prefix
- Decomposition, or explicit authority to decompose
- Sol worker cap, and the five-leaf cap each Sol brief must carry
- Sol brief requirements (the Codex dispatch brief contract)
- Verification command
- Stop-at-integration-branch rule
- Worktree cleanup requirement
- Report schema

Squad leads orchestrate. They may resolve small merge conflicts, but they should
not write feature code.
