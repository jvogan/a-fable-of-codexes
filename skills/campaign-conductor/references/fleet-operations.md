# Fleet Operations

Read this when more than one writer is active, when work may overlap, or when a
wave must be integrated.

## Invariant

One writer per tree. Shared-tree writes are acceptable only for 2-3 workers with
naturally disjoint file boundaries. Anything larger or overlapping gets one git
worktree and branch per worker.

## Worktree Pattern

Create worktrees from a clean base:

```bash
git status --short
git rev-parse HEAD
git worktree add ../wt-<task> -b campaign/<task>
```

Each writer brief must state:

- Base commit
- Branch name
- Worktree path
- Owned files
- Excluded files
- Verification command
- Required commit message: `campaign/<task>: <summary>`

Uncommitted worker output is not ready for integration.

## Fleet Table

Record every active dispatch in `CAMPAIGN.md`:

| Task | Worker | Branch | Worktree | Session | Dispatched | Status |
|---|---|---|---|---|---|---|

Status should include expected duration for running workers. A worker whose
output file is empty past roughly 3x expected duration is stalled: stop it,
inspect its worktree, then resume or redispatch.

## Waves

Structure large campaigns as waves:

1. Dispatch from the current integrated base.
2. Collect worker reports.
3. Inspect diffs and rerun worker verification commands.
4. Integrate branches in dependency order.
5. Run the decisive project verification command.
6. Update campaign files.
7. Start the next wave from the integrated result.

Size a writer wave by how its branches will be verified and integrated, not
by a fixed count. Branches the conductor reviews itself keep a wave to what it
can read. Branches routed through integration and verifier workers let a wave
run as wide as disjoint file ownership and the account's rate limits allow.
Read-only scouts and reviewers fan out wider still because they create no merge
debt.

Do not stack new writer work on unintegrated branches unless the dependency is
explicit. That compounds conflicts and makes verification ambiguous.

## Integration Routing

Merge 1-3 small, independent branches yourself and run tests between merges.

Dispatch an integration worker when there are many branches or semantic overlap.
The integration brief must include:

- Branch list
- Merge order
- Conflict-resolution policy
- Files or subsystems each branch owns
- Full verification command
- Instruction to read each branch's diff against its brief and report defects
  with file and line
- Rule that the integration branch stops before merging to main

Route integration by judgment required: Fable 5.1 or Opus 5.5 for design or
product tradeoffs, a Sol worker for mechanical large-scale reconciliation.

## Cleanup

After integration:

```bash
git worktree remove ../wt-<task>
git branch -d campaign/<task>
```

Use `git worktree list` to find stale worktrees, but trust `CAMPAIGN.md` for
purpose and status. Update the fleet table when a worktree is merged and
removed.
