# Story S8 — Uploaded Image Returns Extracted Text

**Azure DevOps AB#:** (fill in)
**Feature file:** `tests/acceptance/features/orchestration_tier.feature` — "Verify Textract Lambda function exists"

## Audit Trail Checklist

- [ ] `requirement.png` — screenshot of DevOps story S8 in *Done* state
- [ ] `pytest_output.txt` — output of `pytest tests/acceptance -v -k "Textract"` showing PASSED
- [ ] `commit_link.txt` — GitHub link to commit with `Fixes AB#<id>` for this story
- [ ] `smoke_test.png` — end-to-end screenshot: image uploaded → `/api/jobs/{id}` status SUCCEEDED → extracted text visible in `/api/records`
