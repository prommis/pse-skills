# Wrapper Integrity While Building a Flowsheet

Read this reference whenever editing the generated flowsheet changes:

- its functions;
- its decorated execution steps;
- the order in which those steps run; or
- how a solver is created, configured, or used by a solve step.

The generated file is already wrapped. Edit that same file directly. Do not invoke `prommis-wrap`, create another wrapped copy, show a wrapping plan, ask for a wrapping mode, or request another filename.

## Authoritative Sources

Use these sources in order:

1. The user-requested process topology.
2. Installed model classes, configuration, ports, and public APIs.
3. Package documentation and tests.
4. Maintained example flowsheets from the package providing the models.
5. Existing local wrapped flowsheets as additional implementation evidence.

Generate the flowsheet from the requested topology. Do not copy an entire example merely because it looks similar.

Examples may confirm model-specific patterns such as configuration, specifications, scaling, initialization, and solve order. They do not determine the process design.

The canonical wrapped asset is the only file copied wholesale.

Do not hardcode catalogs of unit models, property packages, ports, step names, initialization methods, solver options, or package APIs.

## Validate Step Names

Run `fi-steps --format text` in the detected project environment to obtain the currently valid step names.

Use its output only as an allowed-name set. Never use its printed order to determine flowsheet execution order.

When adding a runtime phase:

1. Determine the phase’s purpose from the generated flowsheet.
2. Select the closest behaviorally accurate valid step name.
3. Confirm that name appears in the current `fi-steps` output.
4. Report any non-exact compatibility mapping to the user.

Never invent a step name or silently combine distinct runtime phases.

## Classify Functions

Keep a function as a plain helper when it only organizes logic inside an existing phase.

Common helpers include functions that:

- add property packages;
- add unit models;
- connect units;
- apply related specifications;
- calculate related scaling factors; or
- report results.

Use a decorated step only when the function represents a distinct runtime phase that:

- must run at a particular point;
- exchanges state through `Context`; or
- should be independently runnable or visible in Flowsheet Inspector.

Do not decorate every helper.

Use substeps only when their Inspector visibility is useful and the installed runner supports them. Otherwise, keep the functions plain.

## Determine Execution Order

Derive execution order from the generated model’s actual dependencies.

Use installed model APIs, package tests, and maintained examples to confirm any required ordering. Do not copy an example’s complete execution sequence without checking that every phase applies to the generated flowsheet.

After every structural change:

1. Identify every decorated runtime step.
2. Determine what state each step requires and produces.
3. Order the steps according to those dependencies.
4. Preserve any ordering required by the selected models.
5. Place solver creation or reconfiguration before the solve that consumes it.
6. Encode the derived sequence explicitly in `FlowsheetRunner(steps=(...))`.

The canonical template begins with an explicit sequence covering all placeholder phases. Tailor it to the generated flowsheet: remove unused decorated placeholder functions and their runner entries, add required phases, and ensure the final sequence contains every remaining decorated runtime step exactly once and no helper functions.

Function-definition order and decorator order do not determine execution order.

## Preserve Context

The wrapper must use one shared `Context` consistently:

- The build phase creates the model and stores it in `context.model`.
- Later model-using steps retrieve the model from `context.model`.
- Solver setup stores the active solver in `context.solver`.
- Solve steps use the solver from context instead of creating another one.
- Results needed later or by the Inspector are stored in `context.results`.
- Solve calls use the context-provided `tee` setting.

Use the context variable name already established by the canonical template or generated file.

## Preserve Solver Behavior

Determine solver behavior from the selected models, installed APIs, and maintained package examples or tests.

Preserve the required:

- solver type;
- solver options;
- solver configuration;
- solve arguments;
- initialization solve behavior; and
- optimization solve behavior.

Do not combine distinct solver configurations. If the solver is changed or reconfigured, place that change before the solve that consumes it.

Do not create a new solver inside a solve step when the solver should come from context.

## Reconcile After Each Increment

After adding or changing units, connections, operating conditions, initialization, costing, or optimization, check the complete working file:

1. Every decorated function uses a currently valid step name.
2. Every decorated step appears exactly once in the runner sequence.
3. Every runner entry resolves to exactly one decorated function.
4. The runner sequence matches the dependency-derived execution order.
5. Plain helpers do not appear in the runner sequence.
6. Model, solver, results, and `tee` use `Context` consistently.
7. The `__main__` block calls `run_steps()` on the declared runner.
8. The complete file parses as valid Python.

If a check fails, repair the same generated file and repeat the failed check. Do not send the file through the interactive `prommis-wrap` workflow.

## Reporting

Report only the strongest state actually verified:

- file created;
- syntax valid;
- imports valid;
- model built;
- topology valid;
- initialized; or
- solved.

A valid wrapper does not prove that the process model builds, initializes, or solves.