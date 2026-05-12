# Tools and Errors

## Tool protocol conformance

A `Tool` is a Swift struct (or class for stateful tools) the model invokes mid-generation. Required surface: `name`, `description`, a nested `@Generable struct Arguments`, and `func call(arguments:) async throws -> ToolOutput`.

```swift
import FoundationModels

struct WeatherTool: Tool {
    let name = "Weather"
    let description = "Look up current weather for a city."

    @Generable
    struct Arguments {
        @Guide(description: "City name, English")
        let city: String
    }

    func call(arguments: Arguments) async throws -> ToolOutput {
        let report = try await fetchWeather(for: arguments.city)
        return ToolOutput("\(arguments.city): \(report.summary), \(report.tempC) C")
    }
}
```

Return `ToolOutput(String)` for free-form text. Return `ToolOutput(GeneratedContent(myGenerable))` when the model should consume a typed value. The same `@Generable` type can be both a tool return shape and a field on the model's structured output, which makes the wiring symmetric.

```swift
struct WebFetchTool: Tool {
    let name = "WebFetch"
    let description = "Fetch a URL and return title, description, and thumbnail."

    @Generable
    struct Arguments {
        @Guide(description: "Absolute https URL")
        let url: String
    }

    func call(arguments: Arguments) async throws -> ToolOutput {
        guard let url = URL(string: arguments.url) else {
            return ToolOutput("Invalid URL: \(arguments.url)")
        }
        let metadata = try await PageMetadataLoader.load(url)
        return ToolOutput(GeneratedContent(metadata))
    }
}
```

## Registering tools on a session

Pass tools at session init. Multiple tools can coexist; the model picks. Mention each tool by name in the instructions so the model knows when to invoke it.

```swift
let session = LanguageModelSession(
    tools: [WeatherTool(), WebFetchTool()]
) {
    """
    You are a concise assistant.
    Use WeatherTool when the user asks about weather.
    Use WebFetchTool when the user pastes a URL.
    Do not invent metadata; only include attachments from tool output.
    """
}
```

## Tool call lifecycle

The model decides to call a tool, the framework invokes `call(arguments:)`, awaits it, then injects the returned `ToolOutput` into the next generation step. From the caller's side this is invisible; you only see the final stream. Tools therefore must:

- Fail soft. Return `ToolOutput("...")` describing the failure instead of throwing for expected errors (bad input, 404, parse miss). Throw only for unexpected programmer errors.
- Be idempotent where possible. The model may retry.
- Avoid force-unwraps on network or parse output. A non-UTF8 body or a missing tag should produce a graceful `ToolOutput`, not a trap.

## The three errors

`respond` and `streamResponse` throw `LanguageModelSession.GenerationError` cases. Catch each explicitly.

```swift
do {
    for try await chunk in session.streamResponse(to: prompt) {
        if Task.isCancelled { break }
        streamingText = chunk
    }
} catch LanguageModelSession.GenerationError.guardrailViolation {
    userMessage = "The content was blocked by safety filters. Try a different prompt."
} catch LanguageModelSession.GenerationError.exceededContextWindowSize {
    await rebuildSessionWithCondensedHistory()
    userMessage = "Conversation got long. Starting a fresh context."
} catch LanguageModelSession.GenerationError.unsupportedLanguageOrLocale {
    userMessage = "Language not supported. Try English."
} catch {
    userMessage = "Something went wrong: \(error.localizedDescription)"
}
```

UI guidance:

- `guardrailViolation`: a system-style bubble with the safety copy. Do not auto-retry the same prompt.
- `exceededContextWindowSize`: silently rebuild the session, then either auto-retry or post a one-line notice. Preserve a rolling summary so the new session has continuity.
- `unsupportedLanguageOrLocale`: tell the user to switch input language. Detect locale up front when possible.

## Context-window management on overflow

Two strategies, pick one per app.

Condensed transcript: keep the first entry (system priming), insert a synthetic system summary, append the last two entries, and seed a new session.

```swift
var entries: [Transcript.Entry] = []
if let first = session.transcript.entries.first { entries.append(first) }
entries.append(Transcript.Entry(role: .system,
    content: "Earlier the user discussed travel plans and weather."))
entries.append(contentsOf: session.transcript.entries.suffix(2))
session = LanguageModelSession(transcript: Transcript(entries: entries))
```

Rolling summary: store a `summary: String` on your conversation model and regenerate it with the same session after each turn. When the estimated token count crosses a safe threshold, prompt with `summary + last user message` instead of full history. This trades one extra generation per turn for predictable steady-state token cost.
