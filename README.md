<!--
“PrOMMiS” was produced under the DOE Process Optimization and Modeling for Minerals Sustainability
(“PrOMMiS”) initiative, and is copyright (c) 2023-2026 by the software owners: The Regents of the
University of California, through Lawrence Berkeley National Laboratory, et al. All rights reserved.
Please see the files COPYRIGHT.md and LICENSE.md for full copyright and license information.
-->

# PSE Skills

Portable Agent Skills for process systems engineering workflows built with
[PrOMMiS](https://prommis.readthedocs.io/en/stable/),
[IDAES](https://idaes-pse.readthedocs.io/en/stable/),
[WaterTAP](https://watertap.readthedocs.io/en/stable/), and
[Flowsheet Inspector](https://github.com/prommis/flowsheet-inspector-lib).

## Available skills

- [`prommis-build-flowsheet`](skills/prommis-build-flowsheet/) — Build or incrementally extend wrapped PrOMMiS, IDAES, and WaterTAP flowsheets from plain-English process descriptions.
- [`prommis-wrap`](skills/prommis-wrap/) — Prepare an existing flowsheet for Flowsheet Inspector.
- [`prommis-change-value`](skills/prommis-change-value/) — Change an operating-condition or parameter value in a flowsheet.
- [`prommis-help-imports`](skills/prommis-help-imports/) — Resolve imports from installed PrOMMiS, IDAES, WaterTAP, Pyomo, and Flowsheet Inspector packages.
- [`prommis-explain-diagnostics`](skills/prommis-explain-diagnostics/) — Run and explain IDAES, IPOPT, and flowsheet diagnostics.

## Getting started

Install a current [Node.js LTS release](https://nodejs.org/), which includes `npm` and `npx`.

Install all skills globally and select the target agents interactively:

```shell
npx skills add prommis/pse-skills --skill '*' -g
```

Verify the installation:

```shell
npx skills list -g
```

Agent Skills and scientific modeling software are installed separately. See the
[complete setup guide](docs/getting-started.md) for installation options, Python
environment requirements, solver setup, and verification commands.

Because this repository is currently private, users must have access to the repository and be authenticated with GitHub.

## Updating

Update the installed global skills:

```shell
npx skills update -g
```

Rerun the installation command with `--skill '*'` when new skills have been added to the repository.

## Repository structure

Each directory under `skills/` is an independently installable Agent Skill and is the canonical source for that skill. Supporting agent resources are stored inside the relevant skill’s `references/`, `scripts/`, and `assets/` directories.

Human-facing installation and setup documentation is stored in [`docs/`](docs/).

See the [skills CLI documentation](https://github.com/vercel-labs/skills) for additional installation options and supported agents.

## Author

Tanushree Subramanian

## Copyright and license

See [COPYRIGHT.md](COPYRIGHT.md) and [LICENSE.md](LICENSE.md) for copyright and license information.
