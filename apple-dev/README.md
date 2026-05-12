# apple-dev

A Claude Code plugin bundling modern SwiftUI doctrine and recipes for Apple-platform development (iOS, iPadOS, macOS, visionOS).

Source: distilled from Thomas Ricouard's (@Dimillian) public open-source iOS work, including IceCubesApp, IcySky, FoundationChat, and AppRouter. The plugin extracts universal patterns; no code is copied verbatim.

## Skills

| Skill | When it fires |
|---|---|
| `swiftui-doctrine` | Always-on baseline for Apple-platform Swift work. The 12 core rules: no ViewModels, @Observable, .task over .onAppear, modular SwiftPM, async/await over Combine. |
| `modular-package-skeleton` | Scaffolding a new iOS / macOS app with the canonical SwiftPM module layout (Models, Network, Env, DesignSystem, per-feature UI). |
| `refactor-to-no-viewmodel` | Migrating ObservableObject / MVVM / Combine code to @Observable + view-state enums + async/await. |
| `foundation-models-integration` | Adding Apple Intelligence on-device LLM with @Generable, streaming, tools, error handling. iOS 26+. |
| `add-approuter` | Adopting AppRouter (github.com/dimillian/AppRouter) for type-safe navigation + deep linking. |
| `ios26-liquid-glass-adoption` | Modernizing UI with iOS 26 APIs (glassEffect, ToolbarSpacer, matchedTransitionSource, scrollPosition, contentTransition). |
| `xcodebuildmcp-build-loop` | Wiring XcodeBuildMCP for agent-driven build verification after edits. |
| `swiftui-push-proxy` | Building E2E-encrypted push notifications via a relay proxy + RFC 8291 on-device decryption. |

## Install

This plugin is part of the `my-plugins` marketplace. Install via the standard Claude Code plugin flow:

```
/plugin install apple-dev
```

After install, `swiftui-doctrine` auto-fires when a conversation touches Apple-platform Swift work. The 7 recipe skills load on demand when their narrower triggers match.

## Drop-in project CLAUDE.md

For new SwiftUI projects, the doctrine is also provided as a copy-pasteable project `CLAUDE.md` at the plugin root:

```bash
cp ~/Documents/Personal/my-plugins/apple-dev/CLAUDE.md.template /path/to/your/project/CLAUDE.md
```

Replace placeholders in `{BRACES}` (PROJECT_NAME, PROJECT_PATH, SCHEME, SIMULATOR, PLATFORM_LIST, SDK_VERSION). Delete the iOS 26 and Foundation Models sections if you do not target those features.

This file and `skills/swiftui-doctrine/references/claude-md-template.md` carry the same template content. The reference version has an explanatory wrapper paragraph for in-skill reading; the root version is raw, ready for `cp`. Keep both in sync if you iterate.

## License

MIT.
