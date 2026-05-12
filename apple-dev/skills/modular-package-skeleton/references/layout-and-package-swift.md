# Layout and Package.swift Templates

Concrete on-disk layout for a modular SwiftUI app, plus two `Package.swift` templates: one for an infrastructure package (no main-actor isolation) and one for a feature UI package (main-actor by default).

## On-disk layout

```
MyApp/
  App/                          thin Xcode app target
    MyAppApp.swift              @main, builds the root scene
    Destinations/
      AppDestinations.swift     switch over RouterDestination -> View
      SheetDestinations.swift   switch over SheetDestination  -> View
    Assets.xcassets
    MyApp.entitlements
  Packages/
    Models/
      Package.swift
      Sources/Models/
      Tests/ModelsTests/
    Network/
      Package.swift
      Sources/Network/
      Tests/NetworkTests/
    Env/
      Package.swift
      Sources/Env/              Router, CurrentUser, services
      Tests/EnvTests/
    DesignSystem/
      Package.swift
      Sources/DesignSystem/     Theme, fonts, atoms, modifiers
      Tests/DesignSystemTests/
    Timeline/                   one feature per package
      Package.swift
      Sources/Timeline/
      Tests/TimelineTests/
    Profile/
      Package.swift
    Settings/
      Package.swift
  MyApp.xcodeproj
  MyApp.xctestplan
```

The app target consumes every feature package plus DesignSystem. Each feature package consumes Env, Network, Models, and DesignSystem. None of the feature packages import each other.

## Infrastructure package template (Models / Network / Env)

Infra packages stay actor-agnostic so they can be called from anywhere. They do not add main-actor isolation.

```swift
// Packages/Network/Package.swift
// swift-tools-version: 6.0
import PackageDescription

let package = Package(
  name: "Network",
  platforms: [
    .iOS(.v17),
    .macOS(.v14),
    .visionOS(.v1),
  ],
  products: [
    .library(name: "Network", targets: ["Network"]),
  ],
  dependencies: [
    .package(path: "../Models"),
  ],
  targets: [
    .target(
      name: "Network",
      dependencies: ["Models"],
      swiftSettings: [
        .swiftLanguageMode(.v6),
      ]
    ),
    .testTarget(
      name: "NetworkTests",
      dependencies: ["Network"]
    ),
  ]
)
```

Models is even simpler: drop the `dependencies` array entirely and import only Foundation in its sources.

## Feature package template (UI layer)

Feature packages opt into main-actor isolation by default for the whole target. This lets every view, observable service binding, and view-modifier stay on the main actor without per-type annotations.

```swift
// Packages/Timeline/Package.swift
// swift-tools-version: 6.0
import PackageDescription

let package = Package(
  name: "Timeline",
  platforms: [
    .iOS(.v17),
    .macOS(.v14),
    .visionOS(.v1),
  ],
  products: [
    .library(name: "Timeline", targets: ["Timeline"]),
  ],
  dependencies: [
    .package(path: "../Models"),
    .package(path: "../Network"),
    .package(path: "../Env"),
    .package(path: "../DesignSystem"),
  ],
  targets: [
    .target(
      name: "Timeline",
      dependencies: [
        "Models",
        "Network",
        "Env",
        "DesignSystem",
      ],
      swiftSettings: [
        .swiftLanguageMode(.v6),
        .defaultIsolation(MainActor.self),
      ]
    ),
    .testTarget(
      name: "TimelineTests",
      dependencies: ["Timeline"]
    ),
  ]
)
```

Same shape for `Profile`, `Settings`, etc. The dependency list is the only thing that changes between feature packages, and it stays short. If a feature wants types from another feature, that is a signal to lift the shared type up into Models or Env, not to add a feature-to-feature edge.

## Why two templates

The split (no isolation for infra, main actor for UI) is the load-bearing concurrency choice. UI code is implicitly `@MainActor` everywhere; HTTP, parsing, and persistence stay free to run on any actor. Sendable boundaries fall naturally on the package edges.
