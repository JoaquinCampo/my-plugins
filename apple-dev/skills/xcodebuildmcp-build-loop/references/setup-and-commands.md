# Setup and Commands

Concrete shapes for the XcodeBuildMCP tools the build loop relies on. All names below are the actual MCP tool names; arguments are the practical minimum.

## Verifying the MCP is connected

In a fresh session, list available tools. You should see names that start with `mcp__XcodeBuildMCP__`. If they are missing:

1. Confirm the server is registered in your MCP config (`~/.claude/settings.json` or project `.mcp.json`).
2. Confirm the command resolves on your `PATH` (run `npx -y xcodebuildmcp --help` in a terminal).
3. Restart Claude Code so MCP servers re-spawn.
4. Check the MCP server log for spawn errors.

## Discovering schemes

Before building, learn what schemes the project exposes.

```text
mcp__XcodeBuildMCP__list_schems_proj
  projectPath: "<ABSOLUTE_PATH_TO_XCODEPROJ>"
```

For a workspace, use the workspace variant if available (`list_schems_ws`). The result is a list; pick the app scheme for an app build and the per-package test scheme for tests.

## Per-session defaults

Set the project path and simulator once so later tool calls stay short.

```text
mcp__XcodeBuildMCP__session-set-defaults
  projectPath: "<ABSOLUTE_PATH_TO_XCODEPROJ>"
  simulatorName: "iPhone 16"
```

After this, omit `projectPath` and `simulatorName` from subsequent calls in the same session.

## iOS / iPadOS / visionOS simulator build

The common case.

```text
mcp__XcodeBuildMCP__build_sim_name_proj
  projectPath: "<ABSOLUTE_PATH_TO_XCODEPROJ>"
  scheme: "<APP_SCHEME>"
  simulatorName: "iPhone 16"
```

For a workspace, use the workspace variant (`build_sim_name_ws`) with `workspacePath` instead of `projectPath`.

If the simulator name is wrong, the call fails fast with a clear "simulator not found" message; copy a name from `xcrun simctl list devices available` and retry.

## macOS build

```text
mcp__XcodeBuildMCP__build_mac_proj
  projectPath: "<ABSOLUTE_PATH_TO_XCODEPROJ>"
  scheme: "<APP_SCHEME>"
```

No simulator argument; the scheme's destination handles it.

## Running tests

Tests run per scheme, on a simulator.

```text
mcp__XcodeBuildMCP__test_sim
  projectPath: "<ABSOLUTE_PATH_TO_XCODEPROJ>"
  scheme: "<TEST_SCHEME>"
  simulatorName: "iPhone 16"
```

If `session-set-defaults` was called, only `scheme` is required.

## Multi-package projects

Modular apps ship multiple Swift packages under `Packages/`, each with its own test target. Treat them as independent build / test units:

1. Build the app scheme once to confirm the whole graph links.
2. Then run `test_sim` against each package test scheme that you touched. Do not try to test "everything" in one call; the per-package scheme runs the relevant tests fastest and the failure output is scoped.

For a SwiftPM-only project with no `.xcodeproj`, fall back to `swift build` and `swift test` from a shell. The MCP layer is for `xcodebuild`-driven projects.

## Other useful tools

- `clean_proj` / `clean_ws`: nuke DerivedData for the project when results look stale.
- `show_build_set_proj`: dump effective build settings for a scheme (deployment target, search paths, etc).
- `describe_ui` and `screenshot`: only relevant for runtime UI tests; not part of the basic build loop.

## Argument hygiene

- Always use absolute paths for `projectPath` / `workspacePath`. Relative paths break across MCP re-spawns.
- Simulator names must match `xcrun simctl list devices available` exactly (case and spacing).
- Quote scheme names that contain spaces.
