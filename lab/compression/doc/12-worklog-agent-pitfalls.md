+++
id = "s0019"
title = "Agent Pitfalls"
tags = ["quality", "methodology"]
+++

# Agent Pitfalls

Observed and anticipated failure modes when LLM agents work with the worklog methodology. Consolidates pitfalls previously scattered across entity specs (Dangers, Observed Agent Failure Modes) into one manageable reference.

Consumers: exam design (s0014), SKILL.md authoring (s0018), methodology refinement (s0001).

## Spec pitfalls

| # | Pitfall | Rule violated | Pressure mechanism | Observed |
|---|---|---|---|---|
| S1 | **Implementation details in specs.** Agent includes API signatures, class names, concrete technology choices, file paths in spec body. | s0011 Forbidden | User or conversation history describes implementation; agent leaks it into spec. | Yes — specific file paths instead of globs, script names that drift from actual filenames. |
| S2 | **Structural update gated unnecessarily.** Agent asks for approval to fix a typo, reword a section, or add a constraint — even though behavior doesn't change. | s0011 Updating (structural = free) | Agent over-applies the approval rule, not distinguishing structural from behavioral. | No. |
| S3 | **Spec update contradicts related spec.** Agent updates one spec without checking parent/sibling specs for contradictions. | s0011 Dangers | Non-obvious: two specs share tags or overlapping paths. | Yes — version drift between specs, overlapping `paths` claims. |
| S4 | **Over-specification.** Agent creates a new spec for something that should extend an existing one. | s0011 Dangers | User asks for spec on a narrow sub-feature of an existing spec's domain. | Yes — narrow spec for a single function instead of extending the module spec. |
| S5 | **Code > spec precedence.** Agent treats code behavior as authoritative when it conflicts with the spec. | SKILL.md Precedence | Agent reads source code that diverges from spec; follows the code. | No. |
| S6 | **Speculative behavioral detail.** Agent adds behavioral requirements to a spec that nobody asked for or decided. Each added detail becomes a binding implementation constraint because spec is authoritative over code. Agent treats spec-writing like documentation (more detail = better) rather than legislation. | s0011 Updating (behavioral = approval) | Agent "fleshes out" a spec based on what seems reasonable, or imports behaviors from similar systems seen in training data. | Yes — arbitrary constraints and edge-case handling added during spec creation, discovered only when implementation hits them. |
| S7 | **New spec without UNIMPLEMENTED markers.** Agent creates a spec for unbuilt features with behaviors stated as established facts. Nothing is implemented but the spec reads as current — no signal about what needs building, drift detection sees no gap. | s0011 Required Sections (mark approved unbuilt items UNIMPLEMENTED) | Spec-writing feels like describing what the system *will* do; agent writes in present tense without distinguishing "exists" from "should exist." | Yes — greenfield specs with all behaviors stated as current, no indication of implementation status. |
| S8 | **UNIMPLEMENTED misread as draft.** Agent interprets `UNIMPLEMENTED` markers as "spec is not finalized" rather than "behavior is approved but not yet built." Leads to hedging, re-asking for approval on already-approved items, or treating the spec as non-authoritative. | SKILL.md Precedence (spec authoritative regardless of markers) | Marker text triggers "work in progress" associations; agent treats marked specs as tentative. | Yes — agent asked to "finalize" specs that were already approved, hedged language around marked behaviors. |

## Task pitfalls

| # | Pitfall | Rule violated | Pressure mechanism | Observed |
|---|---|---|---|---|
| T1 | **Status not maintained.** Agent starts working without setting status to active, or finishes without setting done. | s0012 lifecycle | Agent focuses on implementation, forgets lifecycle bookkeeping. | Yes — plan archived as "active," stale plans in active directory. |
| T2 | **Empty modifies when work touches spec-governed files.** Chore/refactor under spec's `paths` but agent sets modifies = [] because "no behavior change." | s0012 Forbidden | Renaming, cleanup, or refactoring that touches governed paths. | No. |
| T3 | **Stubs presented as complete.** Agent marks task done when implementation uses mock data, placeholder returns, or stub comments. | SKILL.md stubs rule | User scaffolded endpoints; agent completes the task based on shape, not substance. | Yes — SKILL.md presented stub scripts as functional. |
| T4 | **Archive without spec verification.** Agent moves task to archive without checking that the governing spec is still consistent. | s0012 Archiving | Agent just does move_file, doesn't read or verify the spec. | No. |
| T6 | **UNIMPLEMENTED markers left stale.** Agent completes work that resolves an `UNIMPLEMENTED` item but doesn't remove the marker. | s0012 observed failure | Agent focuses on code, doesn't circle back to update spec. | Yes — implemented items still marked as unimplemented in specs. |

## Decision pitfalls

| # | Pitfall | Rule violated | Pressure mechanism | Observed |
|---|---|---|---|---|
| D1 | **Non-trivial edit instead of supersede.** Agent modifies an accepted decision's substance (choice, rationale, consequences) in-place. Trivial fixes (typos, formatting, obvious date corrections) are acceptable. | s0013 Forbidden | The change feels small but alters the historical record. | Yes (inverse) — design rationale buried in archives; decisions not created when they should be. |
| D2 | **Missing relates_to.** Agent creates a decision without linking it to the affected spec(s). | s0013 Forbidden | Decision is about process or tooling; agent doesn't think to link it. | No. |

## Cross-cutting pitfalls

| # | Pitfall | Rule violated | Pressure mechanism | Observed |
|---|---|---|---|---|
| X1 | **Tests after implementation.** Agent writes code first, then tests — or defers testing until "we see it working." | SKILL.md Rules | Conversational momentum ("simple feature, iterate fast"). | Yes — subagent read implementation before writing tests despite explicit black-box instruction. |
| X2 | **Implementation without covering spec.** Agent starts coding before a spec exists for the feature area. | SKILL.md Forbidden | User directly requests implementation; no spec mentioned. | No. |
| X3 | **Test agent reads source code.** Agent derives tests from implementation details rather than spec alone. | SKILL.md Forbidden | Test seems more thorough when grounded in actual code. | Yes — subagent read implementation, defeating spec-only test isolation. |
| X4 | **Lifecycle bypass.** Agent modifies spec inline during task implementation without going through the update approval flow. | v1 lesson | Agent is "in the flow"; updating the spec feels natural. | Yes — v1 lesson: "agents modify specs inline while working." |
| X5 | **Spec change disguised as refactoring.** Agent changes observable behavior under the guise of "cleanup." | SKILL.md Forbidden | The behavioral change is small and the refactor framing feels safe. | No. |
| X6 | **Plan mode as substitute for worklog.** Agent enters an external planning mode when task body or spec body would serve as the planning medium. Duplicates planning outside the worklog where it is not persistent or traceable. | SKILL.md Session resume (worklog is your memory) | Agent defaults to built-in planning workflow rather than using the methodology's own artifacts. | Yes — agents enter plan mode for work that a task file already covers. |

## Severity

Severity = damage × persistence. Persistence depends on visibility: a pitfall the user can see immediately is caught and fixed; one that's invisible in the artifacts persists and compounds.

| Severity | Meaning |
|---|---|
| **Must** | Low visibility, propagating damage. Corrupts the spec→test→code chain or erases audit trail silently. |
| **High** | Medium visibility or cascading. Detectable on inspection but causes real harm if missed. |
| **Medium** | Fixable on discovery. No information destroyed, but adds maintenance burden or governance gaps. |
| **Low** | High visibility, minimal damage. User notices immediately; trivially correctable. |

| # | Severity | Rationale |
|---|---|---|
| S5 | Must | Spec "corrected" to match buggy code. Entire chain poisoned. Change looks reasonable — low visibility. |
| X4 | Must | Spec modified without approval during implementation. No paper trail. |
| X5 | Must | Behavioral change hidden under "cleanup" framing. No decision trail. |
| T3 | Must | Stubs presented as complete. Downstream work assumes feature is done. |
| X1 | Must | Tests written after implementation, coupled to code. Ordering invisible in artifacts. |
| X3 | Must | Tests derived from source code, not spec. Coupling invisible until refactor. |
| S3 | High | Spec update contradicts a related spec. Need to read both specs to notice. |
| X2 | High | Implementation without covering spec. Drift detection blind. |
| D1 | High | Non-trivial edit instead of supersede. Alters historical record silently. |
| T6 | High | Stale UNIMPLEMENTED markers. Completed work still marked unimplemented, spawning redundant tasks. |
| S6 | Must | Speculative requirements silently bind implementation. Extra detail in a spec looks thorough, not harmful — low visibility until implementation. |
| S7 | High | Missing UNIMPLEMENTED markers means no implementation status signal. Drift detection blind to unbuilt features. Visible on careful reading. |
| S8 | High | UNIMPLEMENTED-as-draft undermines spec authority. Agent hedges or re-gates already-approved work. Medium visibility — user notices hedging. |
| S1 | Better | Impl details in spec body. Readable, but maintenance burden compounds. |
| T2 | Better | Empty modifies on governed work. Governance gap, retroactively correctable. |
| T4 | Better | Archive without verifying spec consistency. Catchable on next read. |
| T1 | Better | Status not maintained. Visible but causes stale state if uncaught. |
| D2 | Better | Missing relates_to. Orphaned decision, harder to discover. |
| S2 | Low | Unnecessary approval gate. Delay only. |
| S4 | Low | Fragmented governance. Specs mergeable, just tedious. |
| X6 | Low | Plan mode visible and harmless, just redundant. User notices immediately. |

## Constraints

- Do not create a new entry that is near-identical to an existing one. If two pitfalls differ only in which entity they manifest through (e.g., "hotfix archived without decision" vs. "skipped decision for hotfix"), they are the same pitfall — merge them or keep one.

## Anticipated Changes

- New pitfalls discovered from exam results or production incidents.
- Severity re-evaluation as methodology enforcement matures.
