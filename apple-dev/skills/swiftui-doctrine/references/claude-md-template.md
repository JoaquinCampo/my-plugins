# Project CLAUDE.md Template

Copy the block below into your project's `CLAUDE.md` (or `AGENTS.md`). Replace placeholders in `{BRACES}` with values for your repo. Delete sections that do not apply (for example, the iOS 26 or Foundation Models sections if you do not target those features).

````markdown
# CLAUDE.md

Contributor contract for working on {PROJECT_NAME} with Claude Code or any other AI agent. The rules below are non-negotiable.

## Project Snapshot

{PROJECT_NAME} is a SwiftUI app targeting {PLATFORM_LIST} built against {SDK_VERSION}. Source of truth for the build is {XCODEPROJ_OR_TUIST_OR_SPM} at `{PROJECT_PATH}`.

## Build and Verify

After any code change, build for the relevant scheme and fix errors before considering the task complete.

```bash
xcodebuild \
  -project "{PROJECT_PATH}" \
  -scheme "{SCHEME}" \
  -destination 'platform=iOS Simulator,name={SIMULATOR}' \
  build
```

For SwiftPM-only projects:

```bash
swift build
swift test
```

Run package tests per scheme:

```bash
xcodebuild test -project "{PROJECT_PATH}" -scheme "{TEST_SCHEME}" \
  -destination 'platform=iOS Simulator,name={SIMULATOR}'
```

## Architecture

### Modular Package Layout

The app is organized into Swift packages under `Packages/`:

- `Models`: data shapes and decoding.
- `Network`: API client, transport, auth.
- `Env` (or `AppState`): cross-cutting `@Observable` services.
- `DesignSystem`: colors, typography, reusable components.
- `{FeaturePackage}`: one package per feature domain.

UI packages depend on logic packages, never the reverse. Cross-package dependencies are declared explicitly in each `Package.swift`.

### State Management

- `@State` for local view state. Default.
- `@Binding` for parent-child two-way flow. Only when needed.
- `@Observable` classes for shared state. Inject at the scene with `.environment(service)`; read with `@Environment(Service.self)`.
- Never nest one `@Observable` inside another. Inject siblings.

### View Pattern

Views are pure state expressions. No ViewModels. Model view state as an enum with associated values and switch on it.

```swift
struct ExampleView: View {
  @Environment(Client.self) private var client
  @State private var state: ViewState = .loading
  enum ViewState { case loading, loaded([Item]), error(Error) }

  var body: some View {
    Group {
      switch state {
      case .loading: ProgressView()
      case .loaded(let items): ItemList(items: items)
      case .error(let error): ErrorView(error: error)
      }
    }.task { await load() }.refreshable { await load() }
  }
}
```

### Async

- `async`/`await` is the default. No Combine in new code.
- Use `.task` not `.onAppear`. `.task` cancels with view lifetime.
- Use `AsyncStream` for reactive state. One stream per concept.

### Concurrency

- Actors only where state isolation matters (networking, persistent stores).
- Pure utilities are not actors.
- Do not run CPU work on the main actor; offload with `Task.detached`.
- Snapshot mutable actor state before any `await`.
- Do not capture non-`Sendable` values inside `Task` closures.

### Testing

- Swift Testing (`@Test`, `#expect`) for new code.
- ViewInspector for SwiftUI view assertions when a Preview is not enough.
- `@MainActor` test classes for UI-bound state.
- Test `@Observable` services directly.
- Every view ships at least one `#Preview`.

## Code Style

- Two-space indentation. SwiftFormat enforced.
- PascalCase types, lowerCamelCase members. Files named after the primary type.
- Composition over inheritance. Keep files under roughly 300 lines.
- Comments explain why, not what.

## iOS 26 Features (delete if not targeting iOS 26)

This project may use Liquid Glass (`glassEffect`, `buttonStyle(.glass)`, `ToolbarSpacer`), scroll edge effects (`scrollEdgeEffectStyle`, `backgroundExtensionEffect`), tab bar accessories (`tabBarMinimizeBehavior`, `TabViewBottomAccessoryPlacement`), `WebView`/`WebPage`, the `@Animatable` macro, and `TextEditor` with `AttributedString`. Guard with `@available` or `if #available` when targeting multiple SDKs.

## Foundation Models (delete if not used)

- Check `SystemLanguageModel.default.isAvailable` before every entry point; render a fallback when unavailable.
- Handle named errors explicitly: `GenerationError.guardrailViolation`, `GenerationError.exceededContextWindowSize`, `GenerationError.unsupportedLanguageOrLocale`.
- Stream responses longer than a sentence; prewarm sessions on intent.
- Keep instructions in the session config; never place user text into instructions.
- Use `@Generable` types with `@Guide` for structured output and tool arguments.

## Hard Rules

1. No ViewModels.
2. `@Observable` for shared state, `@Environment` for injection.
3. Never nest `@Observable` inside `@Observable`.
4. `async`/`await` first; Combine only when unavoidable.
5. `AsyncStream` for reactive state.
6. `.task` not `.onAppear`.
7. Compose views; do not abstract.
8. Build after every change.
9. Swift Testing + ViewInspector for new tests.
10. Actors only where state isolation matters.
11. Snapshot mutable actor state before any `await`.
12. Two-space indentation, SwiftFormat enforced.
13. Maintain legacy patterns in legacy code; modern patterns only in new code.
14. Guard new platform APIs with availability checks.
15. Do not commit secrets.

## When in Doubt

Read Apple's documentation, not third-party tutorials. Prefer the simplest code that is obviously correct. If a patch needs a paragraph to justify itself, it is not ready.
````
