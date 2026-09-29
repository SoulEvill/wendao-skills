# PR diff navigation

Give the user a web link to the PR's commenting location, separate from the proposed
comment body. Keep one-based path/side/start/end coordinates and the reviewed head in
the companion record. A repository blob permalink is useful evidence, but does not
replace the PR diff link for manual commenting.

## GitHub

Prefer the URL produced by selecting a line or Shift-selecting a range in Files changed,
or its actual file/line anchors exposed by the host. The current observed URL convention is:

```text
<PR URL>/files#diff-<file-anchor>R18
<PR URL>/files#diff-<file-anchor>R18-R20
<PR URL>/files#diff-<file-anchor>L18-L20
```

`R` uses new-side line numbers for additions/context; `L` uses old-side numbers for
deletions. These are file line numbers, not patch positions. Keep the range tight and on
one side; use separate locations when needed. For renamed files, use the path represented
by the PR's displayed file anchor and the correct side's numbering.

When the actual URL is unavailable, construct a candidate using the current convention:
the file anchor is the lowercase SHA-256 hex digest of the exact repository-relative
filename encoded as UTF-8, without a trailing newline. It is not the file's blob SHA.
Verify the filename and line range from the PR diff. This format was checked against
GitHub's live UI on 2026-09-28; it is an observed convention, not an API guarantee.

Open and check the highlighted location when browser access is available. Otherwise
record that the URL was constructed from verified diff coordinates and that the browser
highlight was not checked. An HTTP 200 response alone does not validate a fragment.
If the format no longer matches, or the path/coordinates cannot be established, use the
verified file-level diff URL or the PR's Files changed page and state the limitation.
Do not fabricate an exact link to hide missing context.

These links follow the PR's current diff. Recheck the head before handing off the draft
and before publication; remap anchors after reviewing any new changes. Keep an immutable
source permalink separately when useful for preserving evidence.

The link selects the review location; it does not automatically open or prefill a comment.
The user can use the line's comment control (`+`) and paste the proposed body. See
[GitHub commenting instructions](https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/commenting-on-a-pull-request)
and [review-comment coordinates](https://docs.github.com/en/rest/pulls/comments#create-a-review-comment-for-a-pull-request).
