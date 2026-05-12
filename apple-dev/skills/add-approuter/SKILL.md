---
name: add-approuter
description: Adopt AppRouter (github.com/dimillian/AppRouter) for type-safe SwiftUI navigation with sheets and deep linking. Use when starting an app's nav layer or replacing ad-hoc `NavigationStack` path management. SimpleRouter or tab Router.
---

# Add AppRouter

## When this applies

- Starting a new SwiftUI app and need a navigation layer that survives beyond a single view.
- Refactoring an app where `@State` paths, sheet flags, and tab indices are scattered across views.
- Wanting URL deep links into the navigation stack without hand-rolling a parser.

## When NOT to use it

- Trivial 2-screen apps. A plain `NavigationStack` with local `@State` is enough.
- Apps already on TCA or pointfreeco/swift-navigation. Do not bolt a second router on.
- You need `.fullScreenCover`, multiple simultaneous sheets, or sheets that are part of the URL.

## Install

1. In Xcode, File, Add Package Dependencies, paste `https://github.com/dimillian/AppRouter`, pin from `1.0.0`.
2. Or in `Package.swift`: `.package(url: "https://github.com/dimillian/AppRouter", from: "1.0.0")`.
3. `import AppRouter` in the file that defines your router root.
4. Min platforms: iOS 17, macOS 14, tvOS 17, watchOS 10. Swift 5.9.

## The 4 core types

- `DestinationType`: `Hashable` enum of push destinations. One requirement, `static func from(path:fullPath:parameters:) -> Self?`, used by the URL parser. Return `nil` if you skip deep linking.
- `SheetType`: `Hashable & Identifiable` enum of sheets. No methods. Common pattern, `var id: Int { hashValue }`.
- `TabType`: `Hashable, CaseIterable, Identifiable, Sendable` enum of tabs, with `var icon: String` (SF Symbol). Only needed for `Router`.
- `SimpleRouter<Destination, Sheet>` for one stack. `Router<Tab, Destination, Sheet>` for a tab app with one independent stack per tab.

Both routers are `@Observable @MainActor final class`. Sheets, one slot, shared across tabs in `Router`.

## 3-step adoption playbook

1. Define `enum Destination: DestinationType` and `enum Sheet: SheetType` for the app's navigation vocabulary. Add `enum AppTab: TabType` only if you have tabs.
2. In the root view, hold the router as `@State`. Inject with `.environment(router)`. For tabs, also set `.environment(\.currentTab, router.selectedTab)`.
3. Bind the stack with `NavigationStack(path: $router.path)` (Simple) or `NavigationStack(path: $router[tab])` (tabs). Bind sheets with `.sheet(item: $router.presentedSheet)`. In children, read with `@Environment(SimpleRouter<Destination, Sheet>.self)` and call `router.navigateTo(.foo)` or `router.presentSheet(.bar)`.

## Deep dives in references/

- `references/simple-and-tab-router.md`: full worked examples of `SimpleRouter` and `Router`.
- `references/deep-linking.md`: URL format, `onOpenURL`, contextual routing, parameter limits.

## Gotchas

- *Symptom*: `myapp://users/detail?id=u1` lands on the wrong destination or returns `false`. *Cause*: `URL.deepLink` uses `String(describing:)` per case; only argumentless cases serialize cleanly, and context prefixes silently skip when `from(...)` returns `nil`. *Fix*: build URLs with `URLComponents`, use `fullPath` to disambiguate inside `from(...)`. See `references/deep-linking.md`.
- *Symptom*: presenting a second sheet replaces the first instead of stacking. *Cause*: one sheet slot per router; `presentSheet` overwrites. *Fix*: dismiss first, or push a `NavigationStack` inside the sheet for multi-step flows.
- *Symptom*: `router.navigate(to: url)` lands in the wrong tab. *Cause*: `navigate(to: URL)` always writes into `selectedTab`. *Fix*: set `router.selectedTab` first; parse the tab from the URL host yourself.
- *Symptom*: contextual routing misfires for URLs with repeated tokens like `myapp://detail/detail`. *Cause*: parser uses `fullPath.firstIndex(of: path)` so both calls see the same previous token. *Fix*: known gap, use distinct tokens (`item`, `subitem`) or pass position via a query parameter.
- *Symptom*: `router.navigate(to: url)` returns `false` and nothing happens. *Cause*: every `from(...)` returned `nil`. *Fix*: log the parse result; ensure at least one path token resolves.

## Hard limits

- One sheet slot per router. No sheet stack, no `.fullScreenCover`, no popover.
- Sheets are not URL-addressable. The parser builds `[Destination]` only; present sheets after navigating.
- Query parameters are shared across every destination parsed from a single URL. There is no per-segment scoping.
- No persistence, no animation hooks, no tab-switch callbacks. Wire those yourself.
