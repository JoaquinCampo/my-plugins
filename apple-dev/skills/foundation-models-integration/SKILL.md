---
name: foundation-models-integration
description: Add Apple's on-device Foundation Models framework (Apple Intelligence) to a SwiftUI app. Use for streaming LLM responses, @Generable structured output, Tool protocol implementations, availability checks. iOS 26+, iPadOS 26+, macOS 26+, visionOS 26+. Triggers on Apple Intelligence, Foundation Models, on-device LLM, @Generable, SystemLanguageModel, LanguageModelSession.
---

# Foundation Models Integration

## When this applies

On-device LLM features in a SwiftUI app: streaming chat, structured output extraction from text, tool calling against system data (Contacts, Calendar, Location) or custom logic. Runs locally with no network, no API key, no per-request cost. Use this skill instead of a cloud LLM when privacy, offline operation, or predictable cost matter more than frontier reasoning quality.

## Prerequisites

- Deployment target iOS 26, iPadOS 26, macOS 26, or visionOS 26.
- Device that supports Apple Intelligence and has it enabled in Settings.
- `import FoundationModels` at the top of any file that touches the framework.
- Simulator runs the model but performance is misleading. Profile on device.

## The 5-step playbook

1. Read `SystemLanguageModel.default.availability` and switch on it. Render a fallback view for each `.unavailable` reason (`.deviceNotEligible`, `.appleIntelligenceNotEnabled`, `.modelNotReady`). Re-read on `scenePhase` becoming active because download or enable state can change while backgrounded.
2. Create one `LanguageModelSession` per long-lived conversation, owned by an `@Observable` service (for example `ChatService`). Configure tools and instructions in the initializer. Instructions are trusted, prompts are not, so never interpolate user input into the instructions string.
3. Pick the output mode. Free-form text streams via `session.streamResponse(to:)` and yields a growing `String`. Structured output requires a `@Generable` type (for example `SummaryGenerable`) and streams via `session.streamResponse(generating:)`, yielding `PartiallyGenerated<T>` whose fields are optional and fill in over time. Each iteration replaces; do not append.
4. For tool calling, conform a struct to `Tool` with `name`, `description`, a nested `@Generable struct Arguments`, and `func call(arguments:) async throws -> ToolOutput`. Register on the session at init via `LanguageModelSession(tools: [WeatherTool()])`. Mention each tool by name in the instructions so the model knows when to invoke it.
5. Catch the three named errors around every `respond` and `streamResponse` call: `LanguageModelSession.GenerationError.guardrailViolation`, `.exceededContextWindowSize`, `.unsupportedLanguageOrLocale`. Map each to a user-visible message. On context overflow, rebuild the session with a condensed transcript or a rolling summary.

## Deep dives in references/

- `references/session-streaming-generable.md`: availability handling, session lifecycle, free-form streaming wired to SwiftUI state, `@Generable` types with `@Guide`, structured streaming with `PartiallyGenerated<T>`.
- `references/tools-and-errors.md`: `Tool` protocol conformance, registering and triggering tools, the three error cases with try/catch examples and recommended UI copy, context-window recovery.

## Anti-patterns

- Putting user-controlled text in the `instructions` argument. That is the prompt-injection vector.
- Force-unwrapping tool outputs (network bodies, parsed HTML, decoded JSON). Tools must fail soft and return a `ToolOutput` string explaining the failure.
- Estimating tokens by word count divided by a constant. Use a proper tokenizer when you need a tight budget.
- Persisting an in-progress placeholder string like `"..."` while streaming. Use an empty string plus a `streaming: Bool` flag, or keep the placeholder outside your durable store until the stream finishes.
- Creating a new `LanguageModelSession` per turn. You lose conversation context, pay the prewarm cost again, and re-send the schema on every structured call.

## Performance levers

- Call `session.prewarm()` as soon as user intent is clear (input field focused, chat view appeared, conversation tapped). It loads weights and primes the KV cache so first-token latency drops.
- On context overflow, prefer a rolling summary over full-transcript replay. Generate the summary with the same session after each turn, store it on your model, and prompt with summary plus last user message when token count crosses a safe threshold.
- Profile with the Foundation Models Instrument in Xcode. Track first-token latency, tokens per second, and thermal state on long sessions.
