# Migration Order

A sequencing guide for taking a medium-sized SwiftUI codebase off MVVM without breaking the build at any step. Optimized for "the project compiles after every commit".

## Step 1. Inventory migration units

A migration unit is a `*ViewModel` file plus its paired view (or set of views). Run a tree search for the three telltale tokens and list the files that match:

- `ObservableObject` conformance.
- `@Published` property declarations.
- `@StateObject`, `@ObservedObject`, `@EnvironmentObject` consumption sites.

Tag each unit with one of three labels:

- **View-local**: one ViewModel, one view, nobody else reads it. Easiest to migrate; collapses into the view.
- **Shared service**: one class read by several unrelated views via `.environmentObject(...)`. Migrates to `@Observable` plus `.environment(...)`.
- **Dead**: no live consumers, or only consumed by code that itself is dead. Delete; do not modernize.

Skip anything outside this list. Helper structs, models, utilities, and pure render code do not need to move.

## Step 2. Order the work

Convert in this order, never the reverse:

1. **Leaf views with view-local ViewModels.** No cross-file impact. Each one is a self-contained collapse: delete the ViewModel file, move the state machine into the view as a `ViewState` enum, change `.onAppear { Task { ... } }` to `.task { ... }`. Build, commit, move on.
2. **Shared services.** Change `class X: ObservableObject` to `@Observable final class X`, drop every `@Published`. The scene wiring becomes `@State private var x = X()` plus `.environment(x)`. The compiler will now flag every `@EnvironmentObject var x: X` in consuming views; leave those errors for step 3.
3. **Consuming views of converted services.** Replace `@EnvironmentObject private var x: X` with `@Environment(X.self) private var x`. The body usually needs no other change because property access stays identical.
4. **Combine pipelines, if any remain.** Rewrite to `async`/`await` and `AsyncStream`. Any view that used a Combine-driven `@Published` becomes `@State` with `.task(id:)`. Half-migrated pipelines (a `@Published` fed by an `async` method, or vice versa) are the worst of both worlds; finish each pipeline in one pass.
5. **Delete empty ViewModels.** After steps 1-4 some files have no remaining responsibility. Delete them and remove their target membership.

## Step 3. Keep the project compiling

The project must build after every step. Two techniques:

- **One unit per commit.** Do not start a second unit until the current one is converted, builds clean, and tests pass. The temptation is to flip every `ObservableObject` to `@Observable` at once; resist it because the consuming views will not compile until step 3 of each unit is also done.
- **Do not mix the two systems on one type.** A class is either `ObservableObject` with `@Published` or `@Observable` with plain `var`. Never both. If you find yourself wanting both, you are trying to migrate consumers and producer at the same time; split it into two commits.

For step 2, an intermediate trick when a service has many consumers: temporarily expose the new `@Observable` service alongside the legacy `ObservableObject` (two different types, two different names), migrate consumers one at a time onto the new type, then delete the legacy type. Slower, but always green.

## Step 4. Verify each step

After every commit:

- Run an actual build on the simulator scheme (not just the type checker). A type checker pass is not the same as a project that links its package graph.
- Run the package tests for any package that owns a migrated file.
- Exercise the migrated screen in a Preview or on a simulator. Confirm the state transitions you cared about (`loading -> loaded`, `loading -> error`, `loaded -> reloaded`) actually happen.
- Verify with the team that the visible behavior matches the old version; the goal is a refactor with no functional drift.

If a migrated view depends on a service that has not been migrated yet, that view stays in legacy form until the service moves. Do not modernize halfway.

## Step 5. What to skip

- **Dead ViewModels.** No consumers means no migration; delete.
- **Generated code.** Touch the generator template, not the output.
- **Third-party SDKs you do not own.** If a vendor exposes an `ObservableObject`, wrap it at the boundary in your own `@Observable` adapter rather than rewriting the SDK.
- **Test-only mocks.** Leave them as `ObservableObject` until the test file itself is being touched for other reasons.
- **Code targeting iOS 16 or earlier.** `@Observable` requires iOS 17, iPadOS 17, macOS 14, tvOS 17, watchOS 10, visionOS 1. If your deployment target is older, this migration does not apply yet.

## Done criteria

The migration is done when none of these tokens appear in your codebase outside of the boundary adapters and test mocks: `ObservableObject`, `@Published`, `@StateObject`, `@ObservedObject`, `@EnvironmentObject`, `.environmentObject(`, `AnyCancellable`. The build is green, the tests pass, every screen behaves identically to before.
