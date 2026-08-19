<!--
“PrOMMiS” was produced under the DOE Process Optimization and Modeling for Minerals Sustainability
(“PrOMMiS”) initiative, and is copyright (c) 2023-2026 by the software owners: The Regents of the
University of California, through Lawrence Berkeley National Laboratory, et al. All rights reserved.
Please see the files COPYRIGHT.md and LICENSE.md for full copyright and license information.
-->

# PSE Skills

This repository contains portable Agent Skills for Process Systems
Engineering workflows.

## Skills

- `prommis-wrap` — Wrap flowsheets for Flowsheet Inspector.
- `prommis-change-value` — Change flowsheet parameter values.
- `prommis-help-imports` — Find Python import paths.
- `prommis-explain-diagnostics` — Run and explain flowsheet diagnostics.

## Getting started

### Requirements

Installation uses the [skills CLI](https://github.com/vercel-labs/skills), which places Agent Skills in the correct locations for Codex, Claude Code, Cursor, Gemini CLI, and other supported agents.

Install a current [Node.js LTS release](https://nodejs.org/), which includes `npm` and `npx`. A separate installation of the skills CLI is not required. The first time `npx skills` is run, `npx` retrieves the CLI package and may display a confirmation prompt before executing the requested command.

Confirm that the required commands are available:

```shell
node --version
npm --version
npx --version
```

Because this repository is currently private, users must also have access to the repository and be authenticated with GitHub.

### Installation

#### Install all skills globally for every supported agent

```shell
npx skills add prommis/pse-skills --skill '*' --agent '*' -g
```

#### Install all skills and select the agents interactively

```shell
npx skills add prommis/pse-skills --skill '*' -g
```

#### Install all skills globally for a specific agent

```shell
# Codex
npx skills add prommis/pse-skills --skill '*' -g -a codex

# Claude Code
npx skills add prommis/pse-skills --skill '*' -g -a claude-code

# Cursor
npx skills add prommis/pse-skills --skill '*' -g -a cursor

# Gemini CLI
npx skills add prommis/pse-skills --skill '*' -g -a gemini-cli

# GitHub Copilot
npx skills add prommis/pse-skills --skill '*' -g -a github-copilot
```

#### Install a specific skill

Replace `<skill-name>` and `<agent-name>` with the required skill and agent names.

Install one skill globally for every supported agent:

```shell
npx skills add prommis/pse-skills --skill <skill-name> --agent '*' -g
```

Select the target agents interactively:

```shell
npx skills add prommis/pse-skills --skill <skill-name> -g
```

Install one skill globally for a specific agent:

```shell
npx skills add prommis/pse-skills --skill <skill-name> -g -a <agent-name>
```

#### Verify the installation

```shell
npx skills list -g
```

On Windows PowerShell, use `npx.cmd` instead of `npx` if required by the local script execution policy.

### Updating

Update all currently installed global skills without listing them individually:

```shell
npx skills update -g
```

When new skills are added to this repository, rerun the installation command
with `--skill '*'` to install them as well.

## Repository structure

Each directory under `skills/` is an independently installable Agent Skill and
is the canonical source for that skill. Supporting workflow material belongs in
that skill's `references/`, `scripts/`, or `assets/` directory as needed.

See the [skills CLI documentation](https://github.com/vercel-labs/skills) for
additional installation options and supported agents.

## Author

Tanushree Subramanian

## Copyright and license

See [COPYRIGHT.md](COPYRIGHT.md) and [LICENSE.md](LICENSE.md) for copyright and license information.
