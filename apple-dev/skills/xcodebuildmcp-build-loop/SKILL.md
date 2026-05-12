---
name: xcodebuildmcp-build-loop
description: Set up and use XcodeBuildMCP to verify SwiftUI / iOS / macOS builds during agent-driven development. Use when working on an Xcode project where Claude should compile and run tests after edits, instead of stopping at type-checking. Provides the build/test commands and common-error remediation. Triggers on Xcode project, .xcodeproj, simulator build, xcodebuild, build verification, after editing iOS code.
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

## Deep dives

- `references/setup-and-commands.md`: concrete tool signatures, scheme discovery, multi-package projects, MCP connectivity checks.
- `references/common-errors.md`: one-screen remediation recipes for the recurring `xcodebuild` failure modes.
