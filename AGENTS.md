# Style

- Never use em-dashes (--) in any output. Use commas, periods, semicolons, or parentheses instead.

# Agents

- Always set `model` explicitly; both the Agent tool and Workflow `agent()` inherit the
  session model when omitted, so under an Opus session "omit" silently means Opus. Tier by
  task: `haiku` for mechanical work (exact-text edits, exploration, simple fetches; always
  `haiku` for Explore), `sonnet` for substantive work, `opus` only for genuinely hard tasks,
  never routine.
- Subagents cannot ask questions: make every prompt self-contained (role, exact file paths,
  what to read first, constraints including "no em-dashes (--)", and "locate by content,
  line numbers are approximate").
- For orchestration-heavy sessions (any work that decomposes into delegable units where the
  main thread's context is worth protecting), use `tools/skills/orchestrating-subagents/SKILL.md`,
  preemptively at session start, not once context is already full.
- For Codex model routing, use
  `tools/skills/codex-model-routing/SKILL.md`: Spark for Explore-style
  fan-out, `gpt-5.4-mini` for bounded reliable workers, `gpt-5.4` for substantive work,
  and `gpt-5.5` for main-thread synthesis or genuinely hard judgment.
- In orchestration sessions, be careful with direct reads in the main thread: the point is
  keeping the main context lean. Read only what is necessary; if unsure how large a file or
  output might be, check its length (`wc -l`, `du`) before reading, and delegate bulk
  reading to subagents.

# Learnings

On corrections, surprises, or "remember this": silently spawn a background agent to append a bullet to `## Learned` below. Format: `- {lesson} — discovered {date}`. Project patterns go in `{project}/.Codex/AGENTS.md`, universal prefs in `~/.Codex/AGENTS.md`. No duplicates, no essays, no mention unless asked.

## Learned

- Never add Co-Authored-By: Codex lines to commits — user explicitly does not want CC co-authorship — discovered 2026-02-04
- When writing Alembic migrations with foreign keys, never use inline `sa.ForeignKey()` inside `op.add_column()` — always add the column first, then use `op.create_foreign_key()` separately. In downgrade, `op.drop_constraint()` must come before `op.drop_column()`. Check existing migrations in the project for the correct pattern before writing new ones — discovered 2026-02-06
- Before launching any GPU job on a remote server, check `nvidia-smi` for stale processes, `pkill -f` any zombies, and verify clean memory usage — a crashed CUDA process can leave the GPU in a dirty state that poisons subsequent runs — discovered 2026-02-24
- Type checker passing does not mean things work — always validate by running tests and exercising the actual flow, not just `tsc --noEmit` — discovered 2026-03-22
- User does not want to read long texts: give the information needed to take decisions, nothing more. Short prose, minimal headers, only load-bearing points; no section-by-section briefings, no restatements. When asked for an explanation it is natural to write more, but never more than required — discovered 2026-05-02, refined 2026-06-12
- When a working feature stops producing a downstream effect and no app code changed recently, check infra boundaries FIRST before theorizing about app state (Lambda/App Runner env vars, recent Terraform/CloudFormation/manual infra changes, queue/topic existence, Sentry); "no log line X + handler exits cleanly" usually means a swallowed exception at a boundary (bad queue URL, missing perm, deleted resource), not subtle in-process state. Diff env vars and recent infra applies before reading orchestrator code — discovered 2026-05-08
- When writing academic/technical reports for course assignments, avoid AI-tell phrases: references to course material the professor already knows ("Este es exactamente el modelo X del curso"), unnecessary qualifiers ("conocido en forma cerrada"), generic practical advice the grader knows, meta-commentary ("es la clave para responder esta pregunta"), and "En definitiva" (use "Por lo tanto" instead). State the fact, derive, conclude; no tutorial framing — discovered 2026-05-10
- In autonomous /goal mode with a long-running background task in flight, do not reply to every stop-hook reminder with "End of turn" or a status check; the stop hook fires after every assistant turn and replying creates a tight loop that burns context. Only respond if the task completed, an actionable error appeared, or there is other parallel work to advance. Rely on the harness task-notification or scheduled wakeup, not stop-hook pings — discovered 2026-05-13
- Never close/reopen/merge PRs, delete branches (local or remote), or force-push without explicit per-action approval. Completing an approved task does NOT authorize adjacent cleanup: "create a PR" means create the PR and stop, nothing else. Proposing cleanup is fine; executing it without a yes is not — discovered 2026-06-03
- "Let's consult the advisor first" or similar mid-discussion requests mean do that one step and return to the discussion — not approval to advance the workflow (writing specs, committing, creating deliverables). Wait for an explicit go-ahead before producing artifacts — discovered 2026-06-07
- A question ("How should we enable X?") asks for advice, not execution; providing credentials or access mid-task does not convert it into authorization. Describe the plan and wait for an explicit "do it" before mutating prod or shared systems — discovered 2026-06-10
- On a "Continue from where you left off" prompt (user-sent or harness-injected), never reply "No response requested": restate the current session state and resume the pending work, so the user does not have to repeat the original request — discovered 2026-06-12
- Before producing an assumption-heavy artifact (global AGENTS.md rewrite, architecture spec, analysis script for a paper result), propose the shape in 1-3 lines and wait for a greenlight; when intent is already established, produce it and offer alternatives as a footnote instead of blocking — discovered 2026-06-12
- Absence of an answer is not approval: act only on what the user explicitly confirmed, and leave the rest pending or ask. Never fill silence with a decision because it seems low-risk — discovered 2026-06-12
- Never present a guess as fact: when evidence is absent (e.g. no CI runs found, unknown deploy target), say "I don't know / can't observe this" instead of naming a plausible-sounding platform or cause; a wrong assumption misdirects the user, an honest unknown invites the answer. This includes tool and infrastructure availability: before telling the user something is live (wandb, a dashboard, a log stream), verify the prerequisite actually works (import succeeds, URL resolves, the process is logging) rather than assuming a config flag implies function — discovered 2026-06-12, extended 2026-06-19
- Before sending, posting, pushing, publishing, or deploying to a system other people can see (git remote, LinkedIn/Basecamp/Slack, email, prod), pause, state exactly what the action is, and wait for an explicit yes WHEN that outward action is incidental to, or a continuation of, a broader approved task rather than the thing you were directly told to do. If the user explicitly asked to publish that thing ("post this", "push X"), just do it. Generalizes the 2026-06-03 PR/branch rule to all outward-facing publishing — discovered 2026-06-17
- If an assumption behind an approved plan breaks mid-execution and recovering requires a new outward-facing action (a different push target, an extra deploy, messaging someone), stop and surface the scope change; do not absorb it under the original approval — discovered 2026-06-17
- For non-trivial, well-solved components (BM25, tokenizers, embedding pooling, standard metrics, auth, parsers, date handling), default to a mature existing library instead of implementing from scratch, and surface any reason to roll your own as an explicit tradeoff. General principle across all domains, not ML-specific; not a reason to pull in a dependency for a few trivial lines — discovered 2026-06-17
- When writing marketing/LinkedIn/blog copy for Pento or any company, never invent capabilities, services, or outcomes. Do not assert what the company does for clients or claim results unless the user confirms it is true; inventing a plausible-sounding practice is the same failure as presenting a guess as fact. If a payoff or CTA needs a capability claim, ask whether the company actually offers it before writing it — discovered 2026-06-17
- Pento content voice rejects these patterns: negative-parallelism/antithesis ("the merits are X, the engineering reality is Y"), negation-then-correction openers ("None of this argues against X; it is Y"), and rule-of-three abstract listicles as closers. Write plain, concrete, declarative sentences in first-person plural, anchored to real artifacts; ground every claim in what Pento actually does — discovered 2026-06-17
- When the user explicitly sets a working scope (e.g. `export AWS_PROFILE=parsan`), treat it as a hard boundary, not a starting point. If the answer might live outside that scope (a different AWS account/profile, another repo, another system), STOP and ask which account/profile to use; never switch profiles, run `aws configure list-profiles`, or enumerate other accounts (even read-only `describe`/`get-caller-identity` calls) to chase an unfamiliar term. Read-only does not make a cross-account call in-scope. An unrecognized name is a reason to ask a question, not to hunt across credentials — discovered 2026-06-17
- Do not use the AskUserQuestion popup when the user is asking for your opinion, judgment, or recommendation; answer directly in prose. Reserve the popup for decisions that are genuinely the user's to make between concrete, pre-defined options. "What do you think?" or "is this enough?" gets a reasoned answer, not a multiple-choice menu — discovered 2026-06-19
- When spawning a background agent or workflow expected to run more than ~5 minutes, emit a brief note at launch ("starting X, ~Y min") and schedule a midpoint status check, so the user does not wonder whether it stalled. Rely on harness task-notifications for completion, but a launch note and one mid-run check prevent the user from sending repeated "is it stuck?" pings — discovered 2026-06-19
- When the user asks for a specific deliverable and explicitly defers a related part to later ("design the final architecture, then we'll see about the first step"), produce ONLY the requested deliverable; do not fold the deferred part (phasing, sequencing, next-steps, v1-vs-later) into the artifact, not even as a toggle or aid. Explicitly deferred means excluded, not "include it lightly" — discovered 2026-06-23
- Never run headless Chrome. The user explicitly does not want headless browser sessions launched (browser-use defaults to headless chromium). If a page must be rendered, serve it over HTTP and use a headed/profile browser only with the user's okay, or avoid browser rendering entirely (verify HTML/data by inspection instead). Publishing an Artifact renders on Codex.ai without a local browser — discovered 2026-06-24
