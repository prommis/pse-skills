<!--
“PrOMMiS” was produced under the DOE Process Optimization and Modeling for Minerals Sustainability
(“PrOMMiS”) initiative, and is copyright (c) 2023-2026 by the software owners: The Regents of the
University of California, through Lawrence Berkeley National Laboratory, et al. All rights reserved.
Please see the files COPYRIGHT.md and LICENSE.md for full copyright and license information.
-->

# Getting Started

This guide explains how to install the PSE Agent Skills and prepare the scientific Python environment used to inspect, build, run, and diagnose flowsheets.

Agent Skills and scientific modeling software are separate:

- The Agent Skills provide reusable instructions, templates, and validation utilities to an AI coding agent.
- The scientific Python environment provides the PrOMMiS, IDAES, WaterTAP, Pyomo, Flowsheet Inspector, and solver functionality used by a flowsheet.

Installing an Agent Skill does not install or modify the scientific Python environment.

## 1. Install the Agent Skills

### Requirements

Install a current [Node.js LTS release](https://nodejs.org/). Node.js includes the `npm` and `npx` commands used by the [skills CLI](https://github.com/vercel-labs/skills).

Confirm that the commands are available:

```shell
node --version
npm --version
npx --version
```

Because the PSE Skills repository is currently private, users must also have access to the repository and be authenticated with GitHub.

### Install all skills

Install all skills globally for every supported agent:

```shell
npx skills add prommis/pse-skills --skill '*' --agent '*' -g
```

Install all skills globally and select the target agents interactively:

```shell
npx skills add prommis/pse-skills --skill '*' -g
```

Install all skills globally for a specific agent:

```shell
npx skills add prommis/pse-skills --skill '*' -g -a <agent-name>
```

For example:

```shell
npx skills add prommis/pse-skills --skill '*' -g -a codex
```

### Install one skill

Install one skill globally for a specific agent:

```shell
npx skills add prommis/pse-skills --skill <skill-name> -g -a <agent-name>
```

Install one skill and select the target agents interactively:

```shell
npx skills add prommis/pse-skills --skill <skill-name> -g
```

For example:

```shell
npx skills add prommis/pse-skills --skill prommis-build-flowsheet -g -a codex
```

Each skill directory is independently installable. Installing one skill does not require cloning the complete PSE Skills repository.

On Windows PowerShell, use `npx.cmd` instead of `npx` if the local script execution policy prevents `npx` from running.

### Verify the installation

List the installed global skills:

```shell
npx skills list -g
```

### Update the installation

Update the currently installed global skills:

```shell
npx skills update -g
```

Rerun the installation command with `--skill '*'` when new skills have been added to the repository.

## 2. Prepare the Scientific Python Environment

Use an existing project or organization-provided environment whenever one is available. Activate that environment before starting the AI agent or running a flowsheet command.

A source checkout of PrOMMiS, IDAES, or WaterTAP is not required for standard use. Install the released Python packages by following the official guide for the framework required by the flowsheet.

### Select the appropriate framework

- Use [PrOMMiS](https://prommis.readthedocs.io/en/stable/getting_started.html) for process systems involving critical minerals, rare-earth elements, and other PrOMMiS models. The standard PrOMMiS installation includes its IDAES and WaterTAP dependencies.
- Use [IDAES](https://idaes-pse.readthedocs.io/en/stable/tutorials/getting_started/) for general process systems engineering flowsheets and IDAES unit models.
- Use [WaterTAP](https://watertap.readthedocs.io/en/stable/getting_started.html) for water treatment, desalination, and WaterTAP unit models.
- Install the [Flowsheet Inspector library](https://github.com/prommis/flowsheet-inspector-lib) when a skill must create, wrap, inspect, or validate a Flowsheet Inspector-compatible model.

Follow the selected project’s official installation guide rather than relying on fixed local paths, environment names, or package versions from this repository.

### Install solver extensions

A compatible solver is required to initialize or solve a flowsheet. PrOMMiS, IDAES, and WaterTAP commonly use the solvers distributed through the IDAES extensions.

After activating the scientific Python environment and installing the selected framework, follow the applicable [IDAES installation instructions](https://idaes-pse.readthedocs.io/en/stable/tutorials/getting_started/) for the operating system.

The standard extensions command is:

```shell
idaes get-extensions
```

Additional platform-specific steps may be required. The official IDAES and WaterTAP installation guides are the source of truth for supported platforms and solver installation.

## 3. Requirements by Skill

| Skill | Scientific runtime requirements |
| --- | --- |
| `prommis-change-value` | No modeling packages are required for a source-only edit. The target model’s environment is required if the edited flowsheet is executed. |
| `prommis-help-imports` | Python and the package being searched must be installed in the active environment. |
| `prommis-wrap` | Flowsheet Inspector is required for wrapper validation. The target model’s packages are required to execute the wrapped flowsheet. |
| `prommis-explain-diagnostics` | The target model’s packages, Flowsheet Inspector, IDAES diagnostics, and a compatible solver are required. |
| `prommis-build-flowsheet` | Pyomo, IDAES, Flowsheet Inspector, the requested PrOMMiS or WaterTAP model family, and a compatible solver are required for complete build and solve validation. |

A skill may still perform source-level work when some runtime dependencies are unavailable, but it must report which execution or validation steps could not be completed.

## 4. Verify the Scientific Environment

Run the checks that apply to the installed frameworks.

Verify Pyomo and IDAES:

```shell
python -c "import pyomo, idaes; print('Pyomo and IDAES are available')"
```

Verify PrOMMiS:

```shell
python -c "import prommis; print('PrOMMiS is available')"
```

Verify WaterTAP:

```shell
python -c "import watertap; print('WaterTAP is available')"
```

Verify Flowsheet Inspector:

```shell
python -c "import idaes_fi; print('Flowsheet Inspector is available')"
fi-steps --format text
```

Run the AI agent and the flowsheet commands from the same activated Python environment. This allows the skills to discover installed packages, models, and import paths without relying on hardcoded installation locations.

## 5. Troubleshooting

### A package cannot be imported

Confirm that the intended Python environment is active:

```shell
python -c "import sys; print(sys.executable)"
```

Install the missing package by following its official installation guide, then restart the agent from the activated environment.

### `fi-steps` or `fi-run` is unavailable

Confirm that Flowsheet Inspector is installed in the active environment and that the environment’s executable directory is available to the current terminal.

### A solver is unavailable

Follow the [IDAES solver installation guidance](https://idaes-pse.readthedocs.io/en/stable/tutorials/getting_started/) for the current operating system, then verify the solver from the same activated environment used to run the flowsheet.

### The skill is installed but does not appear in the agent

Verify the installed skills:

```shell
npx skills list -g
```

If necessary, reinstall the skill for the specific agent:

```shell
npx skills add prommis/pse-skills --skill <skill-name> -g -a <agent-name>
```

See the [skills CLI documentation](https://github.com/vercel-labs/skills) for supported agents, installation scopes, and additional troubleshooting information.