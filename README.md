# 🩺 AI Clinical Decision Support System (AI-CDSS)

> **Version:** 1.0.0 (MVP Foundation Complete)  
> **Project Type:** B.Tech Final Year Project  
> **Status:** 🚧 In Active Development (Phase 1 Completed)

An AI-powered Clinical Decision Support System (CDSS) that assists healthcare professionals by analyzing **Chest X-ray images** and providing disease predictions with confidence scores and explainable AI visualizations (Grad-CAM).

The system is engineered with a **modular, scalable architecture**, laying the foundation for future expansion into Blood Report Analysis, Symptom Analysis, ECG Analysis, and Multimodal Clinical Decision Support.

---

# 📌 Project Objectives

* Detect respiratory diseases from Chest X-ray images using Deep Learning (DenseNet121).
* Provide AI-assisted clinical decision support with confidence scoring.
* Visualize model attention maps using Grad-CAM.
* Store prediction history securely with user access controls.
* Build a scalable, production-ready architecture for future multimodal AI modules.
* Deliver a modern, responsive cross-platform mobile & desktop application using Flutter.

---

# 🚀 Current Implementation Scope (Phase 1 Foundation)

* [x] **Project Structure:** Standardized modular layout across frontend, backend, AI modules, and documentation.
* [x] **Backend Infrastructure:** FastAPI application setup with virtual environment, CORS middleware, health check endpoint, and dependency management.
* [x] **Frontend Setup:** Flutter application initialized using Very Good Ventures (VGV) architecture with empty feature modules.
* [x] **Database Schema:** Supabase PostgreSQL DDL scripts (`users` and `predictions` tables) and storage bucket configurations (`xray-images`).
* [x] **Environment Configuration:** Secure `.env` and `.env.example` templates.
* [ ] **AI Model Inference:** DenseNet121 model loading & inference engine *(Phase 2/3)*.
* [ ] **Grad-CAM Visualization:** Heatmap overlay generation *(Phase 3)*.

---

# 🔮 Future Roadmap

### Version 2.0
* Blood Report Analysis & Laboratory Parameter Classification.

### Version 3.0
* Symptom Analysis & Clinical Questionnaire Support.

### Version 4.0
* Multimodal AI integration combining Chest X-rays, Blood Reports, and Symptoms into unified predictions.

### Future Enhancements
* ECG Analysis & CT Scan Support
* Doctor & Patient Interactive Dashboards
* Automated PDF Clinical Report Generation

---

# 🏗️ System Architecture

```text
                     Flutter Application (ai_clinical_cdss_app)
                               │
                               ▼
                        FastAPI Backend (backend/app)
                               │
                               ▼
                   AI Inference Manager (backend/app/ai)
                               │
        ┌─────────────────────┼────────────────────┐
        │                     │                    │
        ▼                     ▼                    ▼
  Chest X-ray Module      Blood Module*      Symptoms Module*
        │
        ▼
     DenseNet121
        │
        ▼
      Grad-CAM
        │
        ▼
 Clinical Prediction Report ────► Supabase Database & Storage
```

> ***** Planned for future versions.

---

# 🛠 Technology Stack

## Frontend
* **Framework:** Flutter (Dart 3.x)
* **Architecture:** Very Good Ventures (VGV) feature-first pattern
* **UI & State:** Material 3, Riverpod / BLoC, GoRouter

## Backend
* **Language:** Python 3.13
* **Framework:** FastAPI
* **Server:** Uvicorn
* **HTTP Client & Utils:** Pydantic v2, HTTPX, Pillow, python-dotenv

## Artificial Intelligence
* **Framework:** PyTorch, TorchVision
* **Model:** DenseNet121
* **Explainability:** Grad-CAM
* **Data Processing:** NumPy, OpenCV, Pandas, Scikit-Learn

## Backend Cloud Services
* **Database:** Supabase PostgreSQL
* **Authentication:** Supabase Auth
* **Storage:** Supabase Storage (`xray-images`)

---

# 📂 Project Structure

```text
AI-Clinical-CDSS/
├── backend/                   # FastAPI Backend & AI Core Domain Service
│   ├── app/                   # FastAPI Application (Vertical Feature Slices)
│   │   ├── core/              # Settings, Logging, Exception Handlers, Responses
│   │   ├── database/          # Supabase Client & Database Setup
│   │   ├── dependencies/      # Dependency Injection Providers
│   │   ├── features/          # Feature Modules (auth, prediction, history)
│   │   ├── middleware/        # Request Timing & Logger Middleware
│   │   └── main.py            # FastAPI Entrypoint & Health Check
│   │
│   ├── ai_core/               # Machine Learning & AI Core Domain
│   │   ├── training/          # Model Training Engine (datasets, trainers, experiments, checkpoints)
│   │   ├── serving/           # API Serving Engine (inference_manager, predictor, preprocessing, explainability)
│   │   ├── models/            # Deep Learning Model Architectures (DenseNet121) & Registry
│   │   └── evaluation/        # Clinical Metrics (AUC/ROC, Sensitivity), Evaluator, Confusion Matrix
│   │
│   ├── tests/                 # Integration & Unit Test Suite
│   │   └── test_endpoints.py
│   │
│   ├── database/
│   │   └── schema.sql         # Supabase PostgreSQL DDL Script
│   ├── venv/                  # Python Virtual Environment
│   ├── .env                   # Environment Variables
│   ├── .env.example           # Environment Template
│   └── requirements.txt       # Python Dependencies
│
├── frontend/                  # Flutter Application (Cross-Platform Mobile/Desktop)
│   ├── lib/
│   │   ├── app/
│   │   └── features/          # Modular Feature Folders (auth, dashboard, prediction, history, profile)
│   └── pubspec.yaml
│
├── data/                      # Dataset & Model Artifact Storage
│   ├── raw/
│   │   └── chest_xray/        # Raw Chest X-ray Images
│   ├── processed/             # Preprocessed Datasets
│   └── models/                # Trained PyTorch Weights (.pth)
│
├── docs/                      # Architecture & Implementation Guides
├── .agents/                   # Workspace AI Agent Customizations & Rules
├── scripts/                   # Helper Scripts
├── assets/                    # Project Media Assets
├── .gitignore
└── README.md
```

---

# ⚡ Getting Started & Running Locally

### 1. Prerequisites
* Python 3.10+
* Flutter SDK (3.x+)
* Git

### 2. Backend Setup & Local Server Execution
```powershell
# Navigate to backend directory
cd backend

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Run FastAPI development server with auto-reload
python -m uvicorn app.main:app --reload
```
* **API Documentation (Swagger UI):** `http://127.0.0.1:8000/docs`
* **Health Check Endpoint:** `http://127.0.0.1:8000/health`

### 3. Database & Supabase Setup
1. Create a project at [Supabase](https://supabase.com/).
2. Run the DDL script in `backend/database/schema.sql` inside the Supabase SQL Editor to create the `users` and `predictions` tables.
3. Create a public/private storage bucket named `xray-images`.
4. Copy your Supabase URL and anon key into `backend/.env`.

### 4. Flutter Frontend Setup
```powershell
# Navigate to Flutter app directory
cd frontend

# Get dependencies
flutter pub get

# Run application locally
flutter run
```

---

# 📡 API Endpoints Overview

| Method | Endpoint | Description | Status |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Root API greeting & server info | ✅ Implemented |
| `GET` | `/health` | Service health status check | ✅ Implemented |
| `POST` | `/api/v1/auth/login` | User login endpoint | 🚧 Planned |
| `POST` | `/api/v1/auth/register` | User registration endpoint | 🚧 Planned |
| `POST` | `/api/v1/xray/predict` | Chest X-ray upload & AI inference | 🚧 Planned |
| `GET` | `/api/v1/history` | User prediction history list | 🚧 Planned |
| `GET` | `/api/v1/history/{id}` | Prediction detail & Grad-CAM retrieval | 🚧 Planned |

---

# 📊 Database Overview

### Users Table (`users`)
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | Primary Key | Unique user identifier |
| `email` | `Text` | Unique, Not Null | User email address |
| `name` | `Text` | Not Null | User full name |
| `created_at` | `Timestamp` | Default Now | Account creation timestamp |

### Predictions Table (`predictions`)
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | Primary Key | Unique prediction identifier |
| `user_id` | `UUID` | Foreign Key (`users.id`) | Owner of prediction record |
| `module` | `Text` | Check (`XRAY`,`BLOOD`,`SYMPTOMS`) | AI module tag |
| `disease` | `Text` | Not Null | Predicted disease label |
| `confidence` | `Numeric(5,4)` | Not Null | Confidence score (0.0 - 1.0) |
| `image_url` | `Text` | | Supabase storage image link |
| `heatmap_url` | `Text` | | Supabase storage Grad-CAM link |
| `created_at` | `Timestamp` | Default Now | Record creation timestamp |

---

# 📅 Development Roadmap

## Phase 1 — Project Foundation & Environment Setup (Completed ✅)
* [x] Folder Structure & Repository Setup
* [x] Backend Initialization (FastAPI & Virtual Environment)
* [x] Flutter Initialization (VGV Architecture & Feature Placeholders)
* [x] Supabase Database Schema & Storage Configuration
* [x] Project Documentation & Environment Verification

## Phase 2 — Backend Foundation Architecture & REST APIs (Completed ✅)
* [x] Core Configuration, Pydantic Settings & Logging Setup
* [x] Global Exception Handlers & Standardized API Response Envelopes
* [x] Vertical Slice Feature Modules (`auth`, `prediction`, `history`)
* [x] Supabase Client Integration & Graceful Local Fallback Mode
* [x] AI Layer Abstraction (`InferenceManager` & `ModelRegistry`)
* [x] REST API Endpoints (`/health`, `/upload`, `/prediction`, `/history`, `/auth`)
* [x] Endpoint Integration Test Suite (`test_endpoints.py`)

## Phase 3 — Dataset Preparation & AI Model Training
* [ ] Dataset Acquisition & Preprocessing
* [ ] PyTorch DenseNet121 Model Architecture Setup
* [ ] Training Pipeline & Metric Evaluation (AUC/ROC, Accuracy)

## Phase 4 — AI Inference & Explainability Engine
* [ ] Model Loading & Preprocessing Utilities
* [ ] Grad-CAM Heatmap Generation Engine

## Phase 5 — Flutter Application Integration
* [ ] UI Screens (Upload, Result Screen with Heatmap, History)
* [ ] API Client & State Management Integration

## Phase 6 — Polish, Testing & Final Documentation
* [ ] Full End-to-End System Testing
* [ ] Final Project Report & Presentation

---

# 👨‍💻 Author

**Siva Deepak**  
B.Tech Artificial Intelligence & Machine Learning  
Final Year Major Project

---

# 📄 License

This project is licensed under the MIT License.
