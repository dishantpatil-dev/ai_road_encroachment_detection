# CivicScan — Live Road Issue Detection

Uses your webcam (or an uploaded dashcam video) to detect **potholes**,
**garbage areas**, and **road encroachment** with your 3 Roboflow-trained
models, confirms each candidate with **Gemini**, and pins confirmed issues
on a live map with the current GPS location.
<img width="1366" height="768" alt="62a0e29b-7fdb-4d2f-b902-c7e7c9125a0e" src="https://github.com/user-attachments/assets/95deb616-a328-44ad-8b5f-a4a56fd651e9" />


```
Camera / video frame
      │
      ▼
Roboflow ×3  (pothole / garbage / encroachment models — parallel)
      │  (candidate above confidence threshold?)
      ▼
Gemini API   (confirms it's genuine, not a shadow/false positive)
      │  (confirmed?)
      ▼
Pinned on the live map with GPS coords
```

## 1. Requirements

- Python 3.9+
- A webcam (for live mode) — the app runs in your browser, so it works on
  laptop/phone browsers that support camera + geolocation permissions
- Your 4 API keys:
  - **Google API key** (Gemini) — https://aistudio.google.com/apikey
  - **3 Roboflow API keys + model IDs** — one per trained model (pothole,
    garbage, encroachment), from each project's Roboflow dashboard under
    **Deploy**

## 2. Setup

```bash
cd civicscan-app
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r backend/requirements.txt

cp .env.example .env
```

Open `.env` and fill in your real keys:

```ini
GOOGLE_API_KEY=AIza...

ROBOFLOW_POTHOLE_API_KEY=...
ROBOFLOW_POTHOLE_MODEL=your-pothole-project/2      # from Roboflow "Deploy" tab

ROBOFLOW_GARBAGE_API_KEY=...
ROBOFLOW_GARBAGE_MODEL=your-garbage-project/1

ROBOFLOW_ENCROACHMENT_API_KEY=...
ROBOFLOW_ENCROACHMENT_MODEL=your-encroachment-project/1
```

The `MODEL` value is the `model_id/version` shown on your Roboflow
project's **Deploy** page (e.g. `pothole-detection-ab12c/3`) — not the
project name alone.

## 3. Run

```bash
cd backend
python app.py
```

Open **http://localhost:5000** in your browser (Chrome/Edge work best for
camera + geolocation prompts). If you deploy this to a real server, note
that browsers only allow camera/geolocation access over **HTTPS** (or
`localhost`) — plan for a TLS certificate before putting this on a public
domain.

## 4. Using it

**Live Camera tab** — click *Start scanning*. Every N seconds (default 4,
adjustable) it grabs a frame, runs all 3 models, and any candidate Gemini
confirms gets pinned on the map instantly. Watch the *Detection log* on
the left for a live feed of every check (clear / rejected / confirmed /
error).

**Upload Video tab** — for dashcam footage you already have. Since a video
file has no live GPS track, enter a latitude/longitude (or reuse your
current location) and it samples a frame every N seconds and runs the
same pipeline.

## 5. How the pieces fit together

| File | Role |
|---|---|
| `backend/detectors.py` | Calls your 3 Roboflow models, returns the highest-confidence prediction from each |
| `backend/verifier.py` | Sends a candidate frame + label to Gemini, parses back `{confirmed, confidence, reason}` |
| `backend/storage.py` | Append-only JSON file of confirmed pins (`data/pins.json`) — swap for Postgres/PostGIS later without touching `app.py` |
| `backend/app.py` | Flask routes: `/api/analyze` (single frame), `/api/analyze-video` (batch), `/api/pins` (map data) |
| `frontend/` | Vanilla HTML/JS — webcam capture, Leaflet map (OpenStreetMap tiles, no key needed), detection log |

## 6. Tuning

- `DETECTION_CONFIDENCE_THRESHOLD` in `.env` — how confident Roboflow must
  be before a frame is even sent to Gemini (saves API calls/cost).
  Default `0.4`.
- `CAPTURE_INTERVAL_SECONDS` — also adjustable live in the UI.
- The map uses OpenStreetMap tiles, which are free and need no API key —
  so your single Google key stays dedicated to Gemini verification.

## 7. Known limitations to plan around

- This is a prototype: pins are stored in a flat JSON file, fine for
  testing, not for concurrent multi-vehicle production use — move to a
  real database before scaling past one camera.
- Roboflow's free/hosted inference tier has request-per-minute limits;
  the confidence threshold + capture interval exist to stay under them.
- Gemini image calls cost per request — the two-stage design (cheap
  Roboflow filter → Gemini only confirms candidates) keeps that number
  low, but very frequent scanning on a busy road will still add up.
