---
name: prommis-build-flowsheet
description: "Creates, progressively extends, or completes wrapped PrOMMiS, IDAES, and WaterTAP flowsheets from plain-English process descriptions. Supports progressive, guided staged, and end-to-end construction. TRIGGER when: user asks to build, create, generate, or expand a flowsheet. DO NOT TRIGGER when: user only wants to wrap an existing raw flowsheet, change one value, find one import, or diagnose a solver failure."
metadata:
  author: Tanushree Subramanian
license: LICENSE.md
---

<!--
“PrOMMiS” was produced under the DOE Process Optimization and Modeling for Minerals Sustainability
(“PrOMMiS”) initiative, and is copyright (c) 2023-2026 by the software owners: The Regents of the
University of California, through Lawrence Berkeley National Laboratory, et al. All rights reserved.
Please see the files COPYRIGHT.md and LICENSE.md for full copyright and license information.
-->

# Build a PrOMMiS, IDAES, or WaterTAP Flowsheet

Create a wrapped flowsheet from the user’s process description and extend the same file incrementally as the process changes.

For new flowsheets, begin with the canonical wrapped template. Do not first generate a separate unwrapped flowsheet or invoke the interactive `prommis-wrap` workflow.

## Locate Resources

Resolve all scripts, references, and assets relative to the directory containing this `SKILL.md`.

Use the Python interpreter selected through `references/model-discovery.md`. Do not hardcode repository locations, environment names, package paths, imports, or model APIs.

## Interaction Modes

Support three flowsheet-building modes.

### Progressive Build

Use Progressive Build when the user wants to construct the process through multiple prompts.

Each prompt defines only the current increment. Implement and validate that increment, report what changed, and wait for the next process description.

Do not infer unrequested downstream units, operating conditions, initialization, solving, costing, optimization, or reporting. Do not treat the current increment as the completed flowsheet unless the user says it is complete. Treat only what the current prompt explicitly states as the increment. Do not expand it to include a step that would logically follow, even if it seems like the obvious next action.

### Guided Build

Use Guided Build when the user provides the complete requested process but wants it built and reviewed in stages.

Derive coherent stages from the complete requested topology. After each stage:

- explain what was added and its role;
- report the applicable validation result;
- describe the proposed next stage; and
- wait for approval before continuing.

### End-to-End Build

Use End-to-End Build when the user provides the complete requested process and wants it built without intermediate approval pauses.

Build and validate all requested stages, provide concise progress updates, and pause only when missing information prevents a valid modeling decision or requires user authorization.

The interaction mode controls how the requested scope is delivered; it does not expand that scope. Add operating conditions, scaling, initialization, solving, costing, optimization, or result reporting only when the user explicitly requested it, or when it is a hard technical prerequisite for an explicitly requested operation. When adding something under the second condition, state in the response exactly which requested operation it was required for. If that dependency is not certain, ask instead of adding it.

A request to build, create, or add process equipment does not by itself request initialization or solving.

## Scope Discipline

A filename, destination path, or broad process label is not a requirement. Do not use it to infer, plan, search for, mention, or justify adding topology, models, operations, initialization, solving, costing, optimization, or reporting that the user has not explicitly requested in a prompt.

This rule applies to every stage of the workflow, including code generation, example search, and completion reporting.

## Initial Response

When the user first describes a flowsheet:

1. Summarize the interpreted process topology without committing to unverified model classes or APIs.
2. Present a short outline based only on the process scope explicitly provided by the user.
3. Establish the interaction mode:
   - If the user explicitly selects **Progressive Build**, **Guided Build**, or **End-to-End Build**, use that mode without asking again.
   - Otherwise, explain all three modes and ask the user to choose:
     - **Progressive Build** — adds and validates only what each prompt requests, allowing the user to add more process sections through later prompts.
     - **Guided Build** — builds the complete requested flowsheet in stages and pauses after each stage for review.
     - **End-to-End Build** — builds and validates the complete requested flowsheet in one uninterrupted run.
   - If the user does not select a mode after being shown the three choices, ask whether they plan to add more process sections through later prompts or whether the current prompt contains the complete process. If the process is complete, ask whether they want stage checkpoints or one uninterrupted run.
   - Map the fallback response as follows:
     - Additional process sections will be supplied later → **Progressive Build**.
     - The complete process is supplied with stage checkpoints → **Guided Build**.
     - The complete process is supplied for one uninterrupted run → **End-to-End Build**.
   - If the response remains unclear, ask one short follow-up question. Do not begin building until the mode is established.
4. For a new flowsheet, ask where the generated Python file should be saved.
5. Suggest a descriptive snake-case filename ending in `.py` and ask whether the user wants to use it or provide another name.

After the mode is established, state it before building:

- **Progressive Build** — adds and validates only what each prompt requests, continuing in the same flowsheet.
- **Guided Build** — builds the complete requested flowsheet in stages and pauses for review.
- **End-to-End Build** — builds and validates the complete requested flowsheet in one uninterrupted run.

A request to initialize, solve, cost, optimize, validate, or report results defines technical scope independently of the selected interaction mode.

Combine all missing mode, filename, and destination questions into a single response. Ask them together in one message; do not spread them across multiple turns.

If the user already supplied a build mode, filename, or complete output path, do not ask for that information again.

In Progressive Build, a prompt that only selects the mode, filename, or destination does not define a build increment. Record those choices and wait for the first process-model request. Do not detect the modeling environment, create the canonical file, or run validation until the user supplies the first property package, process unit, connection, or other model content.

## Select the Output File

Never save a generated flowsheet inside the installed skill directory.

When extending an existing flowsheet, continue editing that file unless the user requests a new output file.

For a new flowsheet:

1. Obtain or confirm the destination directory.
2. Suggest a process-based filename if the user has not supplied one.
3. Check whether the resulting target path already exists.
4. If it exists, ask whether the user wants to extend that file or choose another filename.
5. Do not overwrite an existing file.

After the path is confirmed and the first process-model increment has been supplied, run:

```text
<selected-python> <skill-directory>/scripts/create_flowsheet.py <target.py>
```

This script copies `assets/flowsheet_template.py`. Do not reproduce the template manually.

## Build Workflow

After the mode and target file are established:

1. Read and follow `references/model-discovery.md`, including running its environment detector when no environment has been confirmed, before selecting or adding model-specific code.
2. Create the canonical wrapped file when starting a new flowsheet.
3. Tailor the canonical execution phases to the requested flowsheet. Remove unused decorated placeholder functions and their runner entries, add any required phases, and keep `FlowsheetRunner(steps=(...))` synchronized with the resulting decorated steps in dependency order.

Treat the canonical template’s optional functions as reusable placeholders, not as a prescribed workflow. Before model-specific validation, decorate only the runtime phases required by the requested flowsheet and derive their runner order from the user’s requirements and the selected models’ verified dependencies. Do not retain a placeholder phase selection or order without verification.

4. In Progressive Build and Guided Build, implement one coherent stage at a time. In End-to-End Build, implement the complete requested scope in dependency order before consolidated validation, unless an intermediate check is needed to verify an uncertain API before dependent code is written.
5. Read `references/recycle-building.md` if the requested topology contains or changes a recycle, return, feedback, bypass, purge, or other directed cycle.
6. Read `references/wrapper-integrity.md` if the stage changes functions, execution phases, solver sequencing, context usage, or the runner step sequence. If the current increment adds no new decorated runtime phase and changes no execution order, do not read this reference and do not run its step-name validation command.
7. Read and follow `references/validation.md`. Validate each completed checkpoint in Progressive Build and Guided Build. In End-to-End Build, consolidate validation and avoid separately executing every intermediate runtime phase when a later run already includes those phases.
8. In Progressive Build mode, report only the completed increment and wait for the user’s next process description. Do not propose or implement an unrequested downstream unit.
9. In Guided Build mode, report the completed stage, describe the next stage derived from the requested complete topology, and wait for approval.
10. In End-to-End Build mode, continue through the remaining requested stages unless user input is required.

Keep user-facing progress updates brief and focused on the process model, completed work, and decisions requiring user input. Do not narrate internal reasoning, command construction, tool selection, patch mechanisms, routine API probes, environment searches, or retry attempts. Mention an execution or environment problem only when it blocks progress or materially affects the requested result; state the problem and required next action concisely.

Keep each build stage efficient. Select the Python environment once. Use exactly one Python process for all import, constructor, configuration, variable, and port checks required by a single increment, unless a check depends on a result from an earlier check in the same increment. Do not open or read the same file more than once per increment. Reuse every successful result whose source has not changed. In End-to-End Build, perform one consolidated final runtime validation. Do not repeat successful environment discovery, unchanged execution prefixes, successful solver runs, or reporting runs.

Do not create API probes, patch helpers, scratch scripts, logs, or other temporary artifacts inside the target repository, output directory, or user workspace. Run checks in memory whenever the check does not require writing to disk, such as import checks, API existence checks, and configuration inspection. Only create a temporary file when the check itself requires file I/O. If a temporary file is required, create it in the operating system’s temporary directory and remove it immediately after use, including after a failed check. At completion, leave only the files requested by the user or permanent project files explicitly required by the requested implementation.

If a required command or file edit fails before execution because of a sandbox or process-launch error, retry it once using the simplest native mechanism. If the retry fails for the same platform reason, use the supported approval or elevated-execution mechanism once and continue from the same stage. Do not restart completed discovery, search for patch wrappers, or attempt encoded or shell-based file-writing workarounds. Stop only if no supported execution path remains or the approved attempt also fails.

Use installed public APIs and authoritative documentation to verify model-specific behavior.

Build primarily from the user’s requirements, installed public APIs and source, and official model documentation.

### Official Example Approval Checkpoint

This checkpoint applies in Progressive Build, Guided Build, and End-to-End Build, but example discovery is optional and must not delay ordinary model discovery.

In Guided Build and End-to-End Build, perform the example check only after the supplied process requirements are understood.

In Progressive Build, perform an example check only after both of these conditions are met:

1. The principal process operation and its package or model family are known. The principal operation is the model that performs the main physical or chemical transformation, such as separation, reaction, heat transfer, membrane treatment, or extraction.
2. At least one identifying technical detail is known: the property or reaction basis, a specialized model configuration, a defining process connection, a costing method, or a simulation or optimization objective.

A feed, product, ordinary connection, property package by itself, or other generic support model does not satisfy these conditions unless it is explicitly the main requested process. If these conditions are never met, continue without an example. Do not infer future topology, costing, optimization, or reporting requirements from an example.

In Progressive Build, the principal process operation must be explicitly requested for implementation in the current increment before an example search is allowed. Do not satisfy this condition using a filename, destination path, broad process label, anticipated future topology, or equipment mentioned only as a later plan. A feed-only, property-package-only, or other preparatory increment remains ineligible even when the likely future process can be inferred.

Once these example-check conditions are met, perform at most one bounded search pass over maintained official examples installed with the selected package. Stop after finding one relevant candidate or completing that pass.

Do not search again unless a later increment:

- adds, removes, or replaces a principal process unit;
- changes the property or reaction model family;
- introduces a defining connection such as a recycle or energy-recovery path; or
- adds or changes the costing, simulation, or optimization purpose;

and the currently approved example no longer supports that changed scope.

Each permitted search is limited to one pass. Do not search the web, unrelated repositories, hidden solution files, or repeatedly broaden the search. If the user explicitly names or provides an official tutorial or example, use that source instead of performing another search.

A candidate is relevant only when the available official description indicates that it:

- uses the same principal model family;
- supports the currently known process topology and configurations; and
- contains no material conflict with the user's supplied requirements.

Differences in numerical values, reporting, wrapper organization, or stages not yet requested do not establish a conflict because those details remain controlled by the user. If multiple candidates remain equally plausible, do not select one; wait for more requirements or continue without an example.

Before approval, use only official example names, paths, package metadata, and descriptive documentation or module-level descriptions to identify a candidate. Do not read executable function bodies or extract code during the candidate search.

Do not inspect a candidate's implementation before receiving approval. If one relevant candidate is found, respond in two or three sentences that:

- identifies the example and its official provider;
- explains which currently requested models, topology, or operations appear similar; and
- explains which technical details it could help verify.

Then ask:

"May I inspect this example and use it only as supporting technical evidence?"

End the current turn and wait for the user's answer. End-to-End Build does not override this authorization checkpoint.

If the user explicitly requests reproduction or use of a named official tutorial or example, that counts as approval. Briefly identify its relevance and continue without asking again.

After approval, inspect only the portions needed for the current flowsheet. Confirm that the example actually uses compatible model families, topology, configurations, and installed-version APIs. If that inspection reveals a material conflict, do not use the example and continue from public APIs and official documentation.

An approved example may confirm:

- supported public import paths and APIs;
- property, reaction, and costing configurations;
- unit-model configuration options;
- model-specific scaling targets;
- initialization methods;
- solver behavior; and
- execution dependencies.

Do not copy the complete flowsheet, import its build helpers, reproduce its function structure, or inherit its numerical assumptions, topology, specifications, costing design, optimization design, or reporting. The user's explicit requirements always determine the generated flowsheet.

If no relevant example is found, the user declines, or the approved candidate proves incompatible, continue using the user's requirements, installed public APIs and source, and official model documentation. Absence of an example is not a blocker.

In Progressive Build, reassess an approved example only when a later increment materially changes the model family, topology, costing method, or simulation or optimization purpose. If the same example remains compatible, reuse it without another search or approval request. If a different example becomes necessary, identify that example and request separate approval before inspecting it.

Do not repeat environment detection, API discovery, validation runs, or solver runs solely for example selection or reassessment.

Treat user-supplied model selections, public import paths, configuration options, numerical values, target objects, scaling operations, initialization methods, and execution order as requirements. Preserve both the supplied value and the exact object or operation to which it applies. Do not broaden, reinterpret, normalize, invert, replace, or silently improve a requirement. If it is unsupported by the installed API, explain the conflict before changing it.

Preserve scientific-model fidelity. Do not create, combine, or substitute thermodynamic, reaction, costing, or initialization configurations unless that construction is supported by a public package API, an authoritative source, or the user’s explicit choice. If the requested behavior cannot be represented using verified public components, stop and explain the missing dependency or modeling decision instead of silently producing an approximation.

## Continue Existing Work

Remember the selected mode and target file throughout the conversation.

In Progressive Build, treat each follow-up process description as a bounded addition to the same file. Do not interpret it as approval to complete, initialize, or solve the remaining flowsheet. Continue until the user explicitly requests those operations or switches modes.

Treat later process descriptions as changes to the same flowsheet unless the user requests a new file. The user may approve the proposed next stage, change the topology, add another unit, provide operating data, request another model, or switch interaction modes.

Inspect the current implementation and its validated state before extending it. Preserve unrelated user code and previously validated behavior.

## Completion

Report:

- the file created or updated;
- the process components added;
- the stages completed;
- the highest validation stage completed;
- any assumptions or checks that could not be verified.


Do not name unrequested downstream units, operations, or process stages in the completion report, even as "not yet added" or "not yet built." Report only what was implemented and validated for the current increment. If the user asks what would come next, answer that separately from the completion report, not inside it.

## Interaction Examples

These examples define the interaction pattern only. Derive actual models, stages, and technical decisions from the user’s process and the available evidence.

### Example: Selecting a Mode and Output File

**User**

```text
Build a desalination flowsheet with a feed, pump, reverse-osmosis unit,
energy-recovery device, and one recycle.
```

**Response**

```text
I interpret this as a pressurized desalination train with membrane separation,
energy recovery, and a recycle connection.

Choose a build mode:

- Progressive Build adds and validates only what each prompt requests, allowing
  you to add more process sections through later prompts.
- Guided Build divides the complete requested flowsheet into stages and pauses
  after each stage for your review.
- End-to-End Build builds and validates the complete requested flowsheet in one
  uninterrupted run.

I suggest the filename `desalination_flowsheet.py`. Where should the file be
saved, and which build mode would you like?
```

### Example: User Already Specifies the Mode and Path

**User**

```text
Build the complete HDA flowsheet in end-to-end mode and save it as
C:\models\hda_flowsheet.py.
```

**Response**

```text
I’ll use End-to-End Build and target `C:\models\hda_flowsheet.py`.

I’ll first verify that the target is available, then derive the process-specific
build stages, create the wrapped scaffold, implement each stage, and run the
applicable validation without pausing between stages.
```

Do not ask the user to select a mode, filename, or directory again.

### Example: Guided Build Checkpoint

**Response after completing a stage**

```text
Stage 1 is complete. I added the verified property package and feed model,
specified the initial feed state, and validated the current build and imports.

The next stage will add the pump and connect it to the feed. Would you like me
to continue with that stage or change the proposed design?
```

### Example: Incremental Follow-Up

**User**

```text
Continue, but add a second pump before the membrane unit.
```

**Response**

```text
I’ll revise the next stage to add two sequential pumps before the membrane
unit, then validate the updated connections and operating specifications.
```

Continue editing the same flowsheet and retain the previously selected interaction mode.