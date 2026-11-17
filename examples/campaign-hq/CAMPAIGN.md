# Campaign: docs-search
Goal: Add client-side full-text search to the documentation site with a keyboard-driven UI.
Status: phase 2 of 3: index pipeline merged; UI and highlighting in flight.

## Phases

### Phase 1: Index pipeline (done)
- [x] Build-time indexer emitting `search-index.json` - worker: codex sol - verify: `npm run build && node scripts/check-index.mjs`
- [x] Tokenizer handling code identifiers (camelCase, snake_case) - worker: codex sol - verify: `npm test -- tokenizer`
- [x] Heading-anchor audit across all docs sections - worker: codex terra sweep (12 scouts at xhigh, one per section) - verify: every heading in the report has a file and line

### Phase 2: Search UI
- [x] Query engine with ranking (title > heading > body) - worker: codex sol (feature + grunt leaves, critic on the engine diff) - verify: `npm test -- ranking`
- [ ] Search palette component (Cmd-K, keyboard navigation) - worker: opus 5.5 - verify: `npm test -- palette` + visual review
- [ ] Result highlighting and deep links to headings - worker: codex sol - verify: `npm test -- highlight`

### Phase 3: Integration
- [ ] Merge phase-2 branches, wire palette to engine - worker: opus 5.5 (integration) - verify: `npm test && npm run e2e`
- [ ] Index size budget check in CI (< 250 KB gzipped) - worker: codex sol - verify: CI green on PR

## Fleet (active dispatches)
| Task | Worker | Branch | Worktree | Session | Dispatched | Status |
|---|---|---|---|---|---|---|
| Search palette | opus 5.5 | campaign/palette | ../wt-palette | agent:palette | 13:58 | in progress, ~45 min expected |
| Result highlighting | codex sol | campaign/highlight | ../wt-highlight | 019826f3-…-8b2c | 14:05 | running, ~30 min expected |
| Ranking engine | codex sol (3 leaves: feature, grunt, critic) | campaign/ranking | (removed) | 0197f1aa-…-42d1 | 11:20 | merged, verified, worktree removed |
