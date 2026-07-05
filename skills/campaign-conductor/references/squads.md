# Squads

Read this only when a phase contains a cohesive sub-goal that needs nested
delegation.

## When To Use A Squad

Use a squad when three or more leaf tasks must integrate with each other before
the conductor needs the result, or when verification is expensive enough that it
should run once at the sub-goal boundary.

Use flat dispatch when tasks can land directly on the campaign main line.
Without intermediate integration, a squad only adds reporting overhead.

## Shape

A squad is one lead worker that:

1. Receives a sub-goal and namespace from the conductor.
2. Dispatches leaf workers.
3. Integrates leaf branches into one squad integration branch.
4. Runs the squad verification command.
5. Reports one structured result to the conductor.

The conductor merges the squad integration branch later. The squad never merges
to main.

## Hard Rules

- Depth caps at two: conductor -> squad lead -> leaves.
- Leaf briefs must forbid spawning subagents.
- Every lead brief must include a hard cap on concurrent leaves.
- Branches and worktrees stay inside the squad namespace.
- The squad lead verifies the integrated branch before reporting.
- The conductor reruns verification when merging the squad branch.
- One conductor fleet-table row tracks the squad integration branch.
- The squad report must enumerate every leaf with status, commit sha, and
  verification evidence.
- Squads live for one wave and clean up leaf worktrees before reporting.

## Namespaces

Assign an exclusive prefix:

- Squad integration branch: `campaign/<squad>`
- Leaf branches: `campaign/<squad>/<subtask>`
- Leaf worktrees: `../wt-<squad>-<subtask>`

The brief must forbid branches or paths outside the prefix.

## Squad Lead Brief

Include:

- Sub-goal
- Sibling squads and file boundaries
- Base commit
- Namespace prefix
- Decomposition, or explicit authority to decompose
- Leaf cap
- Leaf brief requirements
- Verification command
- Stop-at-integration-branch rule
- Worktree cleanup requirement
- Report schema

Squad leads orchestrate. They may resolve small merge conflicts, but they should
not write feature code.
