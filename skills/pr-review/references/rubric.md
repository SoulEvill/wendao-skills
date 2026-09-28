# Review rubric

## Severity: consequence and urgency

These are this skill's conventions, not a universal incident taxonomy. Rate a finding
using its concrete scenario, reach, recoverability, and affected contract. Explain
material preconditions. Never assign a fixed priority to a category.

| Level | Bar | Examples |
| --- | --- | --- |
| P0 | Immediate catastrophic exposure or a universal blocker, established by available evidence. Urgent intervention is needed. | Proven broadly exposed destructive behavior with no effective containment. |
| P1 | Serious supported failure; recommend fixing before merge. | Unauthorized access, data loss, broken primary workflow, dangerous deployment instructions. |
| P2 | Material defect or maintainability regression in a concrete supported case. | Truncated exports, violated retry contracts, a competing policy implementation that will diverge. |
| P3 | Small, localized consequence; can be scheduled normally. | Misleading secondary docs or avoidable complexity with a demonstrated modest maintenance cost. |
| Nit | Optional polish without material behavior/maintenance impact. Never blocking. | A naming or presentation preference consistent with otherwise valid code. |

Do not escalate to P0 on a hypothetical worst case. Do not dilute a serious defect to
P3 because confidence is low. Instead label its *potential* impact in an open question.
Documentation usually has modest consequences, but a runbook that disables a required
access control can be P1. A correct architectural choice can deserve discussion without
being a defect.

For every P0/P1 finding, explicitly justify the serious impact, exposed actor or
affected workflow, and material preconditions using available evidence. A proven
contract or policy violation alone does not establish serious harm. Names such as
"restricted" do not establish confidentiality, an unauthorized recipient, or an
incident's reach. Use P2 for a material violation when stronger impact is unestablished;
separately state the missing evidence that could change its priority.

## Confidence: evidence supporting the specific claim

| Confidence | Evidence bar | Reporting |
| --- | --- | --- |
| High | A reproduction or complete static causal chain establishes the trigger and failure; relevant protections and counterexamples were checked. | Finding, with evidence. Static proof does not require executing production code. |
| Medium | Concrete source/contract evidence supports the failure, but a stated environmental or integration assumption remains. | Resolve the material assumption or present a Low confidence question. A narrower finding must independently meet the high-confidence bar. |
| Low | A plausible concern depends on an unavailable contract, unknown workload, inferred requirement, or unverified execution path. | Open question, missing evidence, and next verification step. |

Confidence is not a calibrated numerical probability. Multiple agents agreeing is not
proof. Distinguish confidence in a finding from completeness of an axis investigation.
These grades belong in the evidence record. For visible comments, follow report.md:
high is implicit, while unresolved material uncertainty is a `Low confidence` question.
An internal medium assessment must not silently appear as an unqualified high-confidence
finding just because the public format omits a routine confidence label.

## Axes: what earns a finding

| Axis | Investigate | Required grounding and common false positive |
| --- | --- | --- |
| Correctness | Inputs, state transitions, invariants, boundary cases, serialization, promised compatibility. | Show input/state, expected behavior, actual behavior, and causal changed code. Do not invent requirements or backward compatibility. |
| Security and privacy | Trust boundaries, authorization, validation, injection, credentials, sensitive data flow, tenant isolation. | Establish reachable input, authority, sensitive sink, and missing control. Consider protections outside the changed function. |
| Reliability and operations | Partial failure, retries, idempotency, cancellation, deadlines, cleanup, rollout, recovery, diagnostics. | Trace a failure sequence and resulting damage or loss of operability. Do not demand elaborate infrastructure for a bounded tool. |
| Performance and scalability | Work per request, query count, pagination, concurrency, memory, contention, external quotas. | Identify the growth variable and evidenced workload, documented limit, or algorithmic consequence. "May be slow" is insufficient. |
| Simplification | Indirection, branching, state, abstraction cost, readability of the real execution path. | Explain what complexity can be removed while preserving behavior and why this reduces maintenance risk. Fewer lines alone is not better. |
| Duplication and reuse | Duplicated policy/ownership, repeated lifecycle logic, existing utilities, diverging contracts. | Cite the existing implementation and prove semantic fit, including lifecycle/dependency constraints. Similar syntax alone does not justify coupling independent domains or historical migrations. |
| Architecture and system fit | Responsibility placement, dependency direction, source of truth, public contracts, extension points, consistency with established design. | Trace the affected boundary and consequence; compare a feasible existing approach. Standard includes this axis. Holistic broadens evidence gathering. |
| Tests and validation | Whether changed behavior and important failure paths are verifiable; assertions, realism, determinism. | Name a concrete uncovered risk or misleading test and a discriminating check. Avoid coverage-percentage demands or tests that restate implementation. |
| Documentation and contracts | API docs, schemas, examples, config defaults, migrations, operator/customer instructions. | Show the inconsistency and who will do what incorrectly as a result. Prefer existing automated source-of-truth generation. |

Axes overlap. An export bypassing an existing paginated service can be one correctness
finding with reuse/architecture noted in the companion record, rather than three comments
about the same cause.
Independent failures with different fixes remain separate.

## Coverage is not a score

In the companion evidence record, for every axis use `reviewed`, `partial`,
`not_applicable`, or `skipped`. Add confidence
in the assessment plus a short evidence/scope note. `reviewed` means the relevant scope
was examined, not that no undiscovered defect exists. `partial` means relevant evidence
was missing. `skipped` means the planned check was not performed, for example due to a
budget limit. Justify `not_applicable` from this change, not from a missing tool.

State missing context honestly even if another axis has a high-confidence finding.
Use report.md's separate outcome labels and finding IDs so the user can distinguish
"No issues found in reviewed scope" from "Finding F1", a question, or missing coverage.
Do not calculate an aggregate quality score that hides a serious defect behind strong
scores elsewhere.
