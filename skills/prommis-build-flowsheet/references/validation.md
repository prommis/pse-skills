# Incremental Flowsheet Validation

Read and follow this reference after any edit that adds, removes, or changes an import, property package, unit model, connection, operating condition, scaling operation, initialization routine, costing block, optimization logic, decorated step, or runner sequence.

Validation is not required for comments or formatting-only changes.

Choose the validation cadence from the interaction mode.

In Progressive Build and Guided Build, run the checks applicable to the completed increment or checkpoint before continuing.

In End-to-End Build, batch the requested implementation first, run static import and wrapper checks once, and execute the smallest runtime sequence that validates the completed scope. A successful `fi-run` through a later step also validates execution of every earlier runner step included in that run when their source has not changed. Do not run separate build, initialization, simulation, costing, and optimization commands when one later run already executes the same unchanged prefix.

Use an intermediate runtime check only when an uncertain earlier phase must be verified before dependent code can be implemented, or when a failure must be isolated. After a successful final runtime check, do not execute the model again merely for a conformance or reporting pass unless the source changed.

Use quiet mode only when numerical console output is not required. When the user requests solved, costed, or optimized results, capture validation and reporting from the same final non-quiet run. Do not solve the model again solely because quiet mode hid its output.

## Running the Helpers

All required helper scripts are included in this skill’s `scripts/` directory.

Run them using the same Python interpreter selected for the generated flowsheet:

```text
<selected-python> <skill-directory>/scripts/<script-name>.py
```

`<skill-directory>` is the installed directory containing this `SKILL.md`.

The validation workflow does not require a cloned `pse-skills` repository or another installed skill.

If a required helper, package, command, solver, or environment is unavailable, stop that validation level and report it as not verified.

## Select the Applicable Checks

Use the smallest validation set that covers the change, and no other level. Do not run a validation level not listed below for the current change type, even if it seems informative. Do not repeat an unchanged execution prefix already covered by a successful later-stage run:

- Import added or changed: run Import Validation.
- Decorator, execution step, helper function, or runner order changed: run Wrapper Validation.
- Property package, unit, port, `Arc`, or transformation changed: run Build Validation.
- Process connection or specification changed: run Topology and Degrees-of-Freedom Validation.
- Operating condition or scaling changed: run through the affected execution step.
- Initialization changed: run through the initialization step.
- Recycle changed: validate the once-through model, then the closed loop and its initialization.
- Solve logic changed: run through the affected solve step.
- Costing or optimization changed: run once through the deepest affected costing or optimization step. That run also validates its unchanged execution prefix.

In End-to-End Build, these bullets define the coverage required from validation; they do not require separate runtime commands. Use one run through the deepest requested step when that run executes the unchanged earlier steps.

Do not attempt a later validation level after an earlier required level fails.

## Import Validation

When an import required by the current increment has not already been verified for this generated file, discover it using the commands below.

The import verifier rejects imports from test-only modules and fixture namespaces by default. A test import succeeding does not establish that it is a supported public API.

Run:

```text
<selected-python> <skill-directory>/scripts/get_imports.py <symbol-name>
```

When the package family is already known, limit the search:

```text
<selected-python> <skill-directory>/scripts/get_imports.py <symbol-name> --package <package-root>
```

Repeat `--package` when more than one package root must be searched.

If the script returns multiple matches, select among them using:

- the generated flowsheet’s model family;
- the required physical behavior;
- property-package compatibility;
- neighboring imports;
- installed model configuration and APIs.

Do not choose a match from its name alone.

After inserting imports, run:

```text
<selected-python> <skill-directory>/scripts/verify_file_imports.py <flowsheet.py> <module> <symbol> [<module> <symbol> ...]
```

Include every import added during the current increment.

Use `--allow-test-only` only when the user explicitly accepts a test-only dependency:

```text
<selected-python> <skill-directory>/scripts/verify_file_imports.py <flowsheet.py> <module> <symbol> [<module> <symbol> ...] --allow-test-only
```

Passing this check establishes that:

- the generated file has valid Python syntax;
- every specified import is present;
- every specified import occurs exactly once;
- the file contains no test-only or fixture imports unless explicitly allowed.

It does not establish that the complete module imports successfully or that the model builds.

## Wrapper Validation

The canonical asset activates only `build`; its optional phase functions begin as plain helpers.

Before validating the wrapper, remove unused decorated placeholder functions and their runner entries, add any required phases, and ensure the sequence contains every remaining decorated execution step exactly once in dependency order:

```python
FS = FlowsheetRunner(
    steps=(
        "build",
        "set_solver",
        # Additional applicable steps
    )
)
```

Run:

```text
<selected-python> <skill-directory>/scripts/check_wrapper.py <flowsheet.py>
```

Passing this check establishes that:

- the file has valid Python syntax;
- exactly one assigned `FlowsheetRunner` exists;
- the runner has an explicit step sequence;
- decorated step names are valid in the installed Flowsheet Inspector environment;
- decorated step names are not duplicated;
- every decorated step appears exactly once in the runner sequence;
- every runner entry resolves to a decorated step;
- the `__main__` guard calls that runner’s `run_steps()`.

This is a static check. It does not import, build, initialize, or solve the flowsheet.

## Build Validation

When `build` is the deepest required checkpoint, or when an uncertain build failure must be isolated, construct a fresh model by running through `build`. In End-to-End Build, do not run this separately when the final deeper run will execute the same unchanged build step:

```text
fi-run <flowsheet.py> --last build --skip-db-test -q
```

Run `fi-run` from the same environment selected for the flowsheet.

Passing this check establishes that:

- all top-level imports executed;
- property packages could be constructed;
- unit models accepted their configuration;
- referenced ports exist;
- declared `Arc` objects could be created;
- requested network transformations completed.

It does not establish correct operating conditions, degrees of freedom, initialization, or solve behavior.

Never reuse a live model after changing the source-level topology. Run a fresh build.

## Topology and Degrees-of-Freedom Validation

Reuse the model constructed during Build Validation when it remains available. Do not construct another identical model solely to repeat unit, port, Arc, or degrees-of-freedom checks.

For a Progressive Build increment or an incomplete Guided Build stage, report the current degrees of freedom as informational. Do not add specifications or attempt initialization or solving merely to obtain zero degrees of freedom.

Inspect the freshly built model and confirm that:

- every requested unit is present;
- every requested process connection is represented;
- every `Arc` uses verified source and destination ports;
- network expansion occurs after all arcs are declared;
- connected ports expose compatible state variables, phases, components, indices, and units;
- feed, product, waste, split, mixing, recycle, purge, and bypass paths match the requested process;
- required translators or interface models are present when property representations differ.

Use the installed IDAES `degrees_of_freedom` API on the built model.

Determine the expected degrees of freedom from:

- the current execution phase;
- user-provided operating conditions;
- required unit-model specifications;
- selected property-package requirements;
- optimization decisions that intentionally remain free.

Do not require zero degrees of freedom at every phase. Nonzero degrees of freedom may be expected before operating conditions are applied or after optimization variables are unfixed.

A successful build, expanded network, or generated diagram does not by itself prove that the topology or specifications are physically correct.

## Operating Conditions and Scaling Validation

When the affected operating-condition or scaling step is the deepest required checkpoint, or when that phase must be isolated, run through the latest affected decorated step. In End-to-End Build, do not run it separately when the final deeper run includes the same unchanged step:

```text
fi-run <flowsheet.py> --last <affected-step-name> --skip-db-test -q
```

Confirm that:

- required variables are fixed or unfixed as intended;
- values use the correct units and indices;
- component, phase, and time indices match the selected property package;
- scaling calls reference objects that exist;
- scaling values follow the selected model’s supported guidance;
- every scaling target and value or formula is supported by the user’s request, installed public APIs, or official documentation;
- scaling is applied only after its required objects and input values exist;
- scaling, specification, initialization, costing, and solving follow their verified dependency order;
- any implementation choice not uniquely prescribed by the available evidence is validated and reported as an assumption;
- degrees of freedom are appropriate after the specifications are applied.

Do not introduce numerical values only to make a validation check pass.

## Source Conformance

For every build, validate the generated flowsheet against the user's supplied requirements and the installed public APIs. Confirm that no unrequested topology, values, configurations, costing decisions, optimization decisions, or reporting were inherited from another flowsheet, or inferred from a filename, destination path, or anticipated future topology, per the Scope Discipline rule in SKILL.md.

Confirm that:

- each important numerical value comes from a user requirement, documented model constant or default, or visible calculation from named inputs;
- numerical outputs from temporary discovery probes were not copied into the generated flowsheet as unexplained constants; and
- derived values are recalculated from their source inputs when the applicable runtime step executes, unless the user explicitly requested a fixed snapshot or the value is a documented constant.

When an approved official example was used as supporting evidence, confirm during the existing validation pass that:

- the generated process design still comes from the user's requirements;
- example-derived information is limited to supported imports, APIs, configurations, scaling targets, initialization methods, solver behavior, costing interfaces, or execution dependencies;
- supported property-package and unit-model operations were used instead of manually reconstructed scientific equations;
- the example remains compatible with the model scope for which it is being used; and
- every material deviation from the user's requirements is explained.

This conformance check does not require another model execution or solver run. Reuse the evidence and results from the existing validation pass.

Only when the user explicitly requests reproduction of a named official example or tutorial should the generated model be compared against that source for reference fidelity. Check its model selections, configurations, numerical values and targets, scaling, initialization, and execution dependencies. Explain deviations required by the wrapper or installed package version.

Comparing an ordinary prompt-generated flowsheet with a hidden solution belongs in a separate acceptance test after generation, not in the flowsheet-building workflow.

## Initialization Validation

When initialization is the deepest required checkpoint, or when initialization must be isolated, run through the initialization step. In End-to-End Build, do not run it separately when the final deeper run includes the same unchanged initialization:

```text
fi-run <flowsheet.py> --last <initialization-step-name> --skip-db-test -q
```

Confirm that:

- initialization uses public APIs supported by the installed models;
- units initialize in dependency order;
- required upstream states are available;
- state propagation uses compatible ports;
- recycle tear selections and guesses come from the generated topology and supported evidence;
- initialization completes without an exception;
- recycle convergence completes when applicable.

When the flowsheet contains a recycle, also follow `recycle-building.md`.

Successful initialization does not prove that the final solve succeeds.

## Solve Validation

Run through the applicable solve step:

```text
fi-run <flowsheet.py> --last <solve-step-name> --skip-db-test -q
```

A zero command exit code alone does not prove that the model solved successfully.

Inspect the stored solver results and confirm that:

- solver status is acceptable;
- termination condition is acceptable;
- results belong to the current generated model;
- no later source edit invalidated the solve;
- the solved degrees of freedom match the intended problem.

Do not report the model as solved when it only built or initialized.

## Costing and Optimization Validation

After adding costing or optimization, run once through the deepest requested costing or optimization step. That run validates its unchanged execution prefix. Run an earlier phase separately only when needed to isolate a confirmed failure:

```text
fi-run <flowsheet.py> --last <costing-or-optimization-step> --skip-db-test -q
```

Confirm that:

- costing blocks are attached to the intended units;
- costing initialization occurs before dependent calculations;
- optimization variables are deliberately unfixed;
- added constraints represent the requested decisions;
- the objective represents the user’s request;
- optimization degrees of freedom are understood;
- solver status and termination condition are acceptable;
- reported results belong to the latest generated model.

## Failure Handling

When a required check fails:

1. Stop at that validation level.
2. Preserve the generated file and all previously verified work.
3. Identify the first failing phase.
4. Record the strongest previous level that passed.
5. Separate import, wrapper, build, topology, specification, scaling, initialization, and solver failures.
6. Repair the failure only when its cause can be traced to a specific line or API call, and the correction is directly supported by installed source, official documentation, or the user's explicit instruction. If the cause cannot be pinned to a specific line, stop and report instead of guessing.
7. Repeat the failed check.
8. Rerun every later check invalidated by the correction.

Automatically repair only confirmed syntax, import, wrapper, or public API-usage errors. Do not change process values, topology, model selection, scaling strategy, initialization guesses, costing logic, optimization decisions, or scientific assumptions without user approval.

After one supported correction, rerun only the failed check and any later checks invalidated by that source change. If the same phase still fails, stop and report the failure instead of beginning another repair cycle, regardless of whether the cause seems understood. A second unapproved repair attempt on the same failure is not permitted; get explicit user approval before trying again.

Do not invent imports, ports, configuration options, specifications, initialization calls, tear guesses, tolerances, or solver settings to force validation to pass.

If the model builds but initialization or solving fails and the cause is not established, report the failure and recommend the diagnostic skill instead of silently changing the process model.

## Reporting

Report only the highest state actually verified:

1. file created;
2. imports and syntax valid;
3. wrapper valid;
4. model built;
5. topology and specifications checked;
6. operating conditions and scaling applied;
7. initialized;
8. solved;
9. costing or optimization completed.

For any required level that was not run, state that it remains unverified and explain why.