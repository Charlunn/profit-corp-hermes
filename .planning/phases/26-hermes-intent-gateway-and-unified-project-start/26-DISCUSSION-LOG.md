# Phase 26: Hermes Intent Gateway and Unified Project Start - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-05-05
**Phase:** 26-Hermes Intent Gateway and Unified Project Start
**Areas discussed:** Hermes-native start contract, authoritative run creation, operator-visible abstraction, backbone reuse boundary

---

## Hermes-native start contract

| Option | Description | Selected |
|--------|-------------|----------|
| Single Hermes start intent | One visible "start project" capability regardless of internal machinery | Yes |
| Multiple explicit entrypoints | Expose different startup modes for different pipeline paths | |
| Script-first startup | Keep commands/scripts as the normal operator path | |

**User's choice:** Auto-selected the canonical single Hermes start intent.
**Notes:** `--auto` mode picked the stricter milestone-aligned option that Hermes owns project start as one visible capability.

---

## Authoritative run creation

| Option | Description | Selected |
|--------|-------------|----------|
| Reuse shipped governed run model | One authoritative run identity and artifact family reused from phases 22-25 | Yes |
| New Hermes-only state model | Create a fresh state machine for v1.3 packaging | |
| Mixed best-effort bridge | Start in Hermes and translate later without one canonical run source | |

**User's choice:** Auto-selected reuse of the shipped governed run model.
**Notes:** This preserves milestone continuity and avoids forking authority truth.

---

## Operator-visible abstraction

| Option | Description | Selected |
|--------|-------------|----------|
| Hermes-native language | Owner sees Hermes-level progress and blocker messages | Yes |
| Mixed Hermes + internal jargon | Some script/phase names leak into healthy-path output | |
| Raw internal reporting | Expose internal pipeline terms directly to the owner | |

**User's choice:** Auto-selected Hermes-native language.
**Notes:** Healthy-path output should feel like one Hermes workflow, with internal details still inspectable in artifacts.

---

## Backbone reuse boundary

| Option | Description | Selected |
|--------|-------------|----------|
| Thin interface layer over current backbone | Wrap existing startup machinery without replacing it | Yes |
| Full orchestration rewrite | Replace the current launch path with a new Hermes runner | |
| Partial duplication | Add new top-level flow while keeping old one separately authoritative | |

**User's choice:** Auto-selected thin interface reuse over the current backbone.
**Notes:** This aligns with the brownfield constraint and the roadmap requirement not to invent a second state model.

---

## the agent's Discretion

- Exact wording of the Hermes start acknowledgement
- Exact field layout of the normalized top-level intent payload
- Exact adapter seam between the visible Hermes entrypoint and existing start scripts

## Deferred Ideas

- Internal role choreography belongs to Phase 27
- Proposal and approval experience belongs to Phase 28
- Final delivery and blocked recovery experience belongs to Phase 29
