# Common Errors and Quick Fixes

Recurring `xcodebuild` failure modes with a 1-3 line fix recipe each. When a build fails, match the error against this list before theorizing.

## "No such module 'X'"

A target imports `X` but does not depend on the package or library that vends it.

Fix:

1. In the consuming target (Xcode target or `Package.swift` `target.dependencies`), add the missing product.
2. For a SwiftPM package: add `.product(name: "X", package: "X")` to the relevant `target`.
3. Rebuild. If still missing, run `clean_proj` and rebuild to clear stale module caches.

## Sendable / actor isolation errors

Examples: "Capture of 'self' with non-Sendable type ... in a `@Sendable` closure", "Call to main actor-isolated ... in a synchronous nonisolated context".

Fix:

1. If the value is read across a `Task` boundary, copy it to a local before the `await` and use the local inside the closure.
2. If a method must run on the main actor, mark it `@MainActor` or hop with `await MainActor.run { ... }`.
3. Do not blanket-mark types `@unchecked Sendable` to silence the diagnostic; that hides real races.

## Availability errors

"'X' is only available in iOS Y.Y or newer".

Fix:

1. If the symbol is genuinely needed, raise the deployment target in the project's General tab and in each `Package.swift` `platforms:` clause.
2. If the project must keep the older floor, gate the call with `if #available(iOS Y, *) { ... } else { fallback }`.
3. Rebuild after editing `Package.swift`; SwiftPM caches resolved versions across builds.

## Linker errors

"Undefined symbol", "duplicate symbol", "framework not found".

Fix:

1. Undefined symbol: the target is missing a framework link (e.g., `import AVFoundation` without `AVFoundation.framework` in "Link Binary With Libraries") or a Swift Package product. Add it to the target's link phase.
2. Duplicate symbol: the same source file is in two targets, or two packages vend the same symbol. Remove the duplicate target membership.
3. Framework not found: a search path is wrong after moving the project; check `FRAMEWORK_SEARCH_PATHS` with `show_build_set_proj`.

## Signing / provisioning errors

"Signing for 'X' requires a development team", "No profiles for ... were found".

Fix:

1. For local dev, set the target's Team to your personal team and use "Sign to Run Locally" or automatic signing.
2. For CI or unattended builds, pass `CODE_SIGNING_ALLOWED=NO` (simulators do not need signing) or configure a manual profile.
3. If only the simulator build is needed, prefer `build_sim_name_proj`; simulator builds skip code signing.

## "Could not find scheme 'X'"

Either the scheme name is wrong or the wrong project / workspace path was passed.

Fix:

1. Run `list_schems_proj` against the project. Copy the scheme name verbatim, including capitalization.
2. If the project is part of a workspace, build through the workspace tool variant (`build_sim_name_ws` with `workspacePath`) instead of `build_sim_name_proj`.
3. Confirm the scheme is shared (Xcode > Manage Schemes > "Shared" checkbox). Unshared schemes are invisible to `xcodebuild`.

## Simulator not found

"Unable to find a device matching the provided destination specifier".

Fix:

1. Run `xcrun simctl list devices available` and copy a name exactly.
2. Newer SDKs require newer simulator runtimes; install the missing iOS runtime via Xcode > Settings > Components.
3. Update `session-set-defaults` with the correct name and retry.

## Stale build / phantom errors

Errors that vanish after a clean. Indicates a DerivedData inconsistency, often after switching branches or bumping deployment targets.

Fix:

1. Call `clean_proj` (or `clean_ws`), then rebuild.
2. If still failing, delete `~/Library/Developer/Xcode/DerivedData/<ProjectHash>` and rebuild.
3. After bumping SwiftPM dependencies, also reset the SwiftPM cache: `rm -rf ~/Library/Caches/org.swift.swiftpm`.
