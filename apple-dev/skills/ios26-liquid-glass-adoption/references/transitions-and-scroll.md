# Transitions, scrolling, content effects, `@Entry`

Worked examples for the iOS 26 motion, scroll, and environment APIs.

## 1. Matched zoom transition

Pair `matchedTransitionSource(id:in:)` on the source view with `.navigationTransition(.zoom(sourceID:in:))` on the destination. Both sides share the same `Namespace.ID` and the same identifier value. The namespace must be propagated to the destination (through the navigation value, the sheet payload, or a captured closure).

Source side:

```swift
struct ThumbnailGrid: View {
    @Namespace private var namespace
    let items: [MediaItem]

    var body: some View {
        LazyVGrid(columns: columns) {
            ForEach(items) { item in
                Button {
                    presented = .full(items: items, focus: item.id, namespace: namespace)
                } label: {
                    AsyncImage(url: item.thumbURL) { image in
                        image.resizable().scaledToFill()
                    } placeholder: { Color.gray.opacity(0.15) }
                }
                .matchedTransitionSource(id: item.id, in: namespace)
            }
        }
    }
}
```

Destination side (sheet or pushed view):

```swift
struct FullScreenMediaView: View {
    let items: [MediaItem]
    let focus: MediaItem.ID
    let namespace: Namespace.ID

    var body: some View {
        TabView(selection: $current) { /* pager */ }
            .navigationTransition(.zoom(sourceID: focus, in: namespace))
    }
}
```

Stash the `Namespace.ID` into your sheet destination enum so the receiver can rebuild the transition.

## 2. `contentTransition(.numericText)` for counters

Animates digit-level crossfades on numeric labels. Pair with `.monospacedDigit()` to avoid layout jitter and an `.animation(.smooth, value: count)` to drive it.

```swift
Text("\(count)")
    .monospacedDigit()
    .contentTransition(.numericText(value: Double(count)))
    .animation(.smooth, value: count)
```

For like counters, also trigger a symbol effect on the toggle state:

```swift
Image(systemName: liked ? "heart.fill" : "heart")
    .symbolEffect(.bounce, value: liked)
```

## 3. `scrollPosition(id:)` plus `scrollTargetBehavior`

Track the currently visible item by its `Identifiable` id. Combine with `scrollTargetLayout()` inside the lazy stack and `.scrollTargetBehavior(.viewAligned)` (or `.paging`) on the scroll view.

```swift
@State private var visible: MediaItem?

ScrollView(.horizontal, showsIndicators: false) {
    LazyHStack(spacing: 0) {
        ForEach(items) { item in
            MediaPage(item: item)
                .containerRelativeFrame([.horizontal, .vertical])
                .id(item)
        }
    }
    .scrollTargetLayout()
}
.scrollPosition(id: $visible)
.scrollTargetBehavior(.viewAligned)
```

`visible` is now usable downstream (share sheet, save button, analytics).

## 4. `scrollEdgeEffectStyle` for top/bottom edges

Customize the edge effect (fade, soft) on a per-edge basis. Useful for content that bleeds under a glass toolbar.

```swift
ScrollView {
    contentBody
}
.scrollEdgeEffectStyle(.soft, for: .top)
.scrollEdgeEffectStyle(.soft, for: .bottom)
```

Combine with `.contentMargins(.top, 60, for: .scrollContent)` when chrome floats over the content.

## 5. `symbolEffect` on SF Symbols

Drive symbol animations from value changes; keep the modifier next to the symbol.

```swift
Image(systemName: "arrow.clockwise")
    .symbolEffect(.rotate, value: isRefreshing)

Image(systemName: "bell")
    .symbolEffect(.bounce, value: unreadCount)
```

Use `.bounce` for discrete events (tap, like, new message), `.rotate` or `.variableColor` for continuous progress.

## 6. `@Entry` macro for environment values

Replaces the `EnvironmentKey` plus `EnvironmentValues` extension boilerplate. Declare the value directly inside an `EnvironmentValues` extension.

```swift
extension EnvironmentValues {
    @Entry public var isQuote: Bool = false
    @Entry public var hideMoreActions: Bool = false
    @Entry public var currentTab: AppTab = .home
}
```

Consumers stay unchanged:

```swift
struct PostBodyView: View {
    @Environment(\.isQuote) private var isQuote
    var body: some View { /* ... */ }
}
```

Set the value with `.environment(\.isQuote, true)` at the call site. Use this for cross-cutting view-side toggles that do not belong in a model; do not abuse it as a global state container.
