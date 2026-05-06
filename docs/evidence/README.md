# Evidence Directory

Each subfolder holds the three-way audit trail for one user story:

1. **requirement.png** — screenshot of the Azure DevOps story in *Done* state
2. **pytest_output.txt** — green `pytest` output for the matching `.feature` scenario
3. **commit_link.txt** — GitHub URL of the commit that closes this story (via `Fixes AB#<id>`)

| Story | Feature | AB# | Folder |
|---|---|---|---|
| S1 | VPC CIDR 10.0.0.0/16 | AB#? | story-s1/ |
| S2 | Two public + two private subnets | AB#? | story-s2/ |
| S3 | NAT Gateway for private subnets | AB#? | story-s3/ |
| S4 | S3 static site bucket | AB#? | story-s4/ |
| S5 | API Gateway GET / → index.html | AB#? | story-s5/ |
| S6 | POST /api/inbox multipart upload | AB#? | story-s6/ |
| S7 | Step Functions FetchImage→CallTextract→SaveResults | AB#? | story-s7/ |
| S8 | Uploaded image → extracted text returned | AB#? | story-s8/ |
| S9 | DynamoDB JobState table | AB#? | story-s9/ |
| S10 | RDS MySQL results database | AB#? | story-s10/ |
| S11 | S3 lifecycle → Glacier after 30 days | AB#? | story-s11/ |
