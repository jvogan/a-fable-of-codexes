# Worker Routing Preferences
<!-- Precedence: user's live instruction > this file > skill defaults.
     Update this file whenever the user states a preference. -->
- Conductor: Claude Fable 5.1 at high effort, or Opus 5.5 at high when Fable is unavailable
- Implementation, tests, debugging, refactors: Codex CLI on gpt-6-sol at high; the worker runs alone or fans out to at most 5 leaves
- Leaves (role files in .codex/agents/): feature (gpt-6-sol, high) for bounded judgment work; critic (gpt-6-sol, medium, read-only) for a second opinion on a sibling's diff; grunt (gpt-6-luna, max) for mechanical work
- UI/UX, design review, squad leads: Claude Opus 5.5 at high; an Opus squad lead dispatches its own Sol workers
- Consultation and review of Claude diffs: Codex CLI on gpt-6-sol at high, read-only. Bake-off judging and arbitration: gpt-6-sol at xhigh, read-only
- Read-only surveys and research scouts: Claude Opus 5.5 at medium effort, or gpt-6-luna at max read-only
- gpt-6-astra at max: only on an explicit user request for a rare, very hard question; read-only
- Other-family second opinions (optional, read-only): agy on gemini-3.8-flash-high, grok on grok-4.7 at xhigh, muse on muse-spark-1.3-contributor at max
- Implementation when Codex is unavailable: Claude Opus 5.5 at medium effort
- Model/effort overrides: user's live request wins; record requested worker, model, and reasoning level before dispatch
- Check-in cadence: phase boundaries and plan-changing surprises
- Permission envelope: record Codex sandbox/network/approval policy and Claude worker edit permissions at kickoff
