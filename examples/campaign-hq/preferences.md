# Worker Routing Preferences
<!-- Precedence: user's live instruction > this file > skill defaults.
     Update this file whenever the user states a preference. -->
- Conductor: Fable 5.2 at high, or Opus 5.5 at high when Fable is unavailable or the user chooses it
- Implementation and tests: codex on gpt-6.1-sol at high; fan out to leaves only when the task splits
- Leaves: feature (sol, high) for the ranking engine; grunt (luna, xhigh) for fixtures and mechanical edits; critic (sol, high) on the engine diff
- Consultation: codex on gpt-6.1-sol at high, read-only; used for the index layout question
- UI/UX, design: claude opus 5.5, high effort; xhigh for hard design calls
- Quick search and read-only surveys: claude sonnet 5.5, high effort
- Bulk read-only sweeps: codex luna at xhigh, one scout per docs section for the heading-anchor audit
- gpt-6-astra at max: not used this campaign (explicit request only)
- Other-family review: agy on gemini-3.8-flash-high, read-only; used on the ranking diff
- Integration: opus 5.5 at high for UI-adjacent merges, sonnet 5.5 at high for mechanical merges
- Verification: conductor reads the ranking and UI diffs itself; mechanical branches verified by the integration worker
- Effort floor: high; no worker, leaf, subagent, or fallback runs at medium or lower
- Model/effort overrides: user's live request wins; record requested worker, model, and reasoning level before dispatch
- Check-in cadence: phase boundaries; ping immediately if the index size budget fails
- Permission envelope: codex workspace-write with network on (npm installs) and approval_policy=never; claude workers with edits pre-accepted
- Preflight: codex-cli 0.169.0, login ok; gpt-6.1-sol and gpt-6-luna reachable; agy and gh ok; `npm test` passes on main
