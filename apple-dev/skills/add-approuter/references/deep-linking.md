# Deep linking with AppRouter

## URL format

`scheme://host/path1/path2?key=value&other=2`. The host is the first path token (iOS lowercases it). Subsequent `/`-separated tokens are the rest of the path. Query parameters are shared across every destination parsed from the URL; there is no per-segment scoping.

Examples for an app with `case list` and `case detail(id: String)`:

```
myapp://list                  -> [.list]
myapp://detail?id=123         -> [.detail(id: "123")]
myapp://list/detail?id=456    -> [.list, .detail(id: "456")]
```

`myapp://` alone is a no-op and returns `false`.

## Implement `Destination.from`

For each path token the parser calls `from(path:fullPath:parameters:)`. Return `nil` to skip that token (useful for structural prefixes like `users` or `posts`). Return a case to append to the stack.

```swift
enum Destination: DestinationType {
  case list
  case detail(id: String)

  static func from(path: String, fullPath: [String], parameters: [String: String]) -> Destination? {
    switch path {
    case "list":   return .list
    case "detail": return .detail(id: parameters["id"] ?? "unknown")
    default:       return nil
    }
  }
}
```

## Wire `onOpenURL`

```swift
struct RootView: View {
  @State private var router = SimpleRouter<Destination, Sheet>()

  var body: some View {
    NavigationStack(path: $router.path) { /* ... */ }
      .environment(router)
      .onOpenURL { url in router.navigate(to: url) }
  }
}
```

Register the scheme in `Info.plist` under `CFBundleURLTypes`. For universal links (https), add Associated Domains, then forward the URL into `router.navigate(to:)`.

## Building URLs from code

```swift
if let url = URL.deepLink(scheme: "myapp", destinations: [Destination.list]) {
  router.navigate(to: url)
}
```

`URL.deepLink` uses `String(describing:)` on each case, so it only works cleanly for argumentless cases like `.list`. For `case detail(id: String)`, build the URL by hand and pass the `id` as a query parameter:

```swift
var components = URLComponents()
components.scheme = "myapp"
components.host = "detail"
components.queryItems = [URLQueryItem(name: "id", value: "42")]
if let url = components.url { router.navigate(to: url) }
```

## Contextual routing

Same path token, different destination depending on the previous token. The library passes `fullPath: [String]` so `from(...)` can switch on context:

```swift
static func from(path: String, fullPath: [String], parameters: [String: String]) -> Destination? {
  guard let i = fullPath.firstIndex(of: path) else { return nil }
  let previous = i > 0 ? fullPath[i - 1] : nil

  switch (previous, path) {
  case ("users", "detail"): return .userDetail(id: parameters["id"] ?? "unknown")
  case ("posts", "detail"): return .postDetail(id: parameters["id"] ?? "unknown")
  case (_, "list"):         return .list
  case (_, "detail"):       return .detail(id: parameters["id"] ?? "default")
  case (nil, "users"), (nil, "posts"): return nil // structural prefix
  default: return nil
  }
}
```

Now `myapp://users/detail?id=u1` resolves to `.userDetail(id: "u1")` and `myapp://posts/detail?id=p1` to `.postDetail(id: "p1")`.

Caveat: `fullPath.firstIndex(of: path)` finds the first match. URLs with a repeated token like `myapp://detail/detail` give both calls the same `previous`. If you need true positional context, that is a known gap.

## Reading the active tab from a child

```swift
struct DeepLinkAwareView: View {
  @Environment(\.currentTab) private var currentTab: (any TabType)?
  var body: some View { Text("Tab: \(String(describing: currentTab))") }
}
```

Set it on the root: `.environment(\.currentTab, router.selectedTab)`.

## Limits to plan around

- Sheets are not part of the URL parser. You cannot deep-link directly to a sheet; push a destination and present the sheet from its view, or read query parameters and call `router.presentSheet(...)` after `navigate(to:)`.
- `Router.navigate(to: url)` always writes into `selectedTab`. To land in another tab, set `router.selectedTab` first (parse the tab yourself from the URL host, then call `navigate(to:)`).
- A path token whose `from(...)` returns `nil` is silently skipped. An entirely-skipped URL returns `false` and leaves the router untouched.
- Query parameters are global to the URL, not per segment. Namespace them (`userId`, `postId`) when one URL fans out into several destinations.
