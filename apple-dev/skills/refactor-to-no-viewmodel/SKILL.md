---
name: refactor-to-no-viewmodel
description: Migrate legacy SwiftUI code from ObservableObject + @Published + ViewModel patterns to @Observable + @Environment + view-state enums. Use when modernizing an iOS or macOS codebase, removing ViewModel layers, or replacing Combine with async/await.
---

# Refactor To No-ViewModel

A step-by-step plan for taking a SwiftUI codebase off MVVM and onto modern Observation. The goal is fewer files, fewer wrappers, and views that own their own local state.

## When this applies

Use this skill when you encounter any of the following in a SwiftUI project targeting iOS 17, iPadOS 17, macOS 14, or newer:

- `*ViewModel` classes paired one-to-one with views.
- `ObservableObject` conformance with `@Published` properties.
- Views consuming state via `@StateObject`, `@ObservedObject`, or `@EnvironmentObject`.
- Combine subscriptions used to bridge async work into view state.
- A "store" or "app state" object passed through `.environmentObject(...)` at the root.

If none of those appear, the code is already modern and this skill does not apply.

## The target pattern

Views declare local state with `@State`, model the screen as a `ViewState` enum, switch on it in the body, and pull shared services from `@Environment`. Services are `@Observable` classes injected at the scene with `.environment(service)`. Async work happens in `.task` and `.task(id:)`, never in `.onAppear`.

## Three migration moves

1. **ObservableObject becomes @Observable.** Add `@Observable` to the class, drop `ObservableObject` conformance, remove every `@Published`. In consuming views, change `@StateObject` to `@State` and `@EnvironmentObject` to `@Environment(Service.self)`. Plain `let` references inside child views need no wrapper at all.
2. **View-local ViewModel logic moves into the view as a `ViewState` enum with `@State`.** When the only consumer of a ViewModel is its paired view, inline the state machine. Replace `@Published var isLoading`, `@Published var items`, and `@Published var error` with a single `enum ViewState { case loading, loaded(T), error(Error) }` and one `@State private var viewState: ViewState = .loading`.
3. **Shared logic moves into an @Observable service.** When two or more views read the same state, lift it into an `@Observable` class injected via `.environment(...)` at the scene and read via `@Environment(Service.self)`. Do not invent a ViewModel as the middle layer.

## Migration order

1. **Start with leaf views.** Pick views that own their state and share nothing. These are pure local-to-the-view ViewModels and convert one file at a time without breaking neighbors.
2. **Then convert services.** Promote shared `ObservableObject` types to `@Observable`. Touch only the service file and the scene injection point.
3. **Then convert views that read shared state.** Switch their consumption sites to `@Environment(Service.self)`. The compiler errors at the call sites are the worklist.
4. **Delete empty ViewModels last.** Once nothing references a `*ViewModel`, remove the file. Do not delete in step 1; the compiler will guide you in step 4.

## Pitfalls

- Do not nest `@Observable` inside `@Observable`; SwiftUI's observation tracking breaks. Inject siblings at the scene instead.
- `@State` on a class needs `@Observable` on the class. `@State` on a struct works as-is.
- Do not keep both `ObservableObject` and `@Observable` on one type during migration; pick one and finish the file before moving on.
- Combine pipelines must be rewritten to `async`/`await` and `AsyncStream`; a half-migrated mix where `@Published` feeds an async function (or vice versa) is the worst of both worlds.
- Do not migrate dead code. If a ViewModel has no live callers, delete it; do not modernize it.
- Maintain legacy patterns inside files you do not own this pass. New code is modern only; existing files stay coherent until intentionally migrated.

## Deep dives in references/

- `references/before-after-snippets.md`: three side-by-side migrations (view-local ViewModel, shared service, Combine pipeline) with abstract names and labeled before/after blocks.
- `references/migration-order.md`: a practical sequencing guide for a medium codebase: how to identify migration units, what order to convert them, how to keep the project compiling, how to verify each step.
