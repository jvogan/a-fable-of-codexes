# Worker Routing Preferences
<!-- Precedence: user's live instruction > this file > skill defaults.
     Update this file whenever the user states a preference. -->
- Conductor: Fable when available, otherwise Claude Opus at high effort
- UI/UX, design, integration judgment: Claude Opus, high effort
- Implementation, tests, research, mechanical refactors: Codex CLI when available
- Codex unavailable: Claude worker agents use the same briefs and report schema
- Model/effort overrides: user's live request wins; record requested worker, model, and reasoning level before dispatch
- Check-in cadence: phase boundaries and plan-changing surprises
- Permission envelope: record Codex sandbox/network/approval policy and Claude worker edit permissions at kickoff
