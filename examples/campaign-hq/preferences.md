# Worker Routing Preferences
<!-- Precedence: user's live instruction > this file > skill defaults.
     Update this file whenever the user states a preference. -->
- Conductor: Fable 5.1 at high, or Opus 5.5 at high when Fable is unavailable
- Implementation, tests, research: codex on gpt-6-sol at high; fan out to leaves only when the task splits (max 5)
- Leaves: feature (sol, high) for the ranking engine; grunt (luna, max) for fixtures and mechanical edits; critic (sol, medium) on the engine diff
- Consultation: codex on gpt-6-sol at high, read-only; used for the index layout question
- UI/UX, design: claude opus 5.5, high effort
- Quick search and read-only surveys: claude opus 5.5, medium effort
- gpt-6-astra at max: not used this campaign (explicit request only)
- Other-family review: agy on gemini-3.8-flash-high, read-only; used on the ranking diff
- Integration: opus 5.5 for UI-adjacent merges, codex sol for mechanical merges
- Model/effort overrides: user's live request wins; record requested worker, model, and reasoning level before dispatch
- Check-in cadence: phase boundaries; ping immediately if the index size budget fails
- Permission envelope: codex workspace-write with network on (npm installs); claude workers with edits pre-accepted
