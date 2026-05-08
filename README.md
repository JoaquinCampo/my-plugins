# my-plugins

Daily-use Claude Code plugins.

## Install

```
/plugin marketplace add JoaquinCampo/my-plugins
/plugin install <name>@my-plugins
```

See [`.claude-plugin/marketplace.json`](./.claude-plugin/marketplace.json) for the current plugin list.

## Layout

```
my-plugins/
├── .claude-plugin/marketplace.json   # source of truth
├── <local-plugin>/
│   └── .claude-plugin/plugin.json
└── README.md
```

External plugins are referenced by URL in `marketplace.json`; no folder in this repo.

## Adding a plugin

**Local** (in this repo):

1. Create `<name>/.claude-plugin/plugin.json`
2. Add a `skills/`, `agents/`, `commands/`, or `hooks/` subdir
3. Add an entry to `.claude-plugin/marketplace.json` with `"source": "./<name>"`

**External** (someone else's repo with `.claude-plugin/plugin.json` at root):

Add an entry with `"source": { "source": "url", "url": "https://github.com/owner/repo.git" }`.

## License

MIT
