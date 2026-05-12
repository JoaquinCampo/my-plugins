# Session, Streaming, and @Generable

## Availability: three states, three UIs

`SystemLanguageModel.default.availability` returns `.available` or `.unavailable(reason)`. Cover every reason explicitly.

```swift
import FoundationModels
import SwiftUI

struct RootView: View {
    var body: some View {
        switch SystemLanguageModel.default.availability {
        case .available:
            ChatView()
        case .unavailable(.deviceNotEligible):
            Text("This device does not support Apple Intelligence.")
        case .unavailable(.appleIntelligenceNotEnabled):
            VStack {
                Text("Apple Intelligence is off.")
                Button("Open Settings") {
                    if let url = URL(string: UIApplication.openSettingsURLString) {
                        UIApplication.shared.open(url)
                    }
                }
            }
        case .unavailable(.modelNotReady):
            VStack { ProgressView(); Text("Model is downloading.") }
        case .unavailable(_):
            Text("Model temporarily unavailable.")
        }
    }
}
```

Re-read availability on `scenePhase` becoming `.active`. Build the session lazily once `.available`; do not construct one when unavailable.

## Session lifecycle

One `LanguageModelSession` per long-lived conversation, owned by an `@Observable` service. One in-flight request per session.

```swift
import FoundationModels
import Observation

@Observable
final class ChatService {
    private let session: LanguageModelSession

    init() {
        session = LanguageModelSession {
            "You are a concise assistant. Keep replies under three sentences."
        }
    }
    func prewarm() { session.prewarm() }
}
```

Call `prewarm()` when intent is clear (input focused, chat view appeared). Drop the service to dispose the session; there is no explicit close.

## Free-form streaming into SwiftUI state

`streamResponse(to:)` yields cumulative `String` values. Each iteration replaces the previous value; do not concatenate.

```swift
@Observable
final class ChatService {
    var streamingText: String = ""
    var isStreaming: Bool = false
    private let session: LanguageModelSession
    // init as above

    func send(_ prompt: String) async throws {
        isStreaming = true
        defer { isStreaming = false }
        for try await chunk in session.streamResponse(to: prompt) {
            if Task.isCancelled { break }
            streamingText = chunk
        }
    }
}
```

In the view, bind `Text(service.streamingText)` and apply `.animation(.bouncy, value: service.streamingText)` to let SwiftUI animate growth. Disable the send button on `service.isStreaming`.

## @Generable types and @Guide

`@Generable` makes a struct or enum a valid output shape. Annotate every field with `@Guide(description:)` at minimum. Add `.count(n)`, `.count(min...max)`, `.range(min...max)`, or a `Regex` when bounds matter. Optional fields may be omitted by the model. Nested types must also be `@Generable`.

```swift
import FoundationModels

@Generable
struct SummaryGenerable {
    @Guide(description: "Headline under ten words")
    let title: String

    @Guide(description: "One sentence summary")
    let summary: String

    @Guide(.range(1...5))
    let confidence: Int

    @Guide(.count(3))
    let keyPoints: [String]

    let category: Category

    @Generable
    enum Category: String, CaseIterable {
        case news, opinion, tutorial, reference
    }
}
```

## Structured streaming with PartiallyGenerated

`streamResponse(generating:)` yields `PartiallyGenerated<T>` whose fields are optional and fill in as generation proceeds. Treat every field as optional in the view layer.

```swift
@Observable
final class ChatService {
    var partial: SummaryGenerable.PartiallyGenerated?
    private let session: LanguageModelSession

    func summarize(_ text: String) async throws {
        let stream = session.streamResponse(generating: SummaryGenerable.self) {
            "Summarize the following text:\n\(text)"
        }
        for try await value in stream {
            if Task.isCancelled { break }
            partial = value
        }
    }
}
```

View side renders each optional field as it appears:

```swift
if let title = service.partial?.title { Text(title).font(.headline) }
if let points = service.partial?.keyPoints, !points.isEmpty {
    ForEach(points, id: \.self) { Text("- \($0)") }
}
```

After the first structured call in a session, pass `includeSchemaInPrompt: false` on subsequent calls and embed an example output in the instructions to keep the model on-shape without re-paying the schema cost.
