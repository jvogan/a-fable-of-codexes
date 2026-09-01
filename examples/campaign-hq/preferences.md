# Worker Routing Preferences
<!-- Precedence: user's live instruction > this file > skill defaults.
     Update this file whenever the user states a preference. -->
- Conductor: Fable 5.1, or Opus 5 at high effort when Fable is unavailable
- Implementation, tests, research: codex on gpt-5.6-sol at high effort; fan out only when the task splits
- Codex leaves when it fans out: terra (xhigh) for engine and tokenizer work; luna (max) for fixtures and mechanical edits
- UI/UX, design: claude opus 5, high effort
- Quick search and read-only surveys: claude sonnet 5
- Third-model review: agy on gemini-3.7-flash-high, read-only; used on the ranking diff
- Integration: opus 5 for UI-adjacent merges, codex for mechanical merges
- Model/effort overrides: user's live request wins; record requested worker, model, and reasoning level before dispatch
- Check-in cadence: phase boundaries; ping immediately if the index size budget fails
- Permission envelope: codex workspace-write with network on (npm installs); claude workers with edits pre-accepted
