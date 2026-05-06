# Total Cost of Ownership (TCO) Analysis

## CMSC 471 Final Project - Image-to-Text Application

---

## Executive Summary

This document analyzes the cost of running a serverless image-to-text application on AWS for a 12-month period using AWS Academy Learner Lab account.

**Key Assumption:** Learner Lab provides minimal/free tier credits; costs below assume commercial pricing for reference only. In actual Learner Lab, most services are free but with quotas.

---

## Workload Profile

### Monthly Volume Estimates

| Metric | Value |
|--------|-------|
| Images processed/month | 1,000 |
| Avg image size | 2 MB |
| Monthly API requests | 5,000 |
| Avg processing time per image | 15 seconds |

---

## Service-Level Cost Breakdown (Commercial Pricing)

### 1. AWS Lambda

**Pricing Model:** $0.0000002 per invocation + $0.0000166667 per GB-second

**Monthly Breakdown:**
- **Index Handler** (GET /): 500 invocations × 512 MB × 1 sec = 256 GB-seconds
  - Compute: 500 × $0.0000002 + 256 × $0.0000166667 = $0.00429 ≈ **$0.01**

- **Submit Handler** (POST /api/jobs): 100 invocations × 512 MB × 2 sec = 102.4 GB-seconds
  - Compute: 100 × $0.0000002 + 102.4 × $0.0000166667 = $0.00171 ≈ **$0.01**

- **Poll Handler** (GET /api/jobs/{id}): 1,000 invocations × 512 MB × 0.5 sec = 256 GB-seconds
  - Compute: 1,000 × $0.0000002 + 256 × $0.0000166667 = $0.00429 ≈ **$0.01**

- **Fetch Image, Call Textract, Save Results** (Step Functions): 1,000 × 3 steps × 512 MB × 30 sec = 46,080 GB-seconds
  - Compute: 3,000 × $0.0000002 + 46,080 × $0.0000166667 = **$0.77**

**Total Lambda/month:** ~**$0.80**

---

### 2. Amazon Textract

**Pricing Model:** $1.50 per 1,000 pages (images)

**Monthly:**
- 1,000 images/month × $1.50 / 1,000 = **$1.50/month**

---

### 3. DynamoDB

**Pricing Model (On-Demand):** $1.25 per 1M write units, $0.25 per 1M read units

**Monthly:**
- Write Units: 1,000 jobs × 2 writes (create + update) = 2,000 writes
  - Cost: 2,000 / 1,000,000 × $1.25 = **$0.0025**

- Read Units: 5,000 reads (polling) / 1,000,000 × $0.25 = **$0.00125**

- Storage: ~50 KB per job × 1,000 jobs = 50 MB
  - Cost: 50 / 1,000 × $1.25 = **$0.0625/month** (first 25 GB free)

**Total DynamoDB/month:** ~**$0.07**

---

### 4. S3 Storage & Transfer

**Pricing Model:**
- Storage: $0.023 per GB/month
- Requests: $0.0004 per 1,000 PUT, $0.0002 per 1,000 GET
- Lifecycle transitions: Included

**Monthly:**
- **Inbox Bucket (raw images):**
  - Storage: 1,000 images × 2 MB × $0.023 = **$46.00/month** (assumes all stored for 30 days before Glacier)
  - Glacier transition: Free after 30 days, then $0.004/GB/month
  - After transition: 2,000 MB × $0.004 = **$8.00/month** (aged images)

- **Static Site Bucket:**
  - Storage: ~500 KB × $0.023 = **$0.01/month**

- **Requests:**
  - PUTs (uploads): 1,000 × $0.0004 / 1,000 = **$0.0004**
  - GETs (reads): 2,000 × $0.0002 / 1,000 = **$0.0004**

**Total S3/month:** ~**$54.01** (reducing to ~$8.01 after Glacier transition on aged data)

---

### 5. Step Functions

**Pricing Model:** $0.000025 per state transition

**Monthly:**
- 1,000 jobs × 3 states = 3,000 transitions
- Cost: 3,000 × $0.000025 = **$0.075/month**

---

### 6. API Gateway

**Pricing Model:** $3.50 per million API calls

**Monthly:**
- 5,000 API requests (index, jobs, polls)
- Cost: 5,000 / 1,000,000 × $3.50 = **$0.0175/month**

---

### 7. CloudWatch (Logs & Monitoring)

**Pricing Model:** $0.50 per GB ingested, $0.03 per GB stored

**Monthly:**
- Log ingestion: ~500 MB/month = 0.5 GB × $0.50 = **$0.25**
- Log storage (14-day retention): 0.5 GB × $0.03 = **$0.015**

**Total CloudWatch/month:** ~**$0.27**

---

### 8. NAT Gateway

**Pricing Model:** $0.045/hr + $0.045/GB data processed

**Monthly:**
- Hourly charge: $0.045 × 720 hrs = **$32.40/month** (idle — no data needed)
- Data processed by 1,000 jobs × ~2 MB × $0.045/GB ≈ **$0.09/month**

**Total NAT Gateway/month:** ~**$32.50**

> **Warning:** This is the dominant *idle* cost. The NAT Gateway charges by the
> hour whether or not traffic flows. Delete the stack at the end of every lab
> session or it will drain ~$32 of Learner Lab credits per month.

---

### 9. RDS MySQL db.t3.micro

**Pricing Model:** $0.017/hr (us-east-1, Single-AZ, gp2 storage)

**Monthly:**
- Instance hours: $0.017 × 720 hrs = **$12.24/month**
- Storage (20 GB gp2): 20 × $0.115 / 12 = **$0.19/month**

**Total RDS/month:** ~**$12.43**

> **Warning:** Like the NAT Gateway, RDS charges by the hour when idle.
> Together, NAT + RDS = **~$44/month** of fixed idle cost.

---

## Monthly & Annual Cost Summary

| Service | Monthly | Annual |
|---------|---------|--------|
| Lambda | $0.80 | $9.60 |
| Textract | $1.50 | $18.00 |
| DynamoDB | $0.07 | $0.84 |
| S3 (first month) | $54.01 | ~$150 avg |
| Step Functions | $0.075 | $0.90 |
| API Gateway | $0.0175 | $0.21 |
| CloudWatch | $0.27 | $3.24 |
| NAT Gateway | $32.50 | $390 |
| RDS db.t3.micro | $12.43 | $149 |
| **TOTAL** | **~$102** | **~$722** |

**Note:** After S3 Glacier transition (30 days), monthly cost drops to ~$10 as archived images cost 80% less.

---

## Cost Optimization Strategies

### 1. S3 Lifecycle Management (Implemented)
- **Savings:** 88% reduction on aged images after 30 days (from $0.023 to $0.004/GB)
- **Annual saving:** ~$600 for typical workloads

### 2. DynamoDB On-Demand (Implemented)
- **vs. Provisioned:** Only pay for what you use; auto-scales
- **Savings:** No idle capacity charges
- **Annual saving:** ~$50-200 depending on usage patterns

### 3. Lambda Right-Sizing (Implemented)
- **512 MB allocation:** Balances cost and performance
- **vs. 1024 MB:** Would double cost
- **Annual saving:** ~$3-5

### 4. CloudWatch Log Retention (Implemented)
- **14-day retention:** Balances troubleshooting vs. storage cost
- **vs. infinite retention:** Would cost $1.5K+/year for typical workloads
- **Annual saving:** ~$200

### 5. Avoiding Over-Provisioning
- **No Aurora cluster** (too expensive for Learner Lab)
- **No CloudFront** (API Gateway is free tier-eligible)
- **No always-on EC2** (serverless only)
- **Annual saving:** ~$300-500

---

## AWS Pricing Calculator Export

[Link to shared calculator model](https://calculator.aws)

**Assumption Set:**
- Region: `us-east-1`
- Lambda: 1,000 invocations/month, 512 MB, 30 sec
- DynamoDB: On-demand, 1M RCU + 1M WCU budget
- S3: 1,000 images/month, 2 MB each, 30-day lifecycle
- Textract: 1,000 documents/month
- CloudWatch: 500 MB logs/month, 14-day retention

---

## Break-Even Analysis

**Fixed costs:** ~$2/month (API Gateway, Step Functions, CloudWatch baseline)
**Variable cost per job:** ~$0.057

For typical university project:
- **100 images/month**: ~$7/month
- **1,000 images/month**: ~$57/month
- **10,000 images/month**: ~$570/month

All well within Learner Lab free tier and undergraduate budget.

---

## Comparison: Alternative Architectures

| Architecture | Monthly Cost | Pros | Cons |
|--------------|--------------|------|------|
| **Serverless (This Design)** | ~$57 | Auto-scales, low fixed cost | Slight latency on cold start |
| **EC2-based** | ~$150-500 | Always-on performance | Always paying; needs scaling |
| **On-premises** | $500+ | One-time purchase | Capital cost, maintenance |

---

## Notes for AWS Academy Learner Lab

1. **Learner Lab provides free credits** (~$100-150/session)
2. **Quotas apply** — max 2 concurrent Lambdas, limited Textract calls
3. **No data transfer costs** between services in same region
4. **No cross-region replication** (stays in one region)

For this project, costs are negligible within Learner Lab free tier.

---

## Recommendations

1. ✅ **Use S3 Lifecycle** to move old images to Glacier
2. ✅ **Monitor CloudWatch dashboard** to catch unexpected cost spikes
3. ✅ **Right-size Lambda** — profile actual memory usage
4. ✅ **Delete test data regularly** — don't let test images accumulate
5. ⚠️ **Set CloudWatch Alarms** if costs exceed estimate

---

**Last Updated:** April 2026  
**Workload Profile:** Typical academic use case  
**Pricing Data:** AWS Pricing as of Q2 2026
