# Incremental Flowsheet Validation

Read and follow this reference after any edit that adds, removes, or changes an import, property package, unit model, connection, operating condition, scaling operation, initialization routine, costing block, optimization logic, decorated step, or runner sequence.

Validation is not required for comments or formatting-only changes.

Run every applicable check before continuing to a dependent phase or reporting completion. A check passes only when its command completes successfully and its results satisfy the stated criteria.

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

Use the smallest validation set that covers the change:

- Import added or changed: run Import Validation.
- Decorator, execution step, helper function, or runner order changed: run Wrapper Validation.
- Property package, unit, port, `Arc`, or transformation changed: run Build Validation.
- Process connection or specification changed: run Topology and Degrees-of-Freedom Validation.
- Operating condition or scaling changed: run through the affected execution step.
- Initialization changed: run through the initialization step.
- Recycle changed: validate the once-through model, then the closed loop and its initialization.
- Solve logic changed: run through the affected solve step.
- Costing or optimization changed: run through every affected costing or optimization step in dependency order.

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

The canonical asset begins with an explicit sequence covering all placeholder phases.

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

After changing property packages, units, ports, connections, or transformations, construct a fresh model by running only through `build`:

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

After changing operating conditions or scaling, run through the latest affected decorated step:

```text
fi-run <flowsheet.py> --last <affected-step-name> --skip-db-test -q
```

Confirm that:

- required variables are fixed or unfixed as intended;
- values use the correct units and indices;
- component, phase, and time indices match the selected property package;
- scaling calls reference objects that exist;
- scaling values follow the selected model’s supported guidance;
- degrees of freedom are appropriate after the specifications are applied.

Do not introduce numerical values only to make a validation check pass.

## Initialization Validation

After adding or changing initialization, run through the initialization step:

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

After adding costing or optimization, run through each affected step in dependency order:

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
6. Repair the failure only when its cause and a supported correction are understood.
7. Repeat the failed check.
8. Rerun every later check invalidated by the correction.

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