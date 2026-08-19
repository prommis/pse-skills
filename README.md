# PSE Skills

Portable Agent Skills for flowsheet workflows.

## Skills

- `prommis-wrap` — Wrap flowsheets for Flowsheet Inspector.
- `prommis-change-value` — Change flowsheet parameter values.
- `prommis-help-imports` — Find Python import paths.
- `prommis-explain-diagnostics` — Run and explain flowsheet diagnostics.

## Install

This repository is currently private. Users must have repository access
and authenticate with GitHub before installing.

Install all skills globally and select the target agents interactively:

```shell
npx skills add prommis/pse-skills --skill '*' -g
```

Install all skills for every supported agent:

```shell
npx skills add prommis/pse-skills --all
```

Verify the installation:

```shell
npx skills list -g
```

On Windows PowerShell, use `npx.cmd` instead of `npx` if required by the
local script execution policy.

Each directory under `skills/` is an independently installable Agent
Skill and is the canonical source for that skill.

See the [skills CLI documentation](https://github.com/vercel-labs/skills)
for agent-specific installation options.
