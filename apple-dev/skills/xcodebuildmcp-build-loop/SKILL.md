---
name: xcodebuildmcp-build-loop
description: Set up and use XcodeBuildMCP to compile and test Xcode projects after Swift edits. Use after any edit to a `.xcodeproj` or `Package.swift`. Triggers on `xcodebuild`, simulator build, build verification, agent-driven iOS development.
---

# XcodeBuildMCP Build Loop

The build is the test. After any non-trivial Swift edit, compile the project end to end on a real simulator (or macOS scheme) through XcodeBuildMCP. Fix failures before continuing. Type checker passing is not enough.

## When this applies

Any task that edits Swift, SwiftUI, `Package.swift`, asset catalogs, or Xcode project settings in a repo built with `xcodebuild` (`.xcodeproj` or `.xcworkspace`). Skip only for pure docs or non-Swift changes.

## Why

The Swift type checker passes long before the project actually links. SwiftUI semantics, `@Observable` registration, `Sendable` and `MainActor` isolation, package dependency resolution, and platform availability gates only fail at the full build or at runtime. A green editor with a red `xcodebuild` is a regression you will ship.

## Install

1. Install the MCP server: `npm install -g xcodebuildmcp` (or use `npx xcodebuildmcp` from the MCP config).
2. Register it in your Claude Code MCP config (`~/.claude/settings.json` or `.mcp.json`). Use the package's documented `command` and `args` (typically `npx -y xcodebuildmcp`).
3. Reload Claude Code. Verify that tools named `mcp__XcodeBuildMCP__*` appear. If not, the MCP did not start; see `references/setup-and-commands.md`.

## The build loop

1. Edit the Swift source.
2. Build: call `mcp__XcodeBuildMCP__build_sim_name_proj` for iOS / iPadOS / visionOS simulators, or `build_mac_proj` for macOS. Pass `projectPath`, `scheme`, `simulatorName` (for sim builds).
3. If the build fails, read the diagnostic, fix the smallest thing that resolves it, and rebuild. Do not move on with red.
4. When the build is green, run tests with `mcp__XcodeBuildMCP__test_sim` against the relevant per-package test scheme.
5. Only then declare the task complete.

## Per-session setup

Once per session, set defaults so subsequent calls stay short:

```text
mcp__XcodeBuildMCP__session-set-defaults
  projectPath: "<ABSOLUTE_PATH_TO_XCODEPROJ>"
  simulatorName: "iPhone 16"
```

Then later calls can omit `projectPath` and `simulatorName`.

If you do not know the scheme name, list schemes first with `mcp__XcodeBuildMCP__list_schems_proj`.

## When to invoke

- After ANY edit to a Swift file or `Package.swift`.
- Before declaring a task complete or claiming "the code is correct".
- After bumping the deployment target or changing build settings.
- After adding a package dependency or moving files between targets.
- Before opening a PR or committing.

## Gotchas

- *Symptom*: `mcp__XcodeBuildMCP__*` tools do not appear in the session. *Cause*: the MCP server did not start. *Fix*: check the registration in `~/.claude/settings.json` (or `.mcp.json`), run `npx -y xcodebuildmcp --help` in a shell to verify the binary resolves, then restart Claude Code.
- *Symptom*: build fails with `No such module 'X'`. *Cause*: the target imports `X` but does not depend on the package that vends it. *Fix*: add the missing `.product(name: "X", package: "X")` to `target.dependencies` in `Package.swift`.
- *Symptom*: build fails with "Unable to find a device matching the provided destination specifier". *Cause*: simulator name does not match an installed runtime. *Fix*: `xcrun simctl list devices available`, copy a name verbatim (case, spacing), update `session-set-defaults`.
- *Symptom*: errors that vanish after a `clean_proj`. *Cause*: stale DerivedData (often after a branch switch or deployment-target bump). *Fix*: call `clean_proj` first; if persistent, delete `~/Library/Developer/Xcode/DerivedData/<ProjectHash>`.

Eight more failure modes with fix recipes live in `references/common-errors.md`.

## Deep dives

- `references/setup-and-commands.md`: concrete tool signatures, scheme discovery, multi-package projects, MCP connectivity checks.
- `references/common-errors.md`: one-screen remediation recipes for the recurring `xcodebuild` failure modes.
