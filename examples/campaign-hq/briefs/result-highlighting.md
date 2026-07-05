# Brief: result highlighting

Goal: highlight matched terms in search results and deep-link each result to
its heading anchor.

Branch: `campaign/highlight`, worktree `../wt-highlight`, base commit `3f2a91c`.

Files you own: `src/search/highlight.ts`, `src/search/anchors.ts`, and their
test files. Do not touch `src/search/palette/` (a sibling worker owns it this
wave) or `src/search/engine.ts` (merged last wave; consume its API as is).

Conventions: named exports only; tests colocated as `*.test.ts`; no new
dependencies.

Verify: `npm test -- highlight` from the worktree root. All tests must pass
before you commit.

Commit your work on this branch with message `campaign/highlight: <summary>`.

Do not spawn subagents; this task is sized for one worker.

Report per the output schema: status, branch, commit, files_changed,
verify_cmd, verify_result, blockers.
