# Building Recycle Loops

Read this reference only when the requested flowsheet contains a directed cycle or when a follow-up request adds, removes, or changes a recycle, return, feedback, bypass, or purge connection.

Use installed package APIs and documentation matching the active environment. Do not hardcode unit classes, ports, tear streams, initialization order, guesses, tolerances, iteration limits, or solver settings.

## When to Consult Official Sources

Do not open every source for every recycle. Apply the durable instructions in this file first and inspect the installed package API, source, tests, and bundled documentation.

When installed evidence is insufficient and browsing is available, open and read the specific official source assigned to the unresolved question before generating the affected code. Do not rely on the link title or URL alone.

Open only the relevant source. Do not browse every link by default.

- For Pyomo graph creation, calculation order, tear selection, tear guesses, or convergence behavior, consult [Pyomo Network: Sequential Decomposition](https://pyomo.readthedocs.io/en/stable/explanation/modeling/network.html).

- For an exact `SequentialDecomposition` method or option, inspect the installed Pyomo API first. If clarification is still needed, consult the [Pyomo SequentialDecomposition API](https://pyomo.readthedocs.io/en/stable/api/pyomo.network.decomposition.html).

- For the standard IDAES construction order, `Arc` declaration, or network expansion, consult the [IDAES General Flowsheet Workflow](https://idaes-pse.readthedocs.io/en/stable/how_to_guides/workflow/general.html).

- For a generic IDAES recycle-initialization example, consult the [IDAES Recycle Flowsheet Tutorial](https://idaes-pse.readthedocs.io/en/1.2.1/tutorials/Module_2_Flowsheet_Solution.html). Treat its APIs as version-specific because this tutorial targets an older IDAES release.

- For a PrOMMiS flowsheet containing multiple recycle loops, consult the [PrOMMiS University of Kentucky Flowsheet Tutorial](https://prommis.readthedocs.io/en/stable/tutorials/uky_flowsheet-solution.html).

- For a PrOMMiS multi-stage membrane process with recycle and state propagation, consult the [PrOMMiS Multi-Stream Contactor Tutorial](https://prommis.readthedocs.io/en/stable/tutorials/diafiltration.html).

- For WaterTAP desalination initialization order, consult the [WaterTAP Seawater RO Desalination documentation](https://watertap.readthedocs.io/en/stable/technical_reference/flowsheets/seawater_RO_desalination.html).

Use a tutorial only for the model family and behavior it demonstrates. Do not copy its complete topology, numerical values, tear streams, initialization order, or solver configuration into a different flowsheet.

When online documentation and the installed package disagree, follow the installed package version.

If required behavior cannot be verified from installed evidence and browsing is unavailable, stop before inventing code and report what could not be verified.

## Describe the Recycle Topology

Translate the user’s request into process roles:

- forward-process path;
- recycle source;
- recycle destination;
- split or recovery point, if required;
- mixing or return point, if required;
- product or waste outlet;
- purge or bypass, if requested;
- affected material or energy state.

These roles describe the requested topology. They are not model or port names.

Infer a missing recycle source or destination only when the requested process and selected models make it unambiguous. Otherwise, ask one focused question before creating the loop.

Do not add a splitter, mixer, purge, translator, or other interface model unless the requested topology or selected model APIs require it.

## Discover Models and Connections

Follow `model-discovery.md` for every model involved in the loop.

Verify from the installed environment:

- exact import paths;
- required model configuration;
- available ports;
- property-package compatibility;
- state-variable compatibility;
- supported initialization methods;
- scaling requirements;
- solver requirements.

Do not assume that similarly named ports are compatible.

When adjacent units use incompatible state representations, search for a supported interface or translation model. If no supported interface exists, report the incompatibility instead of inventing a connection.

## Build Incrementally

Use this construction policy:

1. Build the requested once-through path without closing the recycle.
2. Validate imports, model construction, units, property packages, and forward connections.
3. Add any required split, mixing, purge, or interface models.
4. Add the recycle connection.
5. Rebuild a fresh model from the updated source file.
6. Validate the complete cyclic topology.
7. Add and validate the source-supported initialization procedure.

This staged policy isolates failures during generated flowsheet construction. It does not require the final flowsheet to remain open-loop.

When extending an existing generated file, preserve unaffected models and connections. Modify only the topology and execution phases affected by the recycle request.

## Declare and Expand Connections

Declare connections using verified source and destination ports.

Follow the installed IDAES and Pyomo network workflow:

1. Declare all required `Arc` objects for that model build.
2. Apply the network-expansion transformation after the arcs have been declared.
3. Build a fresh model after source-level connection changes.

Do not apply network expansion repeatedly to the same live model.

Pyomo’s sequential-decomposition graph requires the relevant directed arcs to be present and expanded. Verify this requirement against the installed Pyomo API before running graph-based initialization.

## Determine Specifications

After closing the loop, check the generated model’s degrees of freedom.

Determine required specifications from:

- user-requested operating conditions;
- selected model APIs;
- property-package requirements;
- package tests and maintained examples;
- the generated model’s degrees-of-freedom analysis.

A recycle may change which variables should be fixed or unfixed. Do not reuse specifications from the open-loop construction without checking the closed-loop model.

Do not insert universal `.fix()` values, split fractions, recoveries, purge rates, pressures, or flow guesses.

If the prompt does not provide a required value, use a documented default only when the selected model defines it as appropriate. Otherwise, report the missing specification.

## Choose an Initialization Strategy

Do not assume that every recycle must use the same initialization method.

Inspect the selected models and installed framework for a supported strategy, such as:

- graph-based sequential decomposition;
- a model-provided initializer;
- a documented unit-by-unit initialization sequence;
- a maintained process-specific initialization routine.

Choose the strategy best supported by the selected models and current package versions.

Use `SequentialDecomposition` only when the installed Pyomo API and generated network support it. Import it only when the generated implementation uses it.

## Determine Calculation Order

When using graph-based initialization:

1. Create the graph from the generated network using the installed API.
2. Derive the calculation order from the graph.
3. Verify that required upstream states are available before initializing each unit.
4. Compare the result with ordering requirements documented by the selected models.

Do not determine initialization order from function-definition order, unit names, or a fixed list stored in this skill.

A maintained example may confirm a model-specific ordering requirement. Do not copy its complete order unless the generated topology and selected models match.

## Determine Tear Streams

When the selected initialization method requires tear streams:

1. Detect cycles from the generated network graph.
2. Use installed Pyomo tear-selection or tear-validation APIs when appropriate.
3. Confirm that the selected tear set breaks the required cycles.
4. Confirm that each tear port carries the state required by the downstream unit.
5. Use an explicit tear set only when it is derived from the generated graph or required by maintained model guidance.

Do not hardcode arc names or select a tear merely because another flowsheet used it.

If automatic tear selection requires an unavailable solver or unsupported option, use another installed and documented selection method or derive and validate a tear set from the actual graph. Report the limitation.

## Determine Tear Guesses

Obtain initial tear values from the strongest available evidence:

1. user-provided operating conditions;
2. known upstream or feed states in the generated model;
3. model-defined initialization defaults;
4. maintained examples using the same model and compatible state basis;
5. a documented engineering assumption.

Check units, indices, phases, and components before applying a guess.

Do not copy numerical tear guesses from an unrelated example. Report assumptions that materially affect initialization.

## Reconcile Wrapper Execution

After adding recycle initialization:

1. Decide whether the logic is a helper inside an existing phase or a distinct runtime phase.
2. Validate any new decorated step name against the installed `fi-steps` output.
3. Update the explicit `FlowsheetRunner(steps=(...))` sequence.
4. Preserve model, solver, results, and `tee` handling through `Context`.
5. Follow `wrapper-integrity.md`.

Do not invoke the interactive `prommis-wrap` workflow. Continue editing the same generated wrapped file.

## Validate Incrementally

Report only the highest state actually verified:

1. recycle topology represented;
2. selected models and ports verified;
3. properties and state variables compatible;
4. arcs declared and expanded;
5. degrees of freedom understood;
6. initialization procedure constructed;
7. initialization completed;
8. tear streams converged, when applicable;
9. complete flowsheet solved.

Follow `validation.md` for the exact checks and stopping behavior.

## Handle Failure

If construction or initialization fails:

1. Preserve the generated topology and verified code.
2. Identify the first failed validation level.
3. Separate structural, specification, initialization, and solver failures.
4. Report missing evidence or required user information.
5. Do not invent API calls, numerical guesses, tolerances, or solver options.
6. Recommend diagnostics when the generated model builds but fails to initialize or solve.