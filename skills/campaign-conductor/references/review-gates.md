# Review Gates

Read this when collecting worker outputs, integrating a wave, handling risky
diffs, or pausing a campaign.

## Worker Report Schema

Every worker report must include:

- `status`
- `branch`
- `commit`
- `files_changed`
- `verify_cmd`
- `verify_result` with `passed` and `output_tail`
- `blockers`

Codex workers should use:

```bash
--output-schema docs/campaign-hq/schemas/worker-result.json
```

Claude workers should end with a fenced JSON block matching the same schema.

## Schema Template

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "worker-result",
  "type": "object",
  "required": ["status", "branch", "commit", "files_changed", "verify_cmd", "verify_result", "blockers"],
  "properties": {
    "status": { "enum": ["done", "partial", "blocked", "failed"] },
    "branch": { "type": "string" },
    "commit": { "type": "string", "description": "sha of the final commit; empty if none" },
    "files_changed": { "type": "array", "items": { "type": "string" } },
    "verify_cmd": { "type": "string" },
    "verify_result": {
      "type": "object",
      "required": ["passed", "output_tail"],
      "properties": {
        "passed": { "type": "boolean" },
        "output_tail": { "type": "string" }
      }
    },
    "blockers": { "type": "array", "items": { "type": "string" } }
  },
  "additionalProperties": false
}
```

## Cross-Model Review

Author and reviewer must be separate. Model families that can review: Claude,
Codex, and Gemini, Grok, or Muse through their OAuth-backed CLIs.

- After a Codex worker lands a high-risk diff, dispatch a Claude Opus 5.5
  reviewer or a review from one of the other CLIs.
- After a Claude worker lands a high-risk diff, run a Codex consultation:
  read-only on `gpt-6.1-sol` at `high`.
- After each wave integration, review the merged result to catch semantic
  conflicts that appear only after individually valid branches combine.

High-risk means auth, permissions, billing, data migration, shared state,
security boundaries, persistent storage, or broad refactors.

Codex consultation, also the shape for architecture questions. Inside a Sol
fan-out the same review runs as a `critic` leaf (Sol at `high`), read-only
by role file:

```bash
codex exec -s read-only -m gpt-6.1-sol -c model_reasoning_effort=high \
  -C "$PWD" - < docs/campaign-hq/briefs/<task>.md
```

`codex exec review --base <ref>` runs the built-in review flow and takes the
same `-m` and `-c` flags. Keep the consultant off `ultra`: that tier delegates
on its own, and a consultation is one model reading and advising.

When the user explicitly asks for an exceptional effort on a rare, very hard
question, run the same command with `-m gpt-6-astra -c
model_reasoning_effort=max`. Give it the question, the relevant files, and the
conductor's current answer, and ask for an independent answer with its
reasoning. The conductor weighs both; Astra's answer does not override
verification.

Read-only review from another model family, whichever CLI the user has.
These reviewers are optional and roughly Luna-tier; use them for a different
family's perspective, not as the primary review:

```bash
agy --model gemini-3.8-flash-high --mode plan --sandbox \
  --dangerously-skip-permissions --add-dir "$PWD" --print-timeout 20m \
  -p="<prompt>"

grok -m grok-4.7 --effort xhigh --permission-mode plan --cwd "$PWD" \
  --no-subagents --prompt-file <brief> < /dev/null

muse exec --workspace "$PWD" --trust-workspace \
  --model muse-spark-1.3-contributor --reasoning-effort max \
  --disable-write --prompt-file <brief> < /dev/null
```

For `agy`, attach `-p` to its value with `=` and omit `--effort` in plan mode,
since the tier is part of the slug; a write-mode agent swaps `--mode plan
--sandbox` for `--effort high --mode accept-edits`. `muse` keeps its sandbox
and approval prompts on by default, and its headless options go after `exec`.
Close stdin with `< /dev/null` on headless `grok` and `muse` runs: from a
backgrounded shell they can otherwise exit with no output. Check each CLI's
`--help` for the installed version.

Without a second model available, substitute a fresh reviewer agent that did
not author the diff. Weaker than a different model, still far better than
self-review. Author and reviewer stay separate in every gate.

## Bake-Offs

For a high-stakes task with uncertain solution shape, dispatch the same brief to
two workers in separate worktrees. Pair model families by default: Codex on
`gpt-6.1-sol` against Claude Opus 5.5. Give a judge explicit criteria before
dispatch, correctness first. The judge is the conductor, or a read-only Codex
arbiter on `gpt-6.1-sol` at `xhigh`:

```bash
codex exec -s read-only -m gpt-6.1-sol -c model_reasoning_effort=xhigh \
  -C "$PWD" - < docs/campaign-hq/briefs/<task>-judge.md
```

Give the judge diffs, verification output, and screenshots rather than worker
summaries.

Use bake-offs sparingly because they double worker usage and add judge time.

## Verification

After every worker return:

1. Parse the report.
2. Have an agent that did not write the commit inspect its diff: the conductor
   for high-risk or design-heavy work, otherwise an integration worker or a
   verifier from another model family (Sonnet 5.5 for Codex branches, Sol for
   Claude branches).
3. Rerun the verification command from the brief.
4. Update `CAMPAIGN.md`.
5. Record a durable lesson in `LEARNINGS.md` when the result teaches something.

Re-verify after each merge to the campaign main line and after each squad hands
back an integration branch.

## Campaign Memory

Keep `LEARNINGS.md` cheap to read:

- Put durable rules at the top under `Standing rules`.
- Keep raw log entries newest first.
- Record a lesson in the same turn when the user corrects routing, effort
  policy, check-in cadence, brief quality, integration frequency, or verification
  expectations.
- Record a lesson after any worker failure that changes future briefs or routing.
- When a lesson repeats or the log passes roughly 40 lines, promote durable
  lessons and delete stale raw entries.
- Put routing preferences in `preferences.md`, not `LEARNINGS.md`.
- Overwrite stale preferences instead of appending history.
- A lesson that holds for any project belongs in the skill itself: offer to
  fold it into the user's installed copy, tightening existing text rather than
  appending.

## Pause Or Stop

On "pause" or "stop":

1. Dispatch nothing new.
2. Let in-flight writers finish when practical.
3. If a worker is clearly stalled, stop it and record what was preserved.
4. Collect reports and note uncollected work.
5. Update `CAMPAIGN.md`, `LEARNINGS.md`, and `preferences.md`.
6. Tell the user the exact branch, wave, and task state for resumption.
