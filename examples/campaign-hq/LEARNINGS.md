# Campaign Learnings

## Standing rules
- Codex briefs must name the exact test command; "run the tests" produced `npm test` at repo root, which skips the workspace packages.
- This repo uses named exports only; state it in every brief. Two workers added default exports before this rule existed.
- Keep Opus visual review in the verify step for UI tasks; it catches spacing and contrast issues the automated tests miss.

## Log
<!-- newest first: date | task | worker | outcome | lesson -->
- 2026-07-04 | ranking engine | codex sol + 3 leaves | verified, merged | brief included fixture data; zero rework
- 2026-07-03 | tokenizer | codex | one retry | first brief omitted snake_case cases; extended fixtures
- 2026-07-03 | indexer | codex | verified, merged | clean run
- 2026-07-02 | heading-anchor audit | codex terra sweep, 12 scouts | done | 31 headings lacked stable anchors; the finding went into the highlighting brief
