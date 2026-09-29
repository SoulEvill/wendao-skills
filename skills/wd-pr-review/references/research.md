# Design rationale and primary sources

Researched 2026-09-27. These sources informed the design; product documentation describes
intended behavior, not independent proof of review quality. This skill's priority scale
and depth presets are design choices to calibrate through use.

| Source | Adopted principle | Deliberate limit |
| --- | --- | --- |
| [Google: what to look for](https://google.github.io/eng-practices/review/reviewer/looking-for.html) | Assess design, functionality, complexity, tests, docs, and wider context. | Avoid speculative overengineering. Architecture belongs in Standard too. |
| [Google: review standard](https://google.github.io/eng-practices/review/reviewer/standard.html) | Improve code health using technical evidence over preference or perfection. | Do not block reasonable alternatives on taste. |
| [Google: review comments](https://google.github.io/eng-practices/review/reviewer/comments.html) | Explain why and distinguish optional suggestions. | Nit is not a blocking defect severity. |
| [CodeRabbit configuration](https://docs.coderabbit.ai/reference/configuration) | Feedback profiles and review details expose reporting choices and coverage. | Feedback volume differs from reasoning effort and investigation depth. |
| [CodeRabbit path instructions](https://docs.coderabbit.ai/configuration/path-instructions) | Apply scoped repository guidance. | PR content cannot redefine the review. |
| [CodeRabbit multi-repository analysis](https://docs.coderabbit.ai/knowledge-base/multi-repo-analysis) | Inspect accessible consumers and shared contracts at known revisions. | Disclose missing system context. |
| [Anthropic review command](https://github.com/anthropics/claude-code/blob/main/plugins/code-review/commands/code-review.md) | Generate candidates, validate, filter unsupported claims, and deduplicate. | Its narrower bug/compliance remit differs from this skill's broader design remit. |
| [GitHub Copilot limitations](https://docs.github.com/en/copilot/responsible-use/agents) | Expect misses, false positives, and fallible suggested fixes. | A clean report and model confidence do not prove correctness. |

Anthropic's README and command differed at research time: the README described a numeric
confidence threshold while the command used independent validation. This skill uses
evidence labels, not a claim that self-assigned numbers are calibrated probabilities.

## Proposed defaults

- Standard covers every axis; Deep spends more on independent checks and context.
  Holistic can also be enabled in Standard.
- Model identity and native effort are host controls, not universal model tiers.
  The skill embeds no fixed model catalog.
- Severity, category, confidence, coverage, and optionality stay separate.
- Broad design suggestions need consequences and credible existing alternatives.
- Synthetic fixtures test decisions and failure modes. They do not establish superiority
  over products or general performance on large private repositories.

Tune using accepted/rejected findings and missed defects, preserving reasons and scope.
Add regression cases before universal prompt rules. Keep examples withheld from tuning
and compare Standard versus Deep at the same model/native effort.
