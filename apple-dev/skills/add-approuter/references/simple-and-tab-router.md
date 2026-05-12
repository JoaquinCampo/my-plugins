# SimpleRouter and Router, worked examples

## SimpleRouter, single-stack app

Define the vocabulary:

```swift
import AppRouter
import SwiftUI

enum Destination: DestinationType {
  case detail(id: String)
  case settings

  static func from(path: String, fullPath: [String], parameters: [String: String]) -> Destination? {
    nil // no deep linking here, see deep-linking.md
  }
}

enum Sheet: SheetType {
  case compose
  var id: Int { hashValue }
}
```

Wire the root view, inject the router, attach destinations and sheet:

```swift
struct RootView: View {
  @State private var router = SimpleRouter<Destination, Sheet>()

  var body: some View {
    NavigationStack(path: $router.path) {
      HomeView()
        .navigationDestination(for: Destination.self) { dest in
          switch dest {
          case .detail(let id): DetailView(id: id)
          case .settings:       SettingsView()
          }
        }
    }
    .sheet(item: $router.presentedSheet) { sheet in
      switch sheet {
      case .compose: ComposeView()
      }
    }
    .environment(router)
  }
}
```

Read the router from any descendant:

```swift
struct HomeView: View {
  @Environment(SimpleRouter<Destination, Sheet>.self) private var router

  var body: some View {
    VStack {
      Button("Open detail") { router.navigateTo(.detail(id: "42")) }
      Button("Compose")      { router.presentSheet(.compose) }
      Button("Pop")          { router.popNavigation() }
      Button("Home")         { router.popToRoot() }
    }
  }
}
```

API summary: `path`, `presentedSheet`, `navigateTo(_:)`, `presentSheet(_:)`, `dismissSheet()`, `popNavigation()`, `popToRoot()`, `navigate(to: URL)`, `navigate(to: String)`.

## Router, tab-based app

Add a `TabType` and a typealias for ergonomics:

```swift
enum AppTab: String, TabType, CaseIterable {
  case home, profile, settings
  var id: String { rawValue }
  var icon: String {
    switch self {
    case .home:     "house"
    case .profile:  "person"
    case .settings: "gear"
    }
  }
}

typealias AppRouter = Router<AppTab, Destination, Sheet>
```

Root view, one `NavigationStack` per tab, each bound to its own slice via the `$router[tab]` subscript:

```swift
struct RootView: View {
  @State private var router = AppRouter(initialTab: .home)

  var body: some View {
    TabView(selection: $router.selectedTab) {
      ForEach(AppTab.allCases) { tab in
        NavigationStack(path: $router[tab]) {
          rootView(for: tab)
            .navigationDestination(for: Destination.self) { destinationView(for: $0) }
        }
        .tabItem { Label(tab.rawValue.capitalized, systemImage: tab.icon) }
        .tag(tab)
      }
    }
    .sheet(item: $router.presentedSheet) { sheetView(for: $0) }
    .environment(router)
    .environment(\.currentTab, router.selectedTab)
  }
}
```

The `$router[tab]` binding is what makes each tab's back stack independent. Switching tabs preserves the inactive stacks.

Programmatic tab switch and push from a child:

```swift
struct ProfileView: View {
  @Environment(AppRouter.self) private var router

  var body: some View {
    Button("Go to settings tab") { router.selectedTab = .settings }
    Button("Push detail in current tab") {
      router.navigateTo(.detail(id: "99"))
    }
    Button("Push detail in profile tab") {
      router.navigateTo(.detail(id: "99"), for: .profile)
    }
    Button("Pop profile to root") { router.popToRoot(for: .profile) }
  }
}
```

Notes:

- `presentedSheet` is shared across tabs. There is one sheet slot per router.
- `selectedTabPath` is a read-only convenience for `paths[selectedTab]`.
- Reading `\.currentTab` in a child avoids holding a router reference just to know which tab the view sits in.
