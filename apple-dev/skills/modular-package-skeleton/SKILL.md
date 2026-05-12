---
name: modular-package-skeleton
description: Scaffold a new iOS, iPadOS, macOS, or visionOS app with the canonical modular SwiftPM layout (Models, Network, Env, DesignSystem, per-feature UI packages). Use when starting a new SwiftUI app or restructuring a monolithic Xcode project into Swift Packages.
---

# Modular Package Skeleton

The canonical layout for a SwiftUI app that intends to grow past one screen. The Xcode project becomes a thin shell; the real code lives in a tree of small Swift Packages with strict, one-way dependencies.

## When this applies

Starting a fresh iOS, iPadOS, macOS, or visionOS app, or refactoring a single-target monolithic Xcode project into modular packages. Use this before the project sprawls; retrofitting is painful once views and services tangle.

## The package graph

```
                    App target
                        |
        +---------------+---------------+
        v                               v
    Feature pkgs (Timeline, Profile, Settings, ...)
        |          |             |
        v          v             v
       Env    DesignSystem    (optional MediaUI)
        |          ^
        v          |
     Network ------+
        |
        v
      Models
```

Models is the root. DesignSystem is a leaf with no deps but SwiftUI. Features sit on top and never know about each other.

## Dependency rules

1. App -> Features -> Env -> Network -> Models. Never reverse.
2. DesignSystem has no deps except SwiftUI (and optional image/font libs).
3. Feature packages do not import each other; cross-feature navigation lives in the App via a router type.
4. Models has zero deps except Foundation.

## 5-step scaffolding playbook

1. Create the Xcode project as a thin shell with one app target, or pure SwiftPM if no app shell is needed yet.
2. Add a top-level `Packages/` folder; give each module its own `Package.swift`.
3. Wire up DesignSystem first; it is a leaf and validates the toolchain.
4. Add Models, then Network, then Env, in that order. Build between each.
5. Add the first feature package, link it from the app target, and verify the app builds and launches.

## Deep dives in references/

- `references/layout-and-package-swift.md`: folder layout plus a concrete `Package.swift` template for an infra package and a feature package.
- `references/feature-package-recipe.md`: step-by-step recipe for adding a new feature package, wiring its destination into the router, and setting up its test target.

## Anti-patterns

- One mega-package containing models, network, and every UI screen.
- Feature packages importing each other directly instead of going through the App-level router.
- Network response types leaking into UI without a Models translation layer.
- DesignSystem depending on Env or Network (it must stay a pure leaf).
- Skipping the build-between-steps loop; package graphs fail late and loudly.
