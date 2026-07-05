# Worker Routing Preferences
<!-- Precedence: user's live instruction > this file > skill defaults.
     Update this file whenever the user states a preference. -->
- UI/UX, design: claude opus, high effort
- Conductor: Fable when available, otherwise claude opus at high effort
- Implementation, tests, research: codex CLI when available; split waves across configured accounts only within current usage limits
- Model/effort overrides: user's live request wins; record requested worker, model, and reasoning level before dispatch
- Quick search: native subagents
- Integration: opus for UI-adjacent merges, codex for mechanical merges
- Check-in cadence: phase boundaries; ping immediately if the index size budget fails
- Permission envelope: codex workspace-write with network on (npm installs); claude workers with edits pre-accepted
