# Worker Routing Preferences
<!-- Precedence: user's live instruction > this file > skill defaults.
     Update this file whenever the user states a preference. -->
- Conductor: Fable 5.1, or Opus 5 at high effort when Fable is unavailable
- Implementation, tests, research: codex on gpt-6-astra at medium effort; fan out only when the task splits
- Codex leaves when it fans out: feature (astra, medium) for engine and tokenizer work; grunt (luna, xhigh) for fixtures and mechanical edits; critic (astra, high) on the engine diff
- Consultation: codex on gpt-6-astra at high, read-only; used for the index layout question
- UI/UX, design: claude opus 5, high effort
- Quick search and read-only surveys: claude sonnet 5
- Other-family review: agy on gemini-3.8-flash-high, read-only; used on the ranking diff
- Integration: opus 5 for UI-adjacent merges, codex for mechanical merges
- Model/effort overrides: user's live request wins; record requested worker, model, and reasoning level before dispatch
- Check-in cadence: phase boundaries; ping immediately if the index size budget fails
- Permission envelope: codex workspace-write with network on (npm installs); claude workers with edits pre-accepted
