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

Do not infer unrequested downstream units, operating conditions, initialization, solving, costing, optimization, or reporting. Do not treat the current increment as the completed flowsheet unless the user says it is complete.

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

The interaction mode controls how the requested scope is delivered; it does not expand that scope. Add operating conditions, scaling, initialization, solving, costing, optimization, or result reporting only when requested or required to perform another explicitly requested operation.

A request to build, create, or add process equipment does not by itself request initialization or solving.

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

Combine all missing mode, filename, and destination questions into the same response when practical.

If the user already supplied a build mode, filename, or complete output path, do not ask for that information again.

## Select the Output File

Never save a generated flowsheet inside the installed skill directory.

When extending an existing flowsheet, continue editing that file unless the user requests a new output file.

For a new flowsheet:

1. Obtain or confirm the destination directory.
2. Suggest a process-based filename if the user has not supplied one.
3. Check whether the resulting target path already exists.
4. If it exists, ask whether the user wants to extend that file or choose another filename.
5. Do not overwrite an existing file.

After the path is confirmed, run:

```text
<selected-python> <skill-directory>/scripts/create_flowsheet.py <target.py>
```

This script copies `assets/flowsheet_template.py`. Do not reproduce the template manually.

## Build Workflow

After the mode and target file are established:

1. Read and follow `references/model-discovery.md`, including running its environment detector when no environment has been confirmed, before selecting or adding model-specific code.
2. Create the canonical wrapped file when starting a new flowsheet.
3. Tailor the canonical execution phases to the requested flowsheet. Remove unused decorated placeholder functions and their runner entries, add any required phases, and keep `FlowsheetRunner(steps=(...))` synchronized with the resulting decorated steps in dependency order.
4. Implement one coherent flowsheet stage.
5. Read `references/recycle-building.md` if the requested topology contains or changes a recycle, return, feedback, bypass, purge, or other directed cycle.
6. Read `references/wrapper-integrity.md` if the stage changes functions, execution phases, solver sequencing, context usage, or the runner step sequence.
7. Read and follow `references/validation.md`, executing every check applicable to the completed stage.
8. In Progressive Build mode, report only the completed increment and wait for the user’s next process description. Do not propose or implement an unrequested downstream unit.
9. In Guided Build mode, report the completed stage, describe the next stage derived from the requested complete topology, and wait for approval.
10. In End-to-End Build mode, continue through the remaining requested stages unless user input is required.

Keep each build stage efficient. Reuse evidence already verified for the current generated file, group related read-only checks into as few processes as practical, and do not repeat successful environment discovery.

If a command fails before executing because of a tool-launch or execution-boundary error, retry it once using the simplest supported method. Do not retry equivalent patch commands repeatedly.

Use installed public APIs and authoritative documentation to verify model-specific behavior.

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

Do not report a successful solve unless it was executed and its termination condition was checked.

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