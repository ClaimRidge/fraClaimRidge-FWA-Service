# ClaimRidge Fraud Waste & Abuse (FWA) Service

![Fraud Intelligence Dashboard](https://img.shields.io/badge/Architecture-Clean/Hexagonal-blue)
![Python Version](https://img.shields.io/badge/Python-3.12-green)
![ML Stack](https://img.shields.io/badge/ML-XGBoost%20|%20NetworkX-orange)

The **ClaimRidge FWA Service** is a production-grade microservice designed to detect insurance fraud in real-time using a unique 4-layer ML pipeline. It integrates seamlessly into the ClaimRidge platform to protect financial assets through automated case management and deep behavioral analysis.

## 🛡️ The 4-Layer Detection Pipeline

1.  **Layer 1 (Anomaly Detection)**: Real-time XGBoost scoring of every incoming claim against historical outliers.
2.  **Layer 2 (Behavioral Drift)**: Redis-backed PSI analysis to detect "behavioral mutations" in provider billing habits over 30-day windows.
3.  **Layer 3 (Graph Collusion)**: NetworkX-powered bipartite graph analysis to discover "Collusion Rings" and high-centrality "Hub Providers."
4.  **Layer 4 (Slow-Burn Detection)**: Time-series trend analysis to catch incremental billing inflation that bypasses real-time filters.

## 🚀 Getting Started

### 1. Prerequisites
*   Python 3.12+
*   PostgreSQL (Supabase supported)
*   Redis (For Layer 2 fingerprints)

### 2. Installation
```bash
pip install -r requirements.txt
```

### 3. Database Setup
Configure your `DATABASE_URL` in `.env` and run migrations:
```bash
alembic upgrade head
```

### 4. Training the Models
Populate the system with baseline patterns using the provided training scripts:
```bash
# Train L1 Anomaly Model
python scripts/train_layer1.py

# Generate L2 Provider Fingerprints
python scripts/baseline_providers.py

# Run L3 Graph Discovery
python scripts/analyze_graph.py
```

### 5. Running the Service
```bash
python -m uvicorn src.main:app --reload
```
Visit `http://localhost:8000/dashboard` to access the **Fraud Intelligence Scanner**.

## 🖥️ Architecture
The service follows **Clean Architecture** principles:
*   `src/api`: FastAPI routers and endpoints.
*   `src/layerX`: Modular detection engines.
*   `src/repositories`: Data access layer with multi-tenant enforcement.
*   `src/models`: SQLAlchemy ORM models.

## 🤝 Contributing
1.  Fork the Repository to the `ClaimRidge` organization.
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the Branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

---
© 2026 ClaimRidge Engineering. All rights reserved.
