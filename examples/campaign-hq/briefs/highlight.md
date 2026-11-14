# Brief: result highlighting

Goal: highlight matched terms in search results and deep-link each result to
its heading anchor.

Done when: every result links to an anchor that exists on its page, and
highlighting changes nothing in a result except the highlight markup.

Input: the heading-anchor audit found 31 headings without stable anchors.
`anchors.ts` must derive a stable anchor for each.

Branch: `campaign/highlight`, worktree `../wt-highlight`, base commit `3f2a91c`.

Files you own: `src/search/highlight.ts`, `src/search/anchors.ts`, and their
test files. Do not touch `src/search/palette/` (a sibling worker owns it this
wave) or `src/search/engine.ts` (merged last wave; consume its API as is).

Conventions: named exports only; tests colocated as `*.test.ts`; no new
dependencies.

Verify: `npm test -- highlight` from the worktree root. All tests must pass
before you report.

Leave your changes uncommitted and list every changed path in the report. The
conductor commits them as `campaign/highlight: <summary>`.

Do not spawn subagents; this task is sized for one worker.

Report per the output schema: status, branch, commit, files_changed,
verify_cmd, verify_result, blockers.
