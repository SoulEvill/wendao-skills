# Review presentation and recommendation

Prepare a local draft for the user to review, edit, and publish. The draft contains the
proposed overall comment and anchored inline comments; a remote pending review is still
a publication action and needs authorization. Keep the review concise and conversational.
Retain the investigation evidence
in a companion record; reducing presentation detail must not reduce review coverage.
Honor a required host schema with equivalent fields or a companion artifact.

## Overall comment

Open with the acknowledgment; put the review level with the attribution at the bottom:

```markdown
Thanks for separating the lifecycle into explicit phases and moving close-out into its
own skill. The phase-specific contracts address the structure this PR set out to improve.

I found four P2 issues around publishing permission, setup recovery, and the acceptance
flow. They can allow publishing after permission is revoked or prevent valid workflows
from completing, so I would hold approval until they're fixed. Details are inline.

226 tests passed; targeted probes reproduced the failures. Live publication was not tested.

_Prepared with automated PR review assistance._ **(Review level: Standard)**
```

Use only Standard or Deep in the attribution footer. Put holistic, requested/observed model, and native
effort in the evidence record; do not guess them or confuse them with review level. Include
execution settings visibly only when requested or a capability mismatch affects delivery.

Thank the author briefly for specific observed work and explain
whether the change addresses its stated intent. Credit concrete progress, with qualifications
where behavior is incomplete. If intent or author identity is unavailable, preserve that
uncertainty; a short generic thanks is enough. Do not invent a name, successful outcome,
or human sign-off. Avoid canned praise and repeating thanks in every inline comment.

Next give a high-level synthesis of the findings, then the decision and its reason. These
can share a paragraph; use connected prose rather than a section for every step. If there
are no supported findings, say so within the reviewed scope. Friendly wording must not
soften a blocker or turn a confirmed failure into a speculative concern.

State the recommendation in ordinary prose with the decisive reason. The decision labels
below describe outcomes, not mandatory headings or formulaic phrases. Say whether fixes,
another reviewer's clearance, or a missing check are needed before approval. Follow with a
checks or limitations sentence when useful. Do not repeat inline findings as a table or checklist,
enumerate empty severity buckets, or add a routine confidence legend or nine-axis table.
No supported findings does not imply system correctness.
For a historical merged PR, put its reviewed revision and demo context in a short separate
note, and use conditional language such as "I would hold approval until...". Keep any
authorized format demonstration comment-only.

End the overall comment with a short, transparent attribution and the review level, as
shown above. Keep it after checks and any historical note. Natural
wording does not mean pretending a human performed or approved the review. Do not invent
a model, reviewer identity, or human sign-off. Keep draft handoff instructions outside the
proposed comment so the user can edit and publish it without removing process boilerplate.

## Inline comments

Use Markdown code spans as portable tags, ordered axis, severity, then confidence only
when low. Prefer one primary axis; short labels such as Correctness, Security, Reliability,
Performance, Simplification, Reuse, Architecture, Tests, and Docs map to the rubric axes.
Keep secondary axes in the evidence record unless they materially clarify the comment.

```markdown
`Correctness` `P2` **Restore pagination through the existing export helper**

When an account has more than one page, this call exports only the first page and omits
the remaining orders. The base implementation used `customer_batches`, which follows
`next_cursor` and is still used by the web route. Could we use that shared path here too?
```

Anchor the comment to a short verified changed range. The paragraph should explain the
trigger, failure, consequence, supporting evidence, and smallest useful correction.
Use respectful, collaborative language for the proposed fix while stating established
failures directly. A polite request such as "Could we use the existing helper?" does not
make a verified finding a low-confidence question. Reserve that tag for missing evidence.
Mention reproductions when relevant without adding a separate confidence label. Preserve
the evidenced serious impact and exposure required for P0/P1. Avoid untested patches.
If no reliable inline anchor exists, use a file-level or overall location and explain it.

No confidence tag means the claim meets the rubric's high-confidence bar. If material
uncertainty remains, including an internally medium-confidence assessment, resolve it
or present a question with `Low confidence`; never silently upgrade it to high.

```markdown
`Architecture` `Potential P2` `Low confidence` **Confirm the external consumer contract**

Does the external consumer still require the old field? Its contract is unavailable.
If it does, the rename would break deserialization. Obtain that contract before treating
this as a defect or choosing a compatibility layer.
```

Keep these questions separate from confirmed findings and counts. State the missing
evidence and how to resolve it. Optional polish uses `Nit` and is included only on request.

## Approval recommendation

Always give an opinion, independently of whether publication is authorized. Use current
provider review state before the recommendation and refresh it before any authorized
approval action. Read the complete relevant state, not just the latest comment or an
aggregate approval count. Prefer the provider's effective per-reviewer decision; if only
history is available, reconcile explicit review/dismissal events without guessing.

- Another reviewer's effective request for changes means **Hold approval**, even when
  this review finds no defect. Link the outstanding review and state what must be cleared.
  Another person's approval, a later COMMENT/PENDING review, or outdated diff anchors
  do not clear it. A verified superseding approval from that reviewer or an explicit
  dismissal can. Do not dismiss someone else's review or override it through approval.
- Any confirmed P0/P1 means **Request changes** and withhold approval. State the impact.
- Two or more independent material P2 findings normally mean **Request changes**; explain
  why the combined impact warrants correction before approval. Deduplicate first, and do
  not count secondary tags, duplicate comments, or low-confidence questions as extra P2s.
- Judge a single P2 by its consequence and the repository's merge criteria. P3/Nit alone
  are normally nonblocking. When no blocker remains and review state is known, recommend
  **Approve**, scoped to what was reviewed. This is not a claim that GitHub can merge.
- If review state or evidence critical to the decision is unavailable, **Hold approval**
  pending that specific check. A local diff can have no findings while remote approval
  readiness remains unknown. Ordinary low-confidence questions alone are not blockers.

When both peer requests and this review's defects block, explain both briefly. Severity
continues to follow evidenced impact; merge criteria must not inflate the priority label.
Submitting APPROVE, REQUEST_CHANGES, or COMMENT requires authorization for that action.
A request to show formatting or publish comments does not authorize approval/status changes.

## Companion evidence record

Retain all nine axes with reviewed/partial/not_applicable/skipped, assessment confidence,
and evidence or gaps. Also retain finding confidence and secondary axes, repository/PR,
base tip, merge base, head, peer-review state and retrieval completeness, requested versus
observable model/effort, depth/holistic, actual delegation, applicable guidance and missing
sources, checks executed, exclusions, and failed workstreams. A local artifact or host
record is sufficient; a compact attached section is a fallback when no companion is possible.
Do not put local-only links into published comments. Surface any limitation that materially
changes the recommendation in the visible comment rather than hiding it in the record.

GitHub state semantics: [review decisions](https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/reviewing-proposed-changes-in-a-pull-request)
and [dismissals](https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/dismissing-a-pull-request-review).
