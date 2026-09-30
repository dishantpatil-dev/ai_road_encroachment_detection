"""
Quick standalone test for each of the 3 Roboflow Workflows, independent
of Flask/the browser. Run this first whenever a workflow isn't behaving —
it prints the raw HTTP status and response body.

Usage:
    python test_roboflow.py path/to/a/road/photo.jpg
"""
import base64
import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

ROBOFLOW_INFER_URL = "https://serverless.roboflow.com"
API_KEY = os.environ.get("ROBOFLOW_API_KEY")
WORKSPACE = os.environ.get("ROBOFLOW_WORKSPACE")

WORKFLOWS = {
    "pothole": os.environ.get("ROBOFLOW_POTHOLE_WORKFLOW_ID"),
    "garbage": os.environ.get("ROBOFLOW_GARBAGE_WORKFLOW_ID"),
    "encroachment": os.environ.get("ROBOFLOW_ENCROACHMENT_WORKFLOW_ID"),
}


def test_workflow(name, workflow_id, image_bytes):
    print(f"\n=== {name} (workflow: {workflow_id}) ===")
    if not workflow_id:
        print("  SKIPPED — no workflow id set in .env")
        return
    url = f"{ROBOFLOW_INFER_URL}/{WORKSPACE}/workflows/{workflow_id}"
    b64_image = base64.b64encode(image_bytes).decode("utf-8")
    body = {"api_key": API_KEY, "inputs": {"image": {"type": "base64", "value": b64_image}}}
    try:
        resp = requests.post(url, json=body, timeout=25)
        print(f"  URL: {url}")
        print(f"  HTTP {resp.status_code}")
        text = resp.text[:800]
        print(f"  Body: {text}")
        if resp.status_code == 200:
            try:
                data = resp.json()
                print(f"  Top-level keys: {list(data.keys()) if isinstance(data, dict) else type(data)}")
            except Exception:
                pass
    except requests.exceptions.RequestException as e:
        print(f"  ERROR: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_roboflow.py path/to/image.jpg")
        sys.exit(1)

    if not API_KEY:
        print("ROBOFLOW_API_KEY is not set in .env — set it first.")
        sys.exit(1)
    if not WORKSPACE:
        print(
            "ROBOFLOW_WORKSPACE is not set in .env.\n"
            "Find it: open any of your workflows in Roboflow -> 'Deploy Workflow' "
            "-> the code snippet shown there has workspace_name=\"...\" — copy "
            "that exact value into .env as ROBOFLOW_WORKSPACE."
        )
        sys.exit(1)

    with open(sys.argv[1], "rb") as f:
        img_bytes = f.read()

    for name, workflow_id in WORKFLOWS.items():
        test_workflow(name, workflow_id, img_bytes)

    print(
        "\nIf you see HTTP 200 -> check 'Top-level keys' printed above and tell "
        "Claude what they are, so the prediction-extraction logic can be "
        "pointed at the right field if needed.\n"
        "If you see 401 -> ROBOFLOW_API_KEY is wrong.\n"
        "If you see 404 -> ROBOFLOW_WORKSPACE or the workflow id is wrong.\n"
        "If you see 405 -> this still isn't a Workflow id in the "
        "workspace/workflow_id shape — double check on the 'Deploy Workflow' "
        "page."
    )
