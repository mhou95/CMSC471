#!/usr/bin/env python3
"""
End-to-end smoke test for CMSC 471 Final Project.

Usage:
    python tests/smoke_test.py --image path/to/doc.jpg
    python tests/smoke_test.py --image path/to/doc.jpg --endpoint https://<id>.execute-api.us-east-1.amazonaws.com/Prod

If --endpoint is omitted, the script reads it from the deployed CloudFormation stack.
Output is printed to stdout and also saved to docs/evidence/smoke_test_<timestamp>.txt.

Requirements:
    pip install requests boto3
"""

import argparse
import base64
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import boto3
import requests

STACK_NAME = "cmsc471-final"
POLL_INTERVAL_SEC = 5
POLL_TIMEOUT_SEC = 120


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class Log:
    """Collects output for both stdout and the evidence file."""
    lines: list[str] = []

    @classmethod
    def print(cls, msg: str = "") -> None:
        print(msg)
        cls.lines.append(msg)

    @classmethod
    def save(cls, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(cls.lines), encoding="utf-8")
        print(f"\nEvidence saved → {path}")


def ok(label: str) -> None:
    Log.print(f"  [PASS] {label}")


def fail(label: str, detail: str = "") -> None:
    Log.print(f"  [FAIL] {label}" + (f": {detail}" if detail else ""))
    sys.exit(1)


def step(n: int, title: str) -> None:
    Log.print(f"\nStep {n}: {title}")
    Log.print("-" * 50)


# ---------------------------------------------------------------------------
# Stack helpers
# ---------------------------------------------------------------------------

def get_stack_outputs() -> dict[str, str]:
    cfn = boto3.client("cloudformation")
    try:
        stack = cfn.describe_stacks(StackName=STACK_NAME)["Stacks"][0]
    except Exception as e:
        fail("CloudFormation stack not found", str(e))
    return {o["OutputKey"]: o["OutputValue"] for o in stack.get("Outputs", [])}


# ---------------------------------------------------------------------------
# Smoke test steps
# ---------------------------------------------------------------------------

def check_index_page(api: str) -> None:
    step(1, "GET / — index page loads")
    r = requests.get(api + "/", timeout=15)
    if r.status_code == 200 and "text/html" in r.headers.get("Content-Type", ""):
        ok(f"GET / returned 200 text/html ({len(r.text)} bytes)")
    else:
        fail("GET /", f"status={r.status_code} content-type={r.headers.get('Content-Type')}")


def upload_image(api: str, image_path: Path) -> str:
    step(2, f"POST /api/inbox — upload {image_path.name}")
    image_bytes = image_path.read_bytes()
    payload = {
        "filename": image_path.name,
        "data": base64.b64encode(image_bytes).decode(),
    }
    r = requests.post(
        api + "/api/inbox",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    if r.status_code != 200:
        fail("POST /api/inbox", f"status={r.status_code} body={r.text[:200]}")
    body = r.json()
    object_key = body.get("objectKey")
    if not object_key:
        fail("POST /api/inbox", f"no objectKey in response: {body}")
    ok(f"Uploaded → objectKey={object_key}")
    return object_key


def submit_job(api: str, object_key: str) -> str:
    step(3, "POST /api/jobs — start transcription job")
    r = requests.post(
        api + "/api/jobs",
        json={"imageKey": object_key},
        headers={"Content-Type": "application/json"},
        timeout=15,
    )
    if r.status_code != 200:
        fail("POST /api/jobs", f"status={r.status_code} body={r.text[:200]}")
    body = r.json()
    job_id = body.get("jobId")
    if not job_id:
        fail("POST /api/jobs", f"no jobId in response: {body}")
    ok(f"Job started → jobId={job_id}")
    Log.print(f"         executionArn={body.get('executionArn', 'n/a')}")
    return job_id


def poll_job(api: str, job_id: str) -> dict:
    step(4, f"GET /api/jobs/{job_id} — polling until SUCCEEDED or FAILED")
    deadline = time.time() + POLL_TIMEOUT_SEC
    last_status = None
    while time.time() < deadline:
        r = requests.get(api + f"/api/jobs/{job_id}", timeout=15)
        if r.status_code == 404:
            Log.print("  ... job not yet in DynamoDB, waiting")
            time.sleep(POLL_INTERVAL_SEC)
            continue
        if r.status_code != 200:
            fail(f"GET /api/jobs/{job_id}", f"status={r.status_code} body={r.text[:200]}")
        body = r.json()
        status = body.get("status", "UNKNOWN")
        if status != last_status:
            Log.print(f"  ... status={status}")
            last_status = status
        if status == "SUCCEEDED":
            ok(f"Job SUCCEEDED")
            return body
        if status == "FAILED":
            fail("Job FAILED", body.get("error", "see CloudWatch logs"))
        time.sleep(POLL_INTERVAL_SEC)
    fail("Polling timed out", f"last status={last_status} after {POLL_TIMEOUT_SEC}s")


def check_records(api: str, job_id: str, expected_key: str) -> None:
    step(5, "GET /api/records — verify extracted text stored")
    r = requests.get(api + "/api/records", timeout=15)
    if r.status_code != 200:
        fail("GET /api/records", f"status={r.status_code}")
    records = r.json()
    match = [rec for rec in records if rec.get("jobId") == job_id]
    if not match:
        fail("GET /api/records", f"jobId={job_id} not found in {len(records)} records")
    text = match[0].get("extractedText", "")
    ok(f"Record found — {len(text)} chars of extracted text")
    if text.strip():
        preview = text.strip()[:200].replace("\n", " ")
        Log.print(f"  Extracted text preview: \"{preview}\"")
    else:
        Log.print("  WARNING: extractedText is empty — check Textract had readable content")


def verify_s3_object(outputs: dict, object_key: str) -> None:
    step(6, "S3 inbox — verify raw image object exists")
    bucket = outputs.get("InboxBucketName")
    if not bucket:
        Log.print("  SKIP: InboxBucketName not in stack outputs")
        return
    s3 = boto3.client("s3")
    try:
        s3.head_object(Bucket=bucket, Key=object_key)
        ok(f"s3://{bucket}/{object_key} exists")
    except Exception as e:
        fail(f"s3://{bucket}/{object_key}", str(e))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="CMSC 471 end-to-end smoke test")
    parser.add_argument("--image", required=True,
                        help="Path to a JPEG or PNG image with readable text")
    parser.add_argument("--endpoint",
                        help="API Gateway base URL (auto-detected from CloudFormation if omitted)")
    parser.add_argument("--stack", default=STACK_NAME,
                        help=f"CloudFormation stack name (default: {STACK_NAME})")
    args = parser.parse_args()

    image_path = Path(args.image)
    if not image_path.exists():
        print(f"ERROR: image file not found: {image_path}")
        sys.exit(1)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    evidence_path = Path("docs/evidence") / f"smoke_test_{timestamp}.txt"

    Log.print("=" * 60)
    Log.print("CMSC 471 — End-to-End Smoke Test")
    Log.print(f"Timestamp : {timestamp}")
    Log.print(f"Image     : {image_path}")
    Log.print("=" * 60)

    # Resolve API endpoint
    outputs = {}
    if args.endpoint:
        api = args.endpoint.rstrip("/")
        Log.print(f"Endpoint  : {api}  (from --endpoint)")
    else:
        Log.print(f"\nReading stack outputs from CloudFormation ({args.stack})...")
        outputs = get_stack_outputs()
        api = outputs.get("ApiEndpoint", "").rstrip("/")
        if not api:
            fail("ApiEndpoint not found in stack outputs",
                 "Deploy the stack first or pass --endpoint manually")
        Log.print(f"Endpoint  : {api}  (from CloudFormation)")

    # Run steps
    check_index_page(api)
    object_key = upload_image(api, image_path)
    job_id = submit_job(api, object_key)
    poll_job(api, job_id)
    check_records(api, job_id, object_key)
    verify_s3_object(outputs, object_key)

    Log.print("\n" + "=" * 60)
    Log.print("ALL STEPS PASSED — smoke test complete")
    Log.print("=" * 60)
    Log.print(f"\nJobId      : {job_id}")
    Log.print(f"ObjectKey  : {object_key}")
    Log.print(f"API        : {api}")

    Log.save(evidence_path)


if __name__ == "__main__":
    main()
