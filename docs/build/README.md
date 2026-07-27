# Build Guide

Start-to-finish walkthrough for building this system, split into phases so
you can work through one at a time on the bench.

The old top-level [`../assembly.md`](../assembly.md) is a terser summary of
the same steps and stays as a quick reference. If the two ever disagree,
these phase docs win.

## Reading order

Do the phases in order. Each phase ends with a **success check** — a
specific test you can run, with the expected output. Don't move on until
that check passes; downstream phases assume the previous ones work.

| # | Phase | Time | Prereqs |
|---|---|---|---|
| 00 | [Overview + tools you'll need](00-overview.md) | 15 min read | none |
| 01 | [Prep the Raspberry Pi](01-prep-pi.md) | 1 hr | Pi 5, SD card, monitor+kbd or SSH |
| 02 | [Prep the Pico](02-prep-pico.md) | 30 min | Pico + USB cable, laptop |
| 03A | [Battery Option A — salvaged 18650](03-battery-A.md) | 2–3 weeks calendar | cell tester, ~40 candidate cells |
| 03B | [Battery Option B — purchased LiFePO4](03-battery-B.md) | 30 min | packaged pack (see BOM) |
| 04 | [Power stack bench build](04-power-stack.md) | 2 hr build + 1–2 wk burn-in | Phase 03A or 03B done |
| 05+ | Sensors, cameras, audio, hive install | see later phases | Phases 01, 02, 04 done |

**Pick 03A or 03B — you only do one.** Everything upstream (panel, MPPT,
fuses, buck) and downstream (Pi rail, sensors) is identical either way.

## What each phase doc contains

- Parts checklist for that phase, cross-referenced to [`hardware/BOM.md`](../../hardware/BOM.md).
- Wiring diagram(s) — SVGs in [`../../diagrams/`](../../diagrams/) or inline ASCII.
- Numbered build steps.
- **Success check** — the command you run and what you should see.
- Troubleshooting table for common failures.
- What to do before moving to the next phase.

## Photos

Where a real-world photo would help more than a diagram, you'll see:

> **📷 Photo needed:** [description of what should be shown].

I can't take those — that's on you as you build. Drop the file into
`docs/build/img/` with a matching name and it'll render in-line.
