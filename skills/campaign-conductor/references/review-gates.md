# Review Gates

Read this when collecting worker outputs, integrating a wave, handling risky
diffs, or pausing a campaign.

## Report Schemas

Bootstrap copies two schemas into `schemas/` in the campaign folder:

- `worker-result.json`, for writers and integration workers: `status`,
  `branch`, `commit` (empty when the collector commits), `files_changed`,
  `verify_cmd`, `verify_result` with `passed` and `output_tail`, and
  `blockers`.
- `scout-result.json`, for read-only scouts and sweeps: `status`, `summary`,
  `findings` (each with `claim`, `file`, and `line`), and `blockers`.

A Codex writer or scout dispatch must pass its schema:

```bash
--output-schema docs/campaign-hq/schemas/worker-result.json
--output-schema docs/campaign-hq/schemas/scout-result.json
```

A Claude worker must end with a fenced JSON block matching its schema.

## Cross-Model Review

Author and reviewer must be separate. The reviewing families are Claude and
Codex, plus Gemini, Grok, and Muse through their OAuth-backed CLIs.

- After a Codex worker returns a high-risk diff, dispatch a Claude Opus 5.5
  reviewer or a review from one of the other CLIs.
- After a Claude worker returns a high-risk diff, run a Codex consultation:
  read-only on `gpt-6.2-sol` at `high`.
- After each wave integration, review the merged result to catch semantic
  conflicts that appear only after individually valid branches combine.

High-risk means auth, permissions, billing, data migration, shared state,
security boundaries, persistent storage, or broad refactors.

A Codex consultation is also the shape for architecture questions:

```bash
codex exec -s read-only -m gpt-6.2-sol -c model_reasoning_effort=high \
  -C "$PWD" - < docs/campaign-hq/briefs/<task>.md
```

Inside a Sol fan-out, a `critic` leaf (Sol at `high`, read-only by role file)
runs the same review. `codex exec review --base <ref>` runs the built-in review
flow and takes the same `-m` and `-c` flags. Keep the consultant off `ultra`:
that tier delegates on its own, and a consultation is one model reading and
advising.

When the user explicitly asks for an exceptional effort on a rare, very hard
question, run the same command with
`-m gpt-6.2-astra -c model_reasoning_effort=max`. Give Astra the question, the
relevant files, and the conductor's current answer, and ask for an independent
answer with its reasoning and every obstacle it could not resolve. The
conductor weighs both; Astra's answer does not override verification.

For a read-only review from another model family, use whichever CLI the user
has. These reviewers are optional; use them only as a secondary review from a
different model family:

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
because the tier is part of the slug. `muse` keeps its sandbox and approval
prompts on by default, and its headless options go after `exec`. Close stdin
with `< /dev/null` on headless `grok` and `muse` runs: from a backgrounded
shell they can otherwise exit with no output. Check each CLI's `--help` for
the installed version.

Without a second model available, substitute a fresh reviewer agent that did
not author the diff.

## Bake-Offs

For a high-stakes task with uncertain solution shape, dispatch the same brief,
with each worker's commit rule, to two workers in separate worktrees. Pair
model families by default: Codex on
`gpt-6.2-sol` against Claude Opus 5.5. Give a judge explicit criteria before
dispatch, correctness first. The judge is the conductor, or a read-only Codex
arbiter on `gpt-6.2-sol` at `xhigh`:

```bash
codex exec -s read-only -m gpt-6.2-sol -c model_reasoning_effort=xhigh \
  -C "$PWD" - < docs/campaign-hq/briefs/<task>-judge.md
```

Give the judge diffs, verification output, and screenshots rather than worker
summaries.

Use bake-offs sparingly because they double worker usage and add judge time.

## Verification

After every worker return:

1. Parse the report, and commit a Codex worker's reported changes.
2. Have an agent that did not write the change inspect its diff: the conductor
   for high-risk or design-heavy work, otherwise an integration worker or a
   verifier from another model family (Sonnet 5.5 for Codex branches, Sol for
   Claude branches).
3. Rerun the verification command from the brief.
4. Update `CAMPAIGN.md`.
5. Record durable lessons in `LEARNINGS.md` per the Campaign Memory rules.

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
