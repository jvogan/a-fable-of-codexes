# Worker Routing Preferences
<!-- Precedence: user's live instruction > this file > skill defaults.
     Update this file whenever the user states a preference. -->
- Conductor: Claude Fable 5.1, or Opus 5 at high effort when Fable is unavailable
- Implementation, tests, research, mechanical refactors: Codex CLI on gpt-5.6-sol at high effort; the worker sizes its own fan-out
- Codex leaves when a worker fans out: terra role (gpt-5.6-terra, xhigh) for work needing design care; luna role (gpt-5.6-luna, max) for throughput
- UI/UX, design, design review, integration judgment: Claude Opus 5, high effort
- Read-only surveys, quick search, implementation when Codex is unavailable: Claude Sonnet 5
- Third-model review, scouting, second opinions: Antigravity CLI (agy) on gemini-3.7-flash-high, read-only
- Model/effort overrides: user's live request wins; record requested worker, model, and reasoning level before dispatch
- Check-in cadence: phase boundaries and plan-changing surprises
- Permission envelope: record Codex sandbox/network/approval policy and Claude worker edit permissions at kickoff
