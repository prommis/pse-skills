# Wrapper Integrity While Building a Flowsheet

Read this reference whenever editing the generated flowsheet changes:

- its functions;
- its decorated execution steps;
- the order in which those steps run; or
- how a solver is created, configured, or used by a solve step.

The generated file is already wrapped. Edit that same file directly. Do not invoke `prommis-wrap`, create another wrapped copy, show a wrapping plan, ask for a wrapping mode, or request another filename.

## Authoritative Sources

Use these sources in order:

1. The user-requested process topology and technical requirements.
2. Installed model classes, configurations, ports, and public APIs.
3. Official package documentation.
4. User-approved maintained official examples.
5. Package tests as supporting API evidence.

Generate the flowsheet from the requested topology. When example use is approved, examples may confirm model-specific configurations, scaling targets, initialization APIs, solver behavior, and execution dependencies. They do not determine the process design.

Do not copy a complete example or inherit unrelated topology, specifications, values, costing, optimization, or reporting. The canonical wrapped asset is the only file copied wholesale.

Do not hardcode catalogs of unit models, property packages, ports, step names, initialization methods, solver options, or package APIs.

## Validate Step Names

When the current increment adds, removes, or renames a decorated runtime step, run `fi-steps --format text` in the detected project environment to obtain the currently valid step names. Do not run this command for an increment that adds no new or changed decorated step; reuse the step names already confirmed for this file.

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

Do not decorate every helper. If it's unclear whether a function qualifies as a distinct runtime phase, default to keeping it a plain helper rather than decorating it.

Use substeps only when their Inspector visibility is useful and the installed runner supports them. If it's unclear whether substep visibility is needed, keep the functions plain and do not create substeps.

## Determine Execution Order

Derive execution order from the generated model’s actual dependencies. Do not impose a universal order or move an operation merely to fit a preferred wrapper phase structure.

Use the user’s explicit requirements, installed public model APIs, and official model documentation to determine what each operation requires and produces. Place scaling only after the objects and values it depends on exist, and place initialization only after all required specifications and scaling are available. If the workflow is split into decorated wrapper steps, preserve these dependencies and the model’s supported behavior.

Scaling is not necessarily a single early phase. If costing, optimization, or another later phase creates variables or constraints that require documented scaling, apply that scaling after those objects are constructed and before their corresponding initialization or solve. Do not rescale unchanged parts of the model unnecessarily.

After a structural change that adds, removes, or reorders a decorated runtime step:

1. Identify every decorated runtime step.
2. Determine what state each step requires and produces.
3. Order the steps according to those dependencies.
4. Preserve any ordering required by the selected models.
5. Place solver creation or reconfiguration before the solve that consumes it.
6. Encode the derived sequence explicitly in `FlowsheetRunner(steps=(...))`.

The canonical template activates only `build`. Its optional phase functions are plain reusable helpers. Decorate only the runtime phases required by the generated flowsheet, add every decorated step to the runner sequence exactly once, and do not place plain helpers in the runner sequence.

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

Determine solver behavior from the selected models, installed public APIs, official documentation, and package tests. Use a complete example as solver evidence only when the user approved its use.

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

These eight checks are static verification of the file's current state. Running them does not require rerunning `fi-steps` unless the current increment meets the condition in "Validate Step Names" above.

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