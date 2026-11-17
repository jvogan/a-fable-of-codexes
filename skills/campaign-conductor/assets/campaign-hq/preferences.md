# Worker Routing Preferences
<!-- Precedence: user's live instruction > this file > skill defaults.
     Update this file whenever the user states a preference. -->
- Conductor: Claude Fable 5.2 at high effort, or Opus 5.5 at high when Fable is unavailable or the user chooses it
- Implementation, tests, debugging, refactors: Codex CLI on gpt-6.2-sol at high; the worker runs alone or fans out one leaf per disjoint file group
- Leaves (role files in .codex/agents/): feature (gpt-6.2-sol, high) for bounded judgment work; critic (gpt-6.2-sol, high, read-only) for a second opinion on a sibling's diff; grunt (gpt-6.1-terra, xhigh) for mechanical work
- UI/UX, design review, squad leads: Claude Opus 5.5 at high, or xhigh for hard calls; an Opus squad lead dispatches its own Sol workers
- Consultation and review of Claude diffs: Codex CLI on gpt-6.2-sol at high, read-only. Bake-off judging and arbitration: gpt-6.2-sol at xhigh, read-only
- Read-only surveys and research scouts: Claude Sonnet 5.5 at high (xhigh for hard tasks), or one gpt-6.1-terra scout at max read-only
- Quick lookups (definitions, call sites, event-stream errors): Claude Haiku 5.5 at high, read-only
- Bulk read-only sweeps: many gpt-6.1-terra scouts at xhigh in parallel, one per package, file group, or question
- gpt-6.2-astra at max: only on an explicit user request for a rare, very hard question; read-only
- Other-family second opinions (optional, read-only): agy on gemini-3.8-flash-high, grok on grok-4.7 at xhigh, muse on muse-spark-1.3-contributor at max
- Implementation when Codex is unavailable: Claude Sonnet 5.5 at high or xhigh; Opus 5.5 at high or xhigh for design and for tasks that fail twice on Sonnet
- Verification: conductor reads high-risk diffs and reruns verification on every integrated result; routine branches go through a non-author integration or verifier worker
- Effort floor: high; no worker, leaf, subagent, or fallback runs at medium or lower
- Model/effort overrides: user's live request wins; record requested worker, model, and reasoning level before dispatch
- Check-in cadence: phase boundaries and plan-changing surprises
- Permission envelope: record Codex sandbox/network/approval policy, Codex project trust, and Claude worker edit permissions at kickoff
- Preflight: record CLI versions, login status, reachable Codex models, and the verification command result at kickoff
