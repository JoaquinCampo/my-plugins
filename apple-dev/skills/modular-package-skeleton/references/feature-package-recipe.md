# Feature Package Recipe

Step-by-step recipe for adding a new feature package (`Bookmarks`, `Search`, `Profile`, etc.) to a modular SwiftUI project. Assumes the layout from `layout-and-package-swift.md` is in place: Models, Network, Env, DesignSystem, and an App target that owns the router.

Steps: create folder, write `Package.swift`, add to App target dependencies, create root view, add `RouterDestination` case, wire into App destinations switch, add test target.

## 1. Create folder and skeleton

```
Packages/Bookmarks/
  Package.swift
  Sources/Bookmarks/
    BookmarksView.swift
  Tests/BookmarksTests/
    BookmarksViewTests.swift
```

## 2. Write Package.swift

Follow the feature-package template. Keep the dependency list minimal: Models, Network, Env, DesignSystem. Do not depend on other feature packages.

```swift
// swift-tools-version: 6.0
import PackageDescription

let package = Package(
  name: "Bookmarks",
  platforms: [.iOS(.v17), .macOS(.v14), .visionOS(.v1)],
  products: [.library(name: "Bookmarks", targets: ["Bookmarks"])],
  dependencies: [
    .package(path: "../Models"),
    .package(path: "../Network"),
    .package(path: "../Env"),
    .package(path: "../DesignSystem"),
  ],
  targets: [
    .target(
      name: "Bookmarks",
      dependencies: ["Models", "Network", "Env", "DesignSystem"],
      swiftSettings: [
        .swiftLanguageMode(.v6),
        .defaultIsolation(MainActor.self),
      ]
    ),
    .testTarget(
      name: "BookmarksTests",
      dependencies: ["Bookmarks"]
    ),
  ]
)
```

## 3. Add to the App target

Open the Xcode project, select the App target, and add `Bookmarks` under "Frameworks, Libraries, and Embedded Content". If the workspace is generated, edit the project manifest and add the local package reference.

## 4. Create the root view

The root view is the only public symbol the feature exposes. Keep state inside the view or in an `@Observable` service injected from Env. No ViewModel.

```swift
import SwiftUI
import Env
import Network

public struct BookmarksView: View {
  @Environment(NetworkClient.self) private var client
  @State private var state: ViewState = .loading

  public init() {}

  public var body: some View {
    Group {
      switch state {
      case .loading: ProgressView()
      case .loaded(let items): List(items) { BookmarkRow(item: $0) }
      case .error(let error): ErrorView(error: error) { Task { await load() } }
      }
    }
    .task { await load() }
  }

  private func load() async { /* fetch via client, set state */ }
}

enum ViewState { case loading, loaded([Bookmark]), error(Error) }
```

## 5. Add a RouterDestination case

`RouterDestination` lives in Env (or in a small `Destinations` module if you split it out). Adding a feature means appending one case.

```swift
// Packages/Env/Sources/Env/Router.swift
public enum RouterDestination: Hashable {
  case timeline
  case profile(userID: String)
  case bookmarks
}
```

## 6. Wire the case into the App destinations switch

The App target owns the exhaustive switch that maps each destination to a view. This is the only place that imports every feature package; features themselves stay decoupled.

```swift
// App/Destinations/AppDestinations.swift
import SwiftUI
import Env
import Timeline
import Profile
import Bookmarks

extension View {
  func withAppDestinations() -> some View {
    navigationDestination(for: RouterDestination.self) { dest in
      switch dest {
      case .timeline:               TimelineView()
      case .profile(let id):        ProfileView(userID: id)
      case .bookmarks:              BookmarksView()
      }
    }
  }
}
```

Any feature can push `.bookmarks` onto the router path without importing Bookmarks.

## 7. Add the test target

Swift Testing first. Hit the public API, not internals. Skip snapshot tests unless a layout needs them.

```swift
import Testing
@testable import Bookmarks

@Test func emptyState_rendersList() async throws {
  // Construct the view, drive its state via the public init,
  // and assert via ViewInspector or a smoke test on the model layer.
}
```

Create, declare, wire, test, build. If the project compiles and the new destination pushes, the feature is in.
