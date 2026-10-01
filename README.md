# 🚦 CivicScan — AI Road Issue Detection

<p align="center">
  <strong>Detect road hazards. Verify them with AI. Pin them on a live map.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/github/stars/dishantpatil-dev/AI-Road-Encroachment-Detection?style=for-the-badge&logo=github&label=STARS" alt="GitHub stars" />
  <img src="https://img.shields.io/github/forks/dishantpatil-dev/AI-Road-Encroachment-Detection?style=for-the-badge&logo=github&label=FORKS" alt="GitHub forks" />
  <img src="https://img.shields.io/github/last-commit/dishantpatil-dev/AI-Road-Encroachment-Detection?style=for-the-badge&logo=github&label=UPDATED" alt="Last commit" />
  <img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.9+" />
</p>

<p align="center">
  <a href="https://github.com/dishantpatil-dev/AI-Road-Encroachment-Detection">⭐ Star this project</a>
  ·
  <a href="https://github.com/dishantpatil-dev/AI-Road-Encroachment-Detection/issues">🐛 Report an issue</a>
  ·
  <a href="https://github.com/dishantpatil-dev/AI-Road-Encroachment-Detection/issues/new">💡 Request a feature</a>
</p>

---

## 🎯 What is CivicScan?

**CivicScan** is a computer-vision road monitoring prototype that analyzes webcam or dashcam video to detect:

- 🕳️ **Potholes**
- 🗑️ **Garbage areas**
- 🚧 **Road encroachment**

Detected candidates are passed through a second AI verification stage using **Gemini**. Confirmed issues are then stored and displayed as pins on a live map using the current GPS location.

The pipeline is intentionally designed as a **detect → verify → map** workflow so that candidate detections can be filtered before they become reported road issues.

## 👀 Demo

<p align="center">
  <img width="1366" height="768" src="https://github.com/user-attachments/assets/95deb616-a328-44ad-8b5f-a4a56fd651e9" alt="CivicScan live road issue detection interface" />
</p>

> The screenshot above shows the CivicScan interface and live detection workflow. A short screen recording or GIF can be added here later to make the repository easier to evaluate at a glance.

---

## 🧠 How It Works

```text
┌─────────────────────┐
│   Camera / Video    │
└──────────┬──────────┘
           │
           ▼
┌──────────────────────────────┐
│  Roboflow Models × 3         │
│  Pothole • Garbage •         │
│  Encroachment                │
└──────────┬───────────────────┘
           │
           │ Candidate above threshold
           ▼
┌──────────────────────────────┐
│       Gemini Verification    │
│  Confirms / Rejects candidate│
└──────────┬───────────────────┘
           │
           │ Confirmed issue
           ▼
┌──────────────────────────────┐
│       GPS + Live Map         │
│      Confirmed issue pin     │
└──────────────────────────────┘
```

### Why two AI stages?

The first stage finds potential issues. The second stage provides an additional verification step before a candidate is stored as a confirmed issue.

That separation also makes the system easier to tune: the detection threshold and capture interval can be adjusted without changing the verification logic.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎥 Live camera mode | Analyze frames directly from a browser camera |
| 📹 Video mode | Analyze uploaded dashcam/video footage |
| 🤖 Multi-model detection | Runs separate Roboflow models for three road-issue categories |
| 🧠 AI verification | Uses Gemini to verify detection candidates |
| 📍 GPS mapping | Pins confirmed issues using latitude/longitude |
| 🗺️ Live map | Displays confirmed issues with Leaflet + OpenStreetMap |
| 📋 Detection log | Shows clear/rejected/confirmed/error events |
| ⚙️ Tunable pipeline | Adjust confidence threshold and capture interval |
| 🔌 REST API | Backend exposes endpoints for analysis and map data |

---

## 🛠️ Tech Stack

<p align="center">
  <img src="https://skillicons.dev/icons?i=python,flask,html,css,js,opencv,git,github" alt="Technology stack" />
</p>

**AI / Computer Vision**
- Roboflow-hosted detection models
- Gemini image verification
- OpenCV

**Backend**
- Python
- Flask
- REST API

**Frontend**
- HTML
- CSS
- Vanilla JavaScript
- Leaflet
- OpenStreetMap

**Storage**
- JSON-based confirmed-pin storage for the prototype

---

## 📁 Project Architecture

| Path | Responsibility |
|---|---|
| `backend/app.py` | Flask application and API routes |
| `backend/detectors.py` | Calls the three Roboflow models |
| `backend/verifier.py` | Sends candidates to Gemini and parses verification |
| `backend/storage.py` | Stores confirmed map pins |
| `frontend/` | Camera/video UI, map and detection log |
| `data/pins.json` | Prototype storage for confirmed pins |

---

## 🚀 Getting Started

### 1. Requirements

- Python **3.9+**
- Webcam for live scanning, or a video file
- Google Gemini API key
- Three Roboflow API keys/model IDs:
  - Pothole
  - Garbage
  - Encroachment

### 2. Clone

```bash
git clone https://github.com/dishantpatil-dev/AI-Road-Encroachment-Detection.git
cd AI-Road-Encroachment-Detection
```

### 3. Create a virtual environment

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r backend/requirements.txt
```

### 5. Configure environment variables

Create a `.env` file in the project and add your private API credentials:

```ini
GOOGLE_API_KEY=your_google_api_key

ROBOFLOW_POTHOLE_API_KEY=your_api_key
ROBOFLOW_POTHOLE_MODEL=your-project/1

ROBOFLOW_GARBAGE_API_KEY=your_api_key
ROBOFLOW_GARBAGE_MODEL=your-project/1

ROBOFLOW_ENCROACHMENT_API_KEY=your_api_key
ROBOFLOW_ENCROACHMENT_MODEL=your-project/1
```

**Never commit real API keys to GitHub.**

### 6. Start the backend

```bash
cd backend
python app.py
```

Then open:

```text
http://localhost:5000
```

For camera and geolocation access on a deployed site, use **HTTPS**. Browsers generally permit these capabilities on `localhost` during development.

---

## ⚙️ Configuration

| Variable | Purpose | Prototype default |
|---|---|---|
| `DETECTION_CONFIDENCE_THRESHOLD` | Minimum detector confidence before Gemini verification | `0.4` |
| `CAPTURE_INTERVAL_SECONDS` | Time between captured frames | `4` |

Lowering the threshold can increase candidate detections and API usage. Increasing the threshold can reduce unnecessary verification requests.

---

## 🔌 API

The current backend exposes endpoints including:

| Endpoint | Purpose |
|---|---|
| `/api/analyze` | Analyze a single frame |
| `/api/analyze-video` | Analyze uploaded video frames |
| `/api/pins` | Retrieve confirmed map pins |

---

## 🧪 Example Workflow

1. Open CivicScan.
2. Allow camera and location permissions.
3. Start scanning.
4. A frame is captured at the configured interval.
5. The three detection models check for road issues.
6. Candidates above the configured threshold are sent to Gemini.
7. Confirmed issues are added to the map.
8. The detection log records the result.

---

## ⚠️ Current Limitations

CivicScan is currently a **prototype**, not a production traffic-monitoring platform.

- Confirmed pins use flat JSON storage.
- Hosted Roboflow inference can have request/rate limits.
- Gemini verification adds API cost.
- Video files do not contain a live GPS track, so coordinates must be supplied/reused.
- A production deployment would benefit from a database such as PostgreSQL/PostGIS.
- Authentication, multi-user permissions and production observability would need to be added before public-scale deployment.

---

## 🗺️ Roadmap

- [ ] PostgreSQL/PostGIS storage
- [ ] Authentication and user accounts
- [ ] Historical incident dashboard
- [ ] Better issue filtering and severity classification
- [ ] Production deployment
- [ ] Automated tests
- [ ] CI/CD pipeline
- [ ] Performance benchmarking
- [ ] Short demo video / GIF
- [ ] Public API documentation

---

## 🤝 Contributing

Ideas, bug reports and improvements are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Make your changes.
4. Test locally.
5. Open a pull request with a clear description.

For bugs or feature ideas, use the repository's **Issues** tab.

---

## ⭐ Support the Project

If CivicScan is useful, interesting, or helps you learn about computer vision, **consider giving the repository a star**.

It helps the project become more discoverable and gives useful feedback about community interest.

<p align="center">
  <a href="https://github.com/dishantpatil-dev/AI-Road-Encroachment-Detection">
    <img src="https://img.shields.io/badge/⭐_Star_CivicScan-on_GitHub-181717?style=for-the-badge&logo=github" alt="Star CivicScan on GitHub" />
  </a>
</p>

---

<p align="center">
  <strong>Built with Python • Computer Vision • AI • Maps</strong>
</p>
