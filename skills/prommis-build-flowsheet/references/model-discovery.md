# Model Discovery

Read this reference when creating a new flowsheet or adding a new unit, property package, connection, specification, initialization routine, costing block, or optimization phase.

Generate process-specific code from the user’s requested topology. Do not use a hardcoded catalog of models or copy an entire example flowsheet.

## Discovery Decision Tree

Use this decision tree before adding models or model-specific code. Discovery occurs only within the scope of the current increment or stage. Do not discover models, imports, or configurations for a future increment the user has not yet requested. Apply the Official Example Approval Checkpoint in `SKILL.md` only when its example-discovery conditions are met. Example discovery is optional and must not block ordinary model discovery.

### 1. Select the Python Environment

Reuse an interpreter already confirmed for the current flowsheet and required module set.

If none has been confirmed, run the environment detector once with the complete currently known top-level module list:

    <current-python> <skill-directory>/scripts/detect_flowsheet_environment.py <required-module> [<required-module> ...]

If project configuration identifies another interpreter, include it with `--candidate`. The detector checks the current and project interpreters first and queries Conda only when neither is compatible.

Select a compatible interpreter and reuse its exact executable path for all discovery, file generation, validation, initialization, and solving during the current flowsheet build. Do not perform separate environment searches or repeat detection for an unchanged module list.

If later model discovery introduces another required top-level module, rerun the detector once with the complete expanded module list. If multiple compatible environments are returned and available evidence does not distinguish them, ask the user to choose. If none are compatible, explain the missing package family, link to the [PSE Skills setup guide](https://github.com/prommis/pse-skills/blob/main/docs/getting-started.md), and offer installation help or a clearly marked source-only draft.

Package availability does not prove that model APIs or solvers work; validate those separately. Do not guess environment names, manually search the filesystem for environments, or install dependencies without permission.

### 2. Determine the Required Evidence

For each model required by the current increment:

1. Translate the requested physical operation into the model behavior required.
2. Reuse the Python environment, imports, property packages, APIs, and ports already verified for the current generated file.
3. Discover only models or symbols introduced by the current increment.
4. When one or more import paths are unknown for the current increment, run the import-discovery script exactly once, passing every unresolved symbol name for that increment as separate positional arguments in that single call, for example:

```text
   <selected-python> <skill-directory>/scripts/get_imports.py NaClParameterBlock Feed --package watertap
```
    Do not run this script when every import path for the current increment is already known.
5. Use exactly one Python process for all import, constructor, configuration, variable, and port checks required by the current increment, unless a check depends on the result of an earlier one in the same increment.
6. Determine model selections and implementation details from the user’s requirements, installed public APIs and source, and official package documentation.
7. Prefer a maintained public process-specific property, reaction, or costing configuration when it matches the requested physical assumptions. Do not reconstruct that configuration from unrelated lower-level pieces.
8. Apply the Official Example Approval Checkpoint only when the eligibility conditions defined in `SKILL.md` are met. In Progressive Build, do not search until both eligibility conditions defined in SKILL.md's Official Example Approval Checkpoint are met. A feed-only, property-package-only, or other preparatory increment does not qualify, even if a later increment's process is easy to anticipate. Once eligible, use one bounded installed-example search pass and stop when one relevant candidate is found or the pass produces no relevant candidate.
9. When example use is approved, inspect only the relevant portions and first confirm compatibility with the currently known model family, topology, configurations, and installed APIs. Use the example only for the technical evidence permitted by `SKILL.md`. If it is incompatible, continue without it.

Do not compare multiple weak example candidates, repeatedly broaden the search, or treat absence of an example as missing scientific evidence. Continue with installed public APIs, official documentation, and the user's requirements.

When a selected property package or unit model provides a supported public method for calculating a state or physical quantity, use that method. Do not manually reconstruct thermodynamic, transport, reaction, or costing equations from internal parameters unless the user explicitly requests a custom formulation or no supported public operation exists.

Treat results from temporary discovery probes as verification evidence, not as model inputs. Trace each important numerical value to a user-specified input, documented model constant or default, or visible calculation from named inputs.

When a value is derived from other inputs, calculate it in the generated flowsheet using a supported public package or unit-model operation. For simple algebra explicitly required by the user or authoritative documentation, use a Pyomo `Expression` or `Constraint`, or calculate it during the appropriate runtime step. Do not use this fallback to recreate scientific equations already provided by the selected package.

Do not paste a probe's numerical result into a `Param`, `.fix()`, or initialization value unless that value is explicitly requested by the user or documented as a fixed constant or initialization value. A user-requested fixed snapshot remains allowed.

Do not repeat successful discovery unless the generated file, selected environment, package family, or required model behavior has changed. 

### 3. Execute Efficiently

Use exactly one Python process for all import and API checks required by the current increment, unless a check depends on the result of an earlier one in the same increment. Do not open or read the same file more than once for a single increment's discovery. Stop discovery as soon as the required imports and interfaces are verified.

### 4. Complete the Build Stage

After any required Official Example Approval Checkpoint is resolved, insert the verified code, run the applicable validation, and follow the reporting behavior of the selected interaction mode. Do not otherwise pause after discovery unless the build is blocked.

## Describe the Requested Process

Convert the user’s prompt into a working process specification:

- required unit operations;
- material and energy connections;
- feeds, products, and waste streams;
- splits, mixing points, and recycle loops;
- requested operating conditions;
- requested costing or optimization;
- decisions that remain unspecified.

Preserve the user’s terminology while translating each requested operation into the physical behavior a model must provide.

Ask a question only when an unresolved choice would materially change the process, property basis, or model fidelity. Otherwise, make a source-supported assumption and report it.

## Detect the Runtime Environment

Perform discovery using the Python environment that will run the flowsheet.

Determine package availability and source locations dynamically from:

- the active Python environment;
- the current project configuration;
- importable package metadata; and
- imports already present when extending a generated flowsheet.

Do not assume local installation paths, environment names, or installed package versions.

Prefer models available in the current environment. Do not add or install dependencies unless the user requests it.

## Evidence Order

Use implementation evidence in this order:

1. Installed public model APIs and source.
2. Current official package documentation.
3. User-approved maintained official examples.
4. Package tests as supporting API evidence.
5. User-approved existing compatible local flowsheets.

Package tests may be inspected when the earlier evidence does not establish a required interface. Generated flowsheets must not import models, property packages, configurations, or utilities from test-only modules or fixture namespaces.

An importable public property, reaction, or costing configuration may be reused when it matches the requested physical assumptions. Do not treat a complete flowsheet or its build helpers as a reusable configuration.

When approved, an official example may confirm property-package selection, unit configuration, scaling targets, initialization methods, costing interfaces, solver behavior, and execution order. It does not determine the process design and must not be copied wholesale.

If neither public documentation nor an approved maintained example establishes a required scaling method, initialization strategy, or execution dependency, use a supported documented default when available. Otherwise, report the unresolved choice instead of inventing numerical guesses, solver settings, or staged initialization procedures.

A successful import is not sufficient evidence that a model is scientifically appropriate. Confirm the model’s components, phases, state basis, physical assumptions, and compatibility with the requested units.

If no supported public import path or scientifically appropriate configuration is available, report the limitation instead of silently using test code or constructing an approximation. Use a test-only dependency or an approximate substitute only when the user explicitly accepts it.

## Discover Candidate Models

For each requested process function:

1. Search the available packages using terms derived from the requested physical operation.
2. Identify candidate unit models and property packages.
3. Locate their public import paths.
4. Inspect only the constructor options, ports, state basis, and public methods required by the requested flowsheet. Consult package tests only when public source and documentation do not establish a required interface.
5. Reject candidates that are unavailable, incompatible, or do not represent the requested behavior.

Do not assume a class name, module path, port name, configuration option, or method from memory.

Do not create a permanent model catalog in this skill. Repeat discovery against the installed environment so package updates can be handled without rewriting the skill.

## Verify New or Uncertain Model Details

Before inserting a new or changed model, verify only the details required by the current flowsheet:

- its supported public import path;
- the constructor options actually being used;
- the inlet and outlet ports actually being connected;
- its compatibility with the selected property package; and
- the specifications required by the requested operation.

Verify scaling, initialization, solver, costing, or optimization interfaces only when the current request includes those operations or the selected model requires them to function.

Reuse details already verified for the current generated file. Group related checks into one Python process and stop when the required interfaces are confirmed. Do not enumerate every configuration option, variable, method, or solver feature exposed by the model.

## Verify Property Compatibility

Choose property packages based on the requested chemistry, phases, components, and unit-model requirements.

Do not construct a property or reaction package by combining configurations from different processes merely because the required components are present. Matching component names alone does not establish compatible thermodynamics, phase behavior, reaction behavior, units, or parameter data.

Use a custom or composed configuration when its construction is supported by authoritative model documentation or explicitly requested by the user. Otherwise, prefer a maintained public configuration that satisfies the requested behavior or stop and report the unresolved model choice.

Before connecting units, verify that their ports expose compatible state variables, phases, and component sets.

Do not assume that two objects named `inlet` and `outlet` are compatible.

If adjacent models require incompatible property representations, search for a supported translator, separator, mixer, state junction, or other interface model. Add one only when required by the selected APIs or requested process.

If no supported interface can be found, report the incompatibility instead of inventing a connection.

## Select Among Candidates

Choose the smallest compatible collection of models that satisfies the requested process.

Prefer candidates that:

- represent the requested physical behavior;
- use compatible property definitions;
- expose the required connection points;
- have a supported initialization path;
- match the requested level of fidelity; and
- are supported by installed source, tests, or maintained documentation.

Do not select a candidate only because its name resembles the user’s wording.

When multiple candidates would materially change fidelity, assumptions, or results, explain the alternatives and obtain the user’s choice. For minor implementation differences, choose the strongest-supported option and report the assumption.

## Add Code Incrementally

When adding a model, add only the code required for that increment:

1. Add its verified import.
2. Add or reuse a compatible property package.
3. Construct the unit with verified configuration.
4. Add connections using verified ports.
5. Add required specifications.
6. Add required scaling and initialization behavior.
7. Reconcile wrapper steps and execution order.
8. Run the applicable validation level.

Place discovered code into the canonical structure:

- imports in the import section;
- property packages in `add_property_packages()`;
- unit models in `add_units()`;
- arcs and other connections in `connect_units()`;
- operating specifications in the appropriate helper or step;
- scaling in the appropriate helper or step;
- initialization in an existing phase or a separate phase when required;
- costing and optimization only when requested or required.

Add imports when their associated model or API is added. Remove an import only when it is no longer used by the generated flowsheet.

## Extend an Existing Generated Flowsheet

For a follow-up request:

1. Read the current generated file.
2. Recover its existing units, property packages, connections, and runtime phases.
3. Preserve existing compatible choices.
4. Discover only the APIs required for the requested increment.
5. Modify only the affected imports, helpers, units, connections, and execution phases.
6. Recheck the complete topology and wrapper.

Do not copy the canonical template again or rebuild unaffected sections.

## Handle Missing Evidence

Never invent an import, configuration option, port, variable, initialization method, or solver requirement.

Do not replace missing scientific evidence with a plausible-looking combination of unrelated installed models.

When reliable evidence cannot be found:

1. State what was successfully verified.
2. Identify the unresolved model or compatibility decision.
3. Provide the strongest supported alternative, if one exists.
4. Stop before inserting speculative code.

## Continue With Other References

- Read `recycle-building.md` when the topology contains a recycle loop.
- Read `wrapper-integrity.md` whenever functions or runtime phases change.
- Read `validation.md` after each meaningful increment.