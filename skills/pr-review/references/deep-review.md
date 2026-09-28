# Deep and holistic review

## Independent workstreams

Let actual risk determine grouping. A useful default is:

1. Behavior and contracts: correctness, security/privacy, tests, docs.
2. Failure and resource behavior: reliability, operations, performance/scalability.
3. System fit: architecture, simplicity, duplication/reuse; holistic when on.

The coordinator can own one workstream. Prefer a few substantive assignments over one
agent per axis. Give each reviewer exact revisions, PR intent, applicable guidance,
assigned scope, rubric, tool/budget constraints, and accessible repository. Do not give
initial reviewers another reviewer's conclusions. Do not delegate writes or publication.
Use the requested model and effort unless the user explicitly specifies role overrides.
Resolve external guidance once and pass applicable sources and scope to each workstream;
do not let child reviewers select other repository profiles or update preferences.

Require candidate evidence, counterevidence, coverage gaps, and checks actually performed.
The coordinator reads cited source, checks attribution to this PR, reconciles disagreements,
and deduplicates. For serious or disputed findings, use a focused verification pass if
independent capacity is available. Give the verifier the claim and raw evidence, not an
instruction to confirm it. Drop rejected candidates; keep unresolved uncertainty in questions.

Respect user limits and host capacity. Do not silently escalate cost/concurrency or
launch a chain of reviewers. If a workstream fails or context is truncated, mark its
axes partial/skipped and identify the gap. Sequential Deep expands scope but does not
provide independent corroboration.

## Holistic investigation

This extension is on by default in Deep and opt-in in Standard. Explicit `holistic=off`
limits it while preserving normal architecture and reuse checks.

Start from capabilities introduced or changed, not file names alone:

1. Map responsibility: entry point, callers, domain owner, state/data owner, downstream
   contracts, lifecycle, and operational boundary. Read relevant design records and
   extension examples, checking that they still match current code.
2. Search the accessible repository for semantic equivalents. Search symbols, domain
   vocabulary, behavior (pagination, retry, authorization), registries, tests, and
   neighboring services. Follow promising references instead of reading the whole repo.
   Record paths searched and scope limitations.
3. Compare credible alternatives. Does an existing capability have the same semantics,
   ownership, lifecycle, availability, and dependency constraints? Would reuse introduce
   a cycle, violate a snapshot guarantee, or couple independent domains? Duplication may
   be correct. Absence from one search is not proof no equivalent exists.
4. Trace affected consumers and data/control flow. For accessible external repositories,
   identify exact revisions and contract evidence. An unavailable consumer makes that
   part of the assessment partial; do not invent its behavior.
5. Evaluate growth against evidence: a supported workload, limit, repeated extension
   pattern, roadmap requirement, or operational constraint. Distinguish throughput,
   data volume, number of integrations, and maintenance growth. Do not assume every
   project needs a platform or a distributed architecture.

An actionable architecture finding contains:

- The capability/responsibility and changed path introducing the issue.
- Existing implementation or boundary evidence, with paths/symbols.
- Concrete failure or maintenance consequence and the conditions under which it matters.
- A feasible alternative, why it fits, and significant migration/dependency tradeoffs.
- The smallest useful change now; optional longer-term work is labeled as such.

Stop widening once relevant ownership, credible reuse candidates, affected contracts,
and material growth assumptions are understood, or when the agreed budget is reached.
Summarize important unchecked areas. Avoid prescribing a repository-wide rewrite for
a narrow PR unless a narrow fix demonstrably cannot preserve the contract.

## Example

A new export endpoint directly calls a first-page provider API. Another package owns a
streaming export capability with pagination and cancellation. Inspect whether the new
endpoint can depend on that package and whether its output semantics match. If so,
describe the lost records and existing path that avoids them. Do not simply write
"use DRY" or "introduce an export framework."
