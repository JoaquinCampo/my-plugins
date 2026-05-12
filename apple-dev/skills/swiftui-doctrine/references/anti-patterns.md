# Anti-Patterns

The full ban list. One line of rationale each. If a patch ships any of these in new code, reject it.

## Architecture

- **A `*ViewModel` class per view.** Adds a layer with no observable benefit; views are already the state binding.
- **Moving state out of a view "for cleanliness".** Promote only when sharing is genuinely required; otherwise it is round-trip noise.
- **Speculative abstraction layers.** Protocols, factories, and managers with one implementation are bogus shit until proven otherwise.
- **`.shared` singletons accessed as globals.** Inject via `@Environment`; singletons hide dependencies and break testability.
- **Service locators or DI containers.** SwiftUI's environment is the framework's answer; do not import an extra container.

## State management

- **`ObservableObject` and `@Published` in new code.** Legacy Combine-era; use `@Observable` from the Observation framework.
- **`@StateObject`, `@ObservedObject`, `@EnvironmentObject` in new code.** Replace with `@State` and `@Environment` on `@Observable` types.
- **Nesting an `@Observable` inside another `@Observable`.** Breaks SwiftUI's observation tracking; inject siblings at the scene.
- **`Bool isLoading + [T] items + Error? error` trios.** Use a `ViewState` enum with associated values so illegal states cannot exist.
- **Two-way binding to shared services via custom wrappers.** Use `@Binding` for parent-child only; for shared state, mutate the `@Observable` directly.

## Async and concurrency

- **Combine for trivial async.** Use `async`/`await`; Combine is legacy in new SwiftUI code.
- **`.onAppear { Task { await ... } }`.** Use `.task` for lifecycle and cancellation; `.onAppear` is fire-and-forget.
- **Bridging `async` to `@Published` via `sink`.** Use `AsyncStream` for reactive state; one stream per concept.
- **Actors for everything.** Use actors only where state isolation matters (networking, persistent stores); pure utilities should not be actors.
- **CPU work on the main actor.** Offload with `Task.detached` or `Task(priority:)`.
- **Reading mutable actor state across an `await`.** Snapshot the value into a local before the suspension point.
- **Capturing non-`Sendable` values inside `Task` closures.** Copy out the data you need and capture the copy.

## View construction

- **Monolithic feature files past roughly 300 lines.** Split by responsibility; each subview gets its own struct.
- **Custom container views wrapping a single `Button`.** Extract a `ButtonStyle` or `LabelStyle` instead.
- **Repeated modifier chains pasted across files.** Extract a `ViewModifier` once the same chain appears three times.
- **Fighting the diffing engine with manual `id` games.** Trust SwiftUI; if you must reset state, use `.id(value)` on the subtree, not workarounds.

## Testing

- **Snapshot-testing every screen.** Visual regressions belong in `#Preview`; reserve snapshot tests for the few cases where text comparison is not enough.
- **Sleep-based test waits.** Use Swift Testing's async support, `confirmation`, or `withCheckedContinuation` with explicit signals.
- **Mocking the entire SwiftUI runtime.** Test `@Observable` services directly; test the view with ViewInspector only when a Preview cannot express the intent.

## Style

- **Comments explaining *what* the code does.** The code already says what; comments should explain *why* or a non-obvious constraint.
- **Drive-by refactors mixed into a feature patch.** Surgical changes only; unrelated cleanup goes in its own patch.
- **Reformatting whitespace inside an otherwise small diff.** SwiftFormat owns whitespace; do not relitigate it line by line.

## Platform

- **Using new platform APIs without an availability guard.** Wrap with `@available` or `if #available`; for Foundation Models, gate on `SystemLanguageModel.default.isAvailable` and render a fallback.
- **Placing user-supplied text into LLM session instructions.** Treat user input as data, never as instructions; instructions live in the session config.

## Project hygiene

- **Mixing modern patterns into a legacy MVVM file mid-feature.** Maintain legacy code as-is until intentionally migrated; new files are modern only.
- **Skipping the build after a change.** Type checker passing in an editor is not the same as a clean project build; the build is the first quality gate.
