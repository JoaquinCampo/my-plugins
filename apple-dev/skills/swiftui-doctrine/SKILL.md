---
name: swiftui-doctrine
description: Apply modern SwiftUI conventions on Apple platforms (iOS, iPadOS, macOS, visionOS). Triggers on SwiftUI views, `@Observable` services, `NavigationStack`, Swift `async/await`, and Apple-platform project work. Enforces no-ViewModel, modular SwiftPM.
---

# SwiftUI Doctrine

The always-on baseline for writing or reviewing SwiftUI on iOS 17+, iPadOS, macOS, and visionOS. Use it as the default lens whenever Swift, SwiftUI, or Apple-platform code appears in scope.

## When this applies

Any task that creates, edits, or reviews SwiftUI views, `@Observable` services, navigation stacks, Swift Concurrency, or Apple-platform project structure. If the task is a specific recipe (push notifications, Liquid Glass, etc.), pivot to the matching sibling skill listed at the bottom; the doctrine still applies as the baseline.

## The 12 core rules

1. **No ViewModels.** Views are pure state expressions. The `View` struct is already the binding between state and UI; an extra `*ViewModel` layer fights the framework and creates a second source of truth.
2. **`@Observable`, not `ObservableObject`.** Swift Observation is the default for shared state on iOS 17+. `ObservableObject` and `@Published` are legacy Combine-era and out of new code.
3. **Never nest `@Observable` inside `@Observable`.** Nesting breaks observation tracking. Initialize services at the scene or view level and inject them as siblings via `.environment(...)`.
4. **View state as enum.** Model the screen as `enum ViewState { case loading, loaded(T), error(Error) }` and `switch` on it. The `Bool isLoading + [T] items + Error? error` triple is a special-case trap.
5. **State flows down, actions flow up.** Keep state as close to where it is used as possible. Promote to `@Binding` only for parent-child two-way flow, to `@Observable` only when several unrelated views share the same source of truth.
6. **`async`/`await`, not Combine.** Structured concurrency is the default for one-shot calls and `AsyncStream` for reactive flows. Do not bridge async to Combine. Do not invent `@Published` pipelines.
7. **`.task`, not `.onAppear`.** `.task` is lifecycle-aware: it starts on appear, cancels on disappear, and re-runs on `id` change. `.onAppear { Task { ... } }` is a fire-and-forget callback with no cancellation story.
8. **Modular SwiftPM packages.** For non-trivial apps, ship a `Packages/` directory split by domain: `Models`, `Network`, `Env` (or `AppState`), `DesignSystem`, and one package per feature. UI packages depend on logic packages, never the reverse.
9. **Build verification is mandatory.** After any non-trivial edit, run an actual build for the relevant scheme on a named simulator. Type checker passing in an editor is not the same as a project that compiles end to end. Fix failures before moving on.
10. **Swift Testing + ViewInspector, not XCTest.** For new code use `@Test` and `#expect`. Use ViewInspector when a Preview is not enough. Test `@Observable` services directly. Every view ships at least one `#Preview`.
11. **Composition over abstraction.** Break views by responsibility, not by inventing protocols. When a file passes roughly 300 lines or a `switch` case grows past a few lines, extract a focused subview, a `ViewModifier`, or a `ButtonStyle`.
12. **Do not fight SwiftUI.** Use property wrappers as designed. Trust the diffing engine. Inject dependencies through `@Environment`; no service locator, no DI container, no `.shared` singletons.

## Gotchas

The highest-signal failure modes. If you see one of these symptoms, jump to the cause.

- *Symptom*: view does not re-render when an `@Observable` service mutates. *Cause*: the service is stored as a property of another `@Observable`. *Fix*: hoist to the scene and inject siblings via `.environment(_:)`.
- *Symptom*: in-flight async work continues after the view disappears, or stale results overwrite fresh state. *Cause*: `.onAppear { Task { ... } }` is fire-and-forget. *Fix*: use `.task` (or `.task(id:)` for input-driven reloads); both cancel on disappear.
- *Symptom*: loading spinner stuck, or error and data shown at once. *Cause*: a `Bool isLoading + [T] items + Error? error` trio with no enforced exclusivity. *Fix*: model as `enum ViewState { case loading, loaded(T), error(Error) }` and `switch` in `body`.
- *Symptom*: tests pass but the project fails to build. *Cause*: the editor type checker accepted code that the build refuses (availability gates, Sendable, package dep graph). *Fix*: run an actual build with XcodeBuildMCP or `xcodebuild` after every non-trivial edit; treat the build as the first quality gate.
- *Symptom*: shared service updates appear in some views but not others. *Cause*: the service was re-initialized below the scene (e.g., in a `View`'s body), creating sibling instances. *Fix*: own the service with `@State` at the scene exactly once.

## Anti-patterns banned

- ViewModels in new code (any `*ViewModel` class added to a new feature).
- `ObservableObject` and `@Published` in new code.
- `@StateObject`, `@ObservedObject`, `@EnvironmentObject` in new code (use `@State` plus `@Environment` with `@Observable`).
- Combine for trivial async (use `async`/`await` and `AsyncStream`).
- Sleep-based test waits and snapshot-testing every screen.
- Monolithic feature files (split anything past roughly 300 lines).
- Comments explaining *what* the code does instead of *why* it exists.

## Topic deep-dives

- `references/state-and-async-patterns.md`: worked examples for `@Observable` injection, the view-state enum, `.task(id:)`, and `AsyncStream`-driven reactive state.
- `references/anti-patterns.md`: the full ban list with one-line rationale for each.
- `references/claude-md-template.md`: a copy-pasteable project `CLAUDE.md` that encodes the doctrine, with placeholders for build commands and optional sections.

## When to pivot to a recipe skill

The doctrine is the baseline. For these specific tasks, also use the matching sibling skill (it builds on top of the rules above, does not replace them):

- Adding Apple Intelligence or on-device LLM features: `foundation-models-integration`.
- Adopting type-driven navigation or deep-linking: `add-approuter`.
- Migrating an existing screen off MVVM: `refactor-to-no-viewmodel`.
- Bootstrapping a new modular SwiftUI project: `modular-package-skeleton`.
- Adopting iOS 26 Liquid Glass and scroll edge effects: `ios26-liquid-glass-adoption`.
- Wiring push notifications through a proxy: `swiftui-push-proxy`.
- Setting up the build-verify loop for an agent: `xcodebuildmcp-build-loop`.
