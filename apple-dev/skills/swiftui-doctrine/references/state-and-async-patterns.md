# State and Async Patterns

Worked examples for the doctrine. Abstract code only; adapt to your domain.

## 1. `@Observable` service injected at the scene

A service that several unrelated views need is an `@Observable` class. Initialize it at the scene with `@State`, inject with `.environment(_:)`, read at the leaf with `@Environment(_:)`.

```swift
@Observable
final class AccountStore {
  var current: Account?
  var available: [Account] = []
}

@main
struct MyApp: App {
  @State private var accounts = AccountStore()
  @State private var client = APIClient()

  var body: some Scene {
    WindowGroup {
      RootView()
        .environment(accounts)
        .environment(client)
    }
  }
}

struct ProfileView: View {
  @Environment(AccountStore.self) private var accounts
  // ...
}
```

Sibling services are injected at the same level, never nested. Never store one `@Observable` as a property of another `@Observable`; observation tracking will not see through the boundary.

## 2. View-state enum

Make illegal states unrepresentable, then `switch` in the body.

```swift
struct ItemListView: View {
  @Environment(APIClient.self) private var client
  @State private var state: ViewState = .loading

  enum ViewState {
    case loading
    case loaded([Item])
    case empty
    case error(Error)
  }

  var body: some View {
    Group {
      switch state {
      case .loading: ProgressView()
      case .loaded(let items): ItemList(items: items)
      case .empty: EmptyStateView()
      case .error(let error): ErrorView(error: error) {
        Task { await load() }
      }
    }
    .task { await load() }
    .refreshable { await load() }
  }

  private func load() async {
    do {
      let items = try await client.fetchItems()
      state = items.isEmpty ? .empty : .loaded(items)
    } catch {
      state = .error(error)
    }
  }
}
```

If a `case` grows past a few lines, extract a named subview.

## 3. `.task(id:)` for input-driven reloads

`.task(id:)` cancels and restarts whenever the identifier changes. Use it for detail screens that key off an input, search views, filter views.

```swift
struct DetailView: View {
  @Environment(APIClient.self) private var client
  let itemID: Item.ID
  @State private var state: ViewState = .loading

  var body: some View { content.task(id: itemID) { await load() } }

  private func load() async {
    do { state = .loaded(try await client.fetchItem(itemID)) }
    catch is CancellationError { /* expected on id change */ }
    catch { state = .error(error) }
  }
}
```

`.onAppear` will not cancel the in-flight request when the user navigates to a sibling item; `.task(id:)` will.

## 4. `AsyncStream` for reactive shared state

One stream per concept. The root view loops on it; no `@Published`, no `sink`, no manual subscription bookkeeping.

```swift
@Observable
final class Auth {
  public let configurationUpdates: AsyncStream<Configuration?>
  private let cont: AsyncStream<Configuration?>.Continuation

  init() {
    var c: AsyncStream<Configuration?>.Continuation!
    self.configurationUpdates = AsyncStream { c = $0 }
    self.cont = c
  }

  func login(_ c: Configuration) { cont.yield(c) }
  func logout() { cont.yield(nil) }
}

// At the root view:
.task {
  for await config in auth.configurationUpdates {
    if let config { await refresh(with: config) } else { appState = .unauthenticated }
  }
}
```

Login, logout, refresh are the same event type. The view just reacts.

## 5. Concurrency hygiene

- Snapshot mutable actor state before any `await`; the value can change across the suspension point.
- Do not capture non-`Sendable` values inside `Task` closures; copy out the data you need.
- Offload CPU work with `Task.detached` or `Task(priority:)` rather than hopping onto an actor.
- Use `async let` for independent concurrent calls; `withThrowingTaskGroup` only for dynamic fan-out.

```swift
actor Networking {
  var apiKey: String?

  func send(_ req: Request) async throws -> Data {
    let key = apiKey                 // snapshot first
    return try await perform(req, key: key)
  }
}
```
