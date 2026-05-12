# Glass surfaces, toolbars, tab bars

Worked examples for the iOS 26 glass and chrome APIs. Adopt only when targeting iOS 26+.

## 1. `glassEffect(in:)` on a shaped background

Use `glassEffect(in:)` instead of `.background(.ultraThinMaterial)` for elevated chips, search fields, floating buttons. Pass any `InsettableShape`.

```swift
HStack {
    Image(systemName: "magnifyingglass")
    TextField("Search", text: $query)
}
.padding(.horizontal, 16)
.padding(.vertical, 10)
.glassEffect(in: Capsule())
```

Standalone icon button:

```swift
Button { dismiss() } label: {
    Image(systemName: "xmark")
        .frame(width: 44, height: 44)
        .foregroundStyle(.secondary)
        .glassEffect(in: Circle())
}
```

## 2. `GlassEffectContainer` for sibling shapes that merge

When two adjacent glass shapes should visually fuse and morph as one expands or collapses (search-as-pill expanding into a bar), wrap them in a `GlassEffectContainer`. Animate the parent state with `.animation(.bouncy, value: isExpanded)`.

```swift
GlassEffectContainer {
    HStack {
        HStack {
            Image(systemName: "magnifyingglass")
            TextField("Search", text: $query)
                .allowsHitTesting(isExpanded)
        }
        .frame(maxWidth: isExpanded ? .infinity : 120)
        .padding()
        .glassEffect(in: Capsule())

        if isExpanded {
            Button { isExpanded = false } label: {
                Image(systemName: "xmark")
                    .frame(width: 44, height: 44)
                    .glassEffect(in: Circle())
            }
        }
    }
}
.animation(.bouncy, value: isExpanded)
```

Without the container the two glass shapes render independently and snap; with the container they morph into and out of each other.

## 3. `buttonStyle(.glass)` for CTAs and chrome

Default replacement for `.borderedProminent` on primary actions and for plain buttons sitting in chrome that should read as glass.

```swift
Button("Sign In") { Task { await viewState.signIn() } }
    .buttonStyle(.glass)
    .controlSize(.large)
```

In a toolbar:

```swift
.toolbar {
    ToolbarItem(placement: .topBarTrailing) {
        Button { dismiss() } label: {
            Image(systemName: "xmark")
        }
        .buttonStyle(.glass)
    }
}
```

Use `.tint(...)` to color the glass; do not combine with custom backgrounds.

## 4. `ToolbarSpacer` between toolbar groups

`ToolbarSpacer` is its own `ToolbarContent`. Do not nest `Spacer()` inside a `ToolbarItem`. It groups items visually on the regular toolbar and on the keyboard accessory.

```swift
.toolbar {
    ToolbarItemGroup(placement: .keyboard) {
        Button { addPhoto() } label: { Image(systemName: "photo") }
        Button { addVideo() } label: { Image(systemName: "film") }
        Button { addCamera() } label: { Image(systemName: "camera") }
    }
    ToolbarSpacer(placement: .keyboard)
    ToolbarItemGroup(placement: .keyboard) {
        Button { addMention() } label: { Image(systemName: "at") }
        Button { addHashtag() } label: { Image(systemName: "number") }
    }
    ToolbarItem(placement: .keyboard) {
        Text("\(remaining)")
            .monospacedDigit()
            .foregroundStyle(remaining < 0 ? .red : .secondary)
    }
}
```

## 5. `tabBarMinimizeBehavior(.onScrollDown)`

Attach to a `TabView` to make the tab bar collapse into a pill when content scrolls down and expand on scroll up. No `safeAreaInsets` math.

```swift
TabView(selection: $selection) {
    ForEach(AppTab.allCases) { tab in
        Tab(value: tab, role: .none) {
            TabRootView(tab: tab)
        } label: {
            Label(tab.title, systemImage: tab.icon)
        }
    }
}
.tabBarMinimizeBehavior(.onScrollDown)
```

## 6. `Tab(value:role: .search)` for search-as-tab

A dedicated search role gets a magnifying-glass affordance and the new search presentation. For a tab that should trigger an action (open a composer sheet) instead of pushing content, give it `role: .search` and intercept selection with `.onChange(of: selection)`, then reset.

```swift
TabView(selection: $selection) {
    Tab(value: AppTab.search, role: .search) {
        SearchRootView()
    } label: {
        Label("Search", systemImage: "magnifyingglass")
    }
}
.onChange(of: selection) { _, new in
    if new == .compose {
        showComposer = true
        selection = previousTab
    }
}
```
