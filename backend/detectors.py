"""
Wrapper around the 3 Roboflow-hosted RF-DETR *Workflows* (pothole, garbage,
road encroachment). Each was built in Roboflow's Workflow builder (that's
what the "-logic" suffix in each ID means), which uses a different call
shape than a plain single model: POST JSON to
    https://serverless.roboflow.com/{workspace_name}/workflows/{workflow_id}
instead of the simpler /{model_id}/{version} form.

All 3 workflows live under one Roboflow workspace, so they share
ROBOFLOW_WORKSPACE + ROBOFLOW_API_KEY; each still has its own workflow id.
"""
import base64
import os
import requests

ROBOFLOW_INFER_URL = "https://serverless.roboflow.com"

DETECTOR_CONFIG = {
    "pothole": {
        "label": "Pothole",
        "workflow_env": "ROBOFLOW_POTHOLE_WORKFLOW_ID",
    },
    "garbage": {
        "label": "Garbage Area",
        "workflow_env": "ROBOFLOW_GARBAGE_WORKFLOW_ID",
    },
    "encroachment": {
        "label": "Road Encroachment",
        "workflow_env": "ROBOFLOW_ENCROACHMENT_WORKFLOW_ID",
    },
}


def _find_predictions(obj, depth=0):
    """Workflow output shape depends on how each workflow was built, so
    instead of assuming a fixed key, walk the JSON and return the first
    list of dicts that look like predictions (each has a 'confidence'
    key). This makes us resilient to different workflow output schemas."""
    if depth > 6:
        return None
    if isinstance(obj, list):
        if obj and all(isinstance(i, dict) and "confidence" in i for i in obj):
            return obj
        for item in obj:
            found = _find_predictions(item, depth + 1)
            if found is not None:
                return found
    elif isinstance(obj, dict):
        for value in obj.values():
            found = _find_predictions(value, depth + 1)
            if found is not None:
                return found
    return None


def _run_one_model(detector_key: str, image_bytes: bytes, timeout: int = 25):
    """Call one Roboflow Workflow with a JPEG frame. Returns:
    {"detector": key, "label": ..., "predictions": [...], "error": str|None}
    """
    cfg = DETECTOR_CONFIG[detector_key]
    api_key = os.environ.get("ROBOFLOW_API_KEY")
    workspace = os.environ.get("ROBOFLOW_WORKSPACE")
    workflow_id = os.environ.get(cfg["workflow_env"])

    result = {"detector": detector_key, "label": cfg["label"], "predictions": [], "error": None}

    if not api_key or "your_" in api_key:
        result["error"] = "ROBOFLOW_API_KEY not configured"
        return result
    if not workspace or "your-" in workspace:
        result["error"] = "ROBOFLOW_WORKSPACE not configured"
        return result
    if not workflow_id or "your-" in workflow_id:
        result["error"] = f"{cfg['workflow_env']} not configured"
        return result

    b64_image = base64.b64encode(image_bytes).decode("utf-8")
    url = f"{ROBOFLOW_INFER_URL}/{workspace}/workflows/{workflow_id}"
    body = {
        "api_key": api_key,
        "inputs": {"image": {"type": "base64", "value": b64_image}},
    }

    try:
        resp = requests.post(url, json=body, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        preds = _find_predictions(data)
        result["predictions"] = preds or []
        if preds is None:
            result["error"] = (
                "Workflow ran but no prediction list was found in the "
                f"response — raw keys: {list(data.keys()) if isinstance(data, dict) else type(data)}"
            )
    except requests.exceptions.HTTPError as e:
        body_text = ""
        try:
            body_text = e.response.text[:300]
        except Exception:
            pass
        result["error"] = f"{e} — {body_text}"
    except requests.exceptions.RequestException as e:
        result["error"] = str(e)

    return result


def run_all_detectors(image_bytes: bytes):
    """Run all 3 workflows against the same frame."""
    return [_run_one_model(key, image_bytes) for key in DETECTOR_CONFIG]


def best_prediction(predictions):
    """Given a predictions list, return the highest-confidence one."""
    if not predictions:
        return None
    return max(predictions, key=lambda p: p.get("confidence", 0))
