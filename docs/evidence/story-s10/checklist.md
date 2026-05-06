# Story S10 — RDS MySQL Results Database (jobId, extractedText, createdAt)

**Azure DevOps AB#:** (fill in)
**Feature file:** `tests/acceptance/features/persistence_tier.feature` — "Verify RDS MySQL results database exists"

## Audit Trail Checklist

- [ ] `requirement.png` — screenshot of DevOps story S10 in *Done* state
- [ ] `pytest_output.txt` — output of `pytest tests/acceptance -v -k "RDS"` showing PASSED
- [ ] `commit_link.txt` — GitHub link to commit with `Fixes AB#<id>` for this story

## Learner Lab Note

If `LimitExceededException` occurs during deploy, the Learner Lab may not have RDS quota available.
Fallback: comment out `ResultsDatabase` in template.yaml and document the quota limitation here.
