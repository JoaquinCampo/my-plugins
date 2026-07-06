# dev

Daily-driver development skills, bundled into one install.

## Ships these skills (vendored)

| Skill | Source |
| --- | --- |
| `codebase-design` | [mattpocock/skills](https://github.com/mattpocock/skills) `skills/engineering/codebase-design/` |
| `improve-codebase-architecture` | [mattpocock/skills](https://github.com/mattpocock/skills) `skills/engineering/improve-codebase-architecture/` |
| `grilling` | [mattpocock/skills](https://github.com/mattpocock/skills) `skills/productivity/grilling/` (called by `improve-codebase-architecture`) |
| `python-development` | General Python development skill, authored locally |

The Matt Pocock skills are copied verbatim at commit `6eeb81b`.

## Pulls in (dependencies, not copied)

`pr-review` and `tools` are declared as dependencies, so installing `dev` installs review plus the shared tools bundle.

## Re-sync

Re-run the curl from `mattpocock/skills` at a newer commit, then bump the SHA above.
