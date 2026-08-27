# Model Discovery

Read this reference when creating a new flowsheet or adding a new unit, property package, connection, specification, initialization routine, costing block, or optimization phase.

Generate process-specific code from the user’s requested topology. Do not use a hardcoded catalog of models or copy an entire example flowsheet.

## Discovery Decision Tree

Use this decision tree before adding models or model-specific code. Discovery is preparation within the current increment or stage, not a separate interaction checkpoint.

### 1. Select the Python Environment

Reuse an environment already confirmed during this build.

If no environment has been confirmed, run the following detector before selecting models or writing model-specific code. Do not continue until its result has been interpreted:

    <current-python> <skill-directory>/scripts/detect_flowsheet_environment.py <required-module> [<required-module> ...]

Pass only the top-level modules required by the canonical wrapper and requested model family. If the project already identifies a Python interpreter, include it with `--candidate`; obtain that path from project configuration, not from the user.

Use a compatible project or current interpreter when available. If exactly one other compatible environment is found, use it. If several remain, present their labels as a short choice. If none are compatible, explain the missing package family, link to the [PSE Skills setup guide](https://github.com/prommis/pse-skills/blob/main/docs/getting-started.md), and offer installation help or a clearly marked source-only draft.

Package availability does not prove that model APIs or solvers work; validate those separately. Do not guess environment names, search the filesystem manually, or install dependencies without permission.

Do not repeat environment discovery for an unchanged module list. If model discovery identifies another required top-level dependency, rerun the detector once with the complete expanded module list. Select an environment that satisfies the complete dependency set; do not substitute a different scientific model merely because the currently selected environment contains only part of that set.

### 2. Determine the Required Evidence

For each model required by the current increment:

1. Translate the requested physical operation into the model behavior required.
2. Reuse the Python environment, imports, property packages, APIs, and ports already verified for the current generated file.
3. Discover only models or symbols introduced by the current increment.
4. When an import path is unknown, run the import-discovery script once and restrict it to the relevant installed package family when known.
5. Group related import, constructor, configuration, variable, and port checks into one Python process when practical.
6. When the request names or clearly matches a documented process, first search for a maintained process-specific configuration or implementation for that process.

7. If a maintained process-specific configuration exists and matches the requested physical assumptions, use it unchanged. Do not reconstruct it from lower-level property, component, reaction, costing, or initialization examples.

8. Compose a custom configuration only when no suitable maintained process-specific configuration exists or the user explicitly requests a custom model. Every custom element must be supported by authoritative documentation or an explicit user specification; otherwise stop and explain what information is missing.

9. Before writing model-specific code, identify the selected configuration’s import path and the evidence that it matches the requested process. Importability alone does not establish scientific suitability.

Do not repeat successful discovery unless the generated file, selected environment, package family, or required model behavior has changed. 

### 3. Execute Efficiently

Group related import and API checks into one Python process when practical. Stop discovery as soon as the required imports and interfaces are verified.

### 4. Complete the Build Stage

Insert the verified code, run the applicable validation, and then follow the reporting behavior of the selected interaction mode. Do not pause after discovery alone unless the build is blocked.

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
3. Maintained official examples from the package provider.
4. Package tests as supporting implementation evidence.
5. Existing compatible local flowsheets.

Tests may be inspected as supporting evidence, but generated flowsheets must not import models, property packages, configurations, or utilities from test-only modules or fixture namespaces.

When a maintained official example represents the same named process, chemistry, or equipment arrangement, use it to identify supported property packages, reaction configurations, unit settings, and initialization patterns. Still generate only the topology and scope requested by the user; do not copy the complete example flowsheet.

A successful import is not sufficient evidence that a model is scientifically appropriate. Confirm the model’s components, phases, state basis, physical assumptions, and compatibility with the requested units.

If no supported public import path or scientifically appropriate configuration is available, report the limitation instead of silently using test code or constructing an approximation. Use a test-only dependency or an approximate substitute only when the user explicitly accepts it.

## Discover Candidate Models

For each requested process function:

1. Search the available packages using terms derived from the requested physical operation.
2. Identify candidate unit models and property packages.
3. Locate their public import paths.
4. Inspect their configuration declarations, ports, state blocks, public methods, and tests.
5. Reject candidates that are unavailable, incompatible, or do not represent the requested behavior.

Do not assume a class name, module path, port name, configuration option, or method from memory.

Do not create a permanent model catalog in this skill. Repeat discovery against the installed environment so package updates can be handled without rewriting the skill.

## Verify Each Selected Model

Before inserting a model, verify:

- exact import path;
- class or factory name;
- required constructor configuration;
- supported property packages;
- inlet and outlet structure;
- state-variable and component basis;
- required operating specifications;
- degrees-of-freedom expectations;
- scaling requirements;
- initialization interface;
- solver requirements;
- any required transformations or supporting blocks.

Distinguish required configuration from optional example-specific choices.

Use documented public APIs where available. Treat private implementation details as a last resort and report when they are unavoidable.

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