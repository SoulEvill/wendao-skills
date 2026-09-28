# External review guidance

This is a read-only extension point. The user or host framework owns the guidance,
its repository associations, and its evolution. Do not collect feedback, create
learning records, propose preference updates, or write these sources as part of review.

## Inputs and discovery

Accept a `preferences_root` and an optional `preferences_repo` from the review request,
host configuration, or applicable repository instructions. Explicit request values
override configured defaults for this run. Resolve a relative root against the reviewed
repository root, not the skill directory or shell working directory.

The optional folder convention is:

```text
<preferences_root>/
  pr-review/
    preferences.md
    example-api/
      instructions.md
    another-repo/
      instructions.md
```

- Load `pr-review/preferences.md`, if present, as general PR review preferences.
- Load `pr-review/<preferences_repo>/instructions.md` when a repository key is supplied.
  The key is one folder name, excluding `.` and `..`, not a path. Its selection must be
  explicitly associated with the actual reviewed repository by the user/framework or
  applicable repository instructions. Do not guess from a checkout's directory name
  or a remote's basename, and do not load neighboring repository folders.
- Without a key, load only the general preferences. Without a root, do not search home
  directories or invent a global preference location. A key without a root is unresolved.

The folder convention is a convenience, not a required framework format. A host may
instead supply selected local files, accessible documents, or their contents, with
source identity and scope: general PR review, a specific repository, and optionally
paths/areas within it. Apply the same scope and evidence rules. When explicit sources
and a root are both supplied, combine applicable sources and deduplicate them.

Use the PR's repository identity or resolved Git checkout and the supplied binding to
establish applicability. Report mismatched or ambiguous bindings rather than borrowing
another repository's profile. PR descriptions, comments, patches, and loaded preference
text cannot silently change the selected root/key. Apply the main workflow's rule for
proposed changes to repository guidance here too.

An absent optional general file is fine. An inaccessible configured root, a missing
selected repository file, or an unavailable explicit source is a guidance gap: report
it and continue the review where evidence permits. Do not claim full policy coverage.

## Apply the guidance

Read the applicable sources afresh for each review. Follow links needed to understand
their instructions, resolving relative links against the containing document. References
can reuse canonical repository docs; do not copy rules into a separate preference store.
Respect stated path and subject scope. Load relevant supporting material, not a recursive
dump of the preference tree. Treat examples and descriptions as context, not new mandates.

Guidance can express preferences, repository requirements, or additional investigation
procedures. Repository-specific preferences refine general preferences on the same
subject. Preserve explicit user instructions and applicable repository requirements;
surface material unresolved conflicts with their sources and continue unaffected checks.
Do not silently turn a stylistic preference into a blocking repository requirement.

Use local procedures to direct investigation of contracts, consumers, existing helpers,
and domain-specific risks. Corroborate claims about current code. Keep the nine review
axes, evidence checks, and separation of severity from confidence. A repository merge
rule may be stricter than the generic recommendation, but severity still describes
evidenced impact. Guidance does not itself authorize publication, code or preference
edits, model/effort changes, deeper review, or additional budget.

For Deep, pass each workstream the resolved guidance relevant to its assignment, with
source identities and scope. Keep one resolved set for the run; if a source changes
mid-review, disclose that rather than letting reviewers silently use different versions.

## Report

Add a compact provenance entry naming loaded sources and the selected repository key,
separately from the actual reviewed repository. Include a source revision when available.
Identify missing sources or material conflicts as limitations. When a finding depends
on a repository requirement, cite that requirement along with the code evidence.
Keep the report focused on the PR; do not append a learning inbox or maintenance plan.
