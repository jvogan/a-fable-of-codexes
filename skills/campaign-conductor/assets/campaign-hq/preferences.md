# Worker Routing Preferences
<!-- Precedence: user's live instruction > this file > skill defaults.
     Update this file whenever the user states a preference. -->
- Conductor: Claude Fable 5.1, or Opus 5 at high effort when Fable is unavailable
- Implementation, tests, research, mechanical refactors: Codex CLI on gpt-6-astra at high effort; the worker sizes its own fan-out. Fallback while Astra is unavailable on the account: gpt-5.6-sol at high
- Codex leaves when a worker fans out: astra role (gpt-6-astra, medium) for work needing design care; terra role (gpt-5.6-terra, xhigh) for everyday work; luna role (gpt-5.6-luna, xhigh) for throughput; sol role (gpt-5.6-sol, high) for a second opinion
- Consultation (architecture questions, design second opinions, read-only review of Claude diffs): Codex CLI on gpt-6-astra at xhigh, read-only
- UI/UX, design, design review, integration judgment: Claude Opus 5, high effort
- Read-only surveys, quick search, implementation when Codex is unavailable: Claude Sonnet 5
- Review, scouting, second opinions from another model family: agy on gemini-3.8-flash-high, grok on grok-4.6 at high, or muse on muse-spark-1.3-contributor at xhigh; read-only
- Model/effort overrides: user's live request wins; record requested worker, model, and reasoning level before dispatch
- Check-in cadence: phase boundaries and plan-changing surprises
- Permission envelope: record Codex sandbox/network/approval policy and Claude worker edit permissions at kickoff
