# WatchTheBlue

---

## The Problem

Every year, thousands of whales, dolphins, sea turtles, and sharks strand on Indian coastlines. By the time NGOs are alerted, the animal is already severely stressed or dead. Ocean conditions — temperature, oxygen, salinity, pH — deteriorate days before a stranding occurs. The satellite data exists. No platform translates it into species-level risk that field teams can act on.

**WatchTheBlue fills that gap.**

---

## What It Does

- 🛰️ **Pulls live ocean data** from Copernicus Marine (CMEMS) every 6 hours across 4 Indian Ocean zones
- 🤖 **Predicts stranding risk** per species using a RandomForest ML model trained on 10 years of OBIS stranding records
- 🔁 **Backward drift simulation** — traces where a stranded animal originated using 72-hour Euler integration on CMEMS current vectors
- 🗺️ **Interactive map** with color-coded stress zones across the Indian Ocean
- 🤝 **NGO dashboard** for 6 partner organizations covering India's 7,500 km coastline

---

## Demo

| Page | Description |
|------|-------------|
| **Home** | Mission stats, how it works (7-step pipeline) |
| **Ocean Zones** | Live stress levels for 4 zones |
| **Species** | Threat level bars for 10 species |
| **Live Monitor** | Real-time zone dashboard |
| **View Map** | Interactive Leaflet map with drift simulation |
| **Join** | NGO Partner + Citizen Scientist registration |

---

## ML Model

| Metric | Value |
|--------|-------|
| Algorithm | RandomForest Classifier |
| Training samples | 1,995 |
| Species tracked | 10 |
| Overall accuracy | **90.04%** |
| Macro F1 | **0.87** |
| Spinner Dolphin precision | 1.00 |
| Whale Shark precision | 1.00 |

---

## Backward Drift Simulation

Uses CMEMS hourly current vector fields (eastward `uo`, northward `vo`) to run Euler backward integration from a stranding coordinate over 72 hours. Outputs:
- Probable origin zone
- 72-point drift path
- Uncertainty cone (8 offset paths)

Helps NGOs identify the actual stress zone, not just where the carcass appeared — a workflow that previously required specialist software and hours of manual work.

---

## Ocean Zones Covered

| Zone | Coordinates | Key Species | NGO Partner |
|------|-------------|-------------|-------------|
| Bay of Bengal | 10°N–20°N, 80°E–90°E | Olive Ridley, Humpback Whale | TREE Foundation |
| Arabian Sea | 10°N–23°N, 68°E–77°E | Whale Shark, Spinner Dolphin | Wildlife Trust of India |
| Lakshadweep Sea | 8°N–12°N, 72°E–74°E | Reef Shark, Manta Ray | Coastal Impact |
| Andaman Sea | 10°N–14°N, 92°E–98°E | Dugong, Green Sea Turtle | ReefWatch |

---

## Species Monitored

Olive Ridley Turtle · Whale Shark · Spinner Dolphin · Humpback Whale · Dugong · Manta Ray · Reef Shark · Clownfish · Blue Whale · Green Sea Turtle

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, Tailwind CSS, Leaflet.js |
| Backend | Python 3.11, FastAPI, Uvicorn |
| ML | RandomForest (scikit-learn), SHAP |
| Data | CMEMS API, OBIS API, NOAA CoralTemp |
| Map | Leaflet.js, React-Leaflet |
| Charts | Recharts |

---

## Impact

- Reduces NGO response time from **8–16 hours** to **30 minutes–2 hours**
- Shifts field teams from **reactive** to **predictive** deployment
- Provides evidence-based data for **Marine Protected Area** policy proposals
- Democratizes drift origin analysis — previously required specialist software

---

