# Before / After Snippets

Three migrations side-by-side. Names are abstract (`WidgetService`, `WidgetView`, `Item`).

## 1. View-local ViewModel becomes @State + view-state enum

The ViewModel is paired one-to-one with the view and only hosts three published properties.

### Before

```swift
@MainActor
final class WidgetViewModel: ObservableObject {
  @Published var isLoading = false
  @Published var items: [Item] = []
  @Published var error: Error?
  func load(using service: WidgetService) async {
    isLoading = true; defer { isLoading = false }
    do { items = try await service.fetchItems() } catch { self.error = error }
  }
}
struct WidgetView: View {
  @StateObject private var viewModel = WidgetViewModel()
  @EnvironmentObject private var service: WidgetService
  var body: some View {
    Group {
      if viewModel.isLoading { ProgressView() }
      else if let error = viewModel.error { ErrorView(error: error) }
      else { ItemList(items: viewModel.items) }
    }
    .onAppear { Task { await viewModel.load(using: service) } }
  }
}
```

### After

```swift
struct WidgetView: View {
  @Environment(WidgetService.self) private var service
  @State private var viewState: ViewState = .loading
  enum ViewState { case loading, loaded([Item]), error(Error) }
  var body: some View {
    Group {
      switch viewState {
      case .loading: ProgressView()
      case .loaded(let items): ItemList(items: items)
      case .error(let error): ErrorView(error: error)
      }
    }
    .task { await load() }
  }
  private func load() async {
    do { viewState = .loaded(try await service.fetchItems()) }
    catch { viewState = .error(error) }
  }
}
```

The ViewModel file is deleted. `isLoading + items + error` collapse into one enum that makes illegal states unrepresentable.

## 2. Shared ObservableObject service becomes @Observable via @Environment

### Before

```swift
final class AccountStore: ObservableObject {
  @Published var current: Account?
  @Published var available: [Account] = []
}
@main
struct WidgetApp: App {
  @StateObject private var accounts = AccountStore()
  var body: some Scene {
    WindowGroup { RootView().environmentObject(accounts) }
  }
}
struct ProfileView: View {
  @EnvironmentObject private var accounts: AccountStore
  var body: some View { Text(accounts.current?.name ?? "") }
}
```

### After

```swift
@Observable
final class AccountStore {
  var current: Account?
  var available: [Account] = []
}
@main
struct WidgetApp: App {
  @State private var accounts = AccountStore()
  var body: some Scene {
    WindowGroup { RootView().environment(accounts) }
  }
}
struct ProfileView: View {
  @Environment(AccountStore.self) private var accounts
  var body: some View { Text(accounts.current?.name ?? "") }
}
```

Only views that read `current` or `available` recompute; SwiftUI tracks property reads, not the whole object.

## 3. Combine pipeline becomes async/await + .task(id:)

### Before

```swift
final class SearchViewModel: ObservableObject {
  @Published var query = ""
  @Published var results: [Item] = []
  private var bag = Set<AnyCancellable>()
  init(service: WidgetService) {
    $query
      .debounce(for: .milliseconds(300), scheduler: RunLoop.main)
      .removeDuplicates()
      .flatMap { service.searchPublisher(for: $0) }
      .replaceError(with: [])
      .assign(to: &$results)
  }
}
```

### After

```swift
struct SearchView: View {
  @Environment(WidgetService.self) private var service
  @State private var query = ""
  @State private var results: [Item] = []
  var body: some View {
    List(results) { ItemRow(item: $0) }
      .searchable(text: $query)
      .task(id: query) {
        try? await Task.sleep(for: .milliseconds(300))
        guard !Task.isCancelled else { return }
        results = (try? await service.search(query)) ?? []
      }
  }
}
```

`.task(id:)` re-runs when `query` changes and cancels the in-flight task automatically, replacing `debounce`, `removeDuplicates`, `flatMap`, and `assign(to:)`. The service exposes a plain `async` `search(_:)`; the publisher is gone.
