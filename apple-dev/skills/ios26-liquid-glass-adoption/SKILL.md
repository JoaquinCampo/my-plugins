---
name: ios26-liquid-glass-adoption
description: Adopt iOS 26 / iPadOS 26 / macOS 26 SwiftUI APIs: Liquid Glass, modernized toolbars and tab bars, matched transitions, scroll position. Triggers: `glassEffect`, `buttonStyle(.glass)`, `ToolbarSpacer`, `matchedTransitionSource`, `tabBarMinimizeBehavior`.
---

# iOS 26 Liquid Glass Adoption

## When this applies

UI work on a project that already targets iOS 26+, or work to upgrade an existing iOS 17 / iOS 18 codebase to feel native on iOS 26. Pure logic and Model layers are out of scope.

## Prerequisite

Deployment target must be iOS 26 / iPadOS 26 / macOS 26, with Xcode 26+. None of these APIs are back-deployable; do not wrap them in `if #available` to ship on older OSes. Bump the Package.swift platforms tuple (and the Xcode project minimum deployment target) before touching call sites.

## What's actually new and worth adopting

1. **Glass surfaces**: `glassEffect(_:in:isEnabled:)` for translucent shapes, `GlassEffectContainer` for sibling glass shapes that morph into each other, and `buttonStyle(.glass)` for primary CTAs and toolbar buttons. Replaces ad-hoc `.background(.ultraThinMaterial)` and `.borderedProminent`.
2. **Toolbars and tab bars**: `ToolbarSpacer` as first-class `ToolbarContent` (not `Spacer()` in a `ToolbarItem`), `tabBarMinimizeBehavior(.onScrollDown)` to collapse the tab bar on scroll, and the new `Tab(value:role:content:label:)` initializer with `role: .search` for a dedicated search tab.
3. **Transitions**: `matchedTransitionSource(id:in:)` on a source view paired with `.navigationTransition(.zoom(sourceID:in:))` on the destination, plus `contentTransition(.numericText)` for animated counters.
4. **Scrolling**: `scrollPosition(id:)` with an `Identifiable` binding, `scrollTargetBehavior(.viewAligned)` and `.paging`, and `scrollEdgeEffectStyle(_:for:)` for the new top and bottom edge effects.
5. **Other**: the `@Entry` macro for environment values (replaces the `EnvironmentKey` boilerplate), `symbolEffect(.bounce, value:)` on SF Symbols, two-detent sheets with `presentationDetents([.height(...), .large])` and `presentationBackgroundInteraction(.enabled)`, and `textInputFormattingControlVisibility(.hidden, for: .all)` to suppress the new default formatting strip in `TextEditor`.

## Gotchas

- *Symptom*: `.glassEffect(in:)` renders as a plain background, no translucency. *Cause*: deployment target is still iOS 17 or 18. *Fix*: bump `Package.swift` `.iOS(.v26)` and the Xcode project minimum before touching the call sites; none of these APIs are back-deployable.
- *Symptom*: matched zoom transition snaps instead of animating between the source and destination. *Cause*: source and destination use different `Namespace.ID` instances (each declared its own `@Namespace`). *Fix*: declare the namespace once at the parent and propagate it via the navigation value, sheet payload, or destination enum.
- *Symptom*: two adjacent glass shapes flicker independently when one expands or contracts. *Cause*: each shape owns its own glass surface, so they cannot morph. *Fix*: wrap them in a `GlassEffectContainer` and animate the parent state.
- *Symptom*: `contentTransition(.numericText)` animation jitters, digits reflow. *Cause*: no `.monospacedDigit()` on the label. *Fix*: add `.monospacedDigit()` adjacent to the `contentTransition` modifier; drive with `.animation(.smooth, value: count)`.
- *Symptom*: tab bar does not collapse on scroll. *Cause*: `.tabBarMinimizeBehavior` is attached to a child view, not the `TabView`. *Fix*: attach the modifier directly to the `TabView`.

## Adoption order

1. Bump deployment target to 26 in `Package.swift` and the Xcode project. Verify the project still builds and the simulator launches.
2. Apply `.glassEffect(in:)` to elevated surfaces (toolbars, floating search fields, action chips). Swap primary CTAs from `.borderedProminent` to `.buttonStyle(.glass)`.
3. Add `ToolbarSpacer` to break dense toolbars into visual groups (especially keyboard toolbars).
4. Wire `matchedTransitionSource` on list cells or thumbnails, and `.navigationTransition(.zoom(sourceID:in:))` on the destination view that the cell pushes or presents.
5. Replace deprecated `.tabItem` usages with the new `Tab(value:role:content:label:)` API. Add `.tabBarMinimizeBehavior(.onScrollDown)` to the `TabView`.

## What to skip (advertised but rarely needed)

- `backgroundExtensionEffect()`: niche, only useful for content that should bleed under bars.
- `@Animatable` macro: only relevant if you write custom `Animatable` shapes; default SwiftUI animation already covers most cases.
- `WebView` / `WebPage`: only when you need a full web view embedded; do not adopt for one-off links.

## Deep dives in references/

- `references/glass-and-toolbar.md`: glass effects, `GlassEffectContainer`, toolbar and tab bar adoption.
- `references/transitions-and-scroll.md`: matched transitions, scroll position and edge effects, symbol effects, `@Entry`.
