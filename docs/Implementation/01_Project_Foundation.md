# Phase 1 — Project Foundation & Environment Setup

> **Project:** AI Clinical Decision Support System (AI-CDSS)
>
> **Version:** 1.0
>
> **Estimated Time:** 1–2 Days
>
> **Status:** ⬜ Not Started

---

# 🎯 Objective

The objective of this phase is to establish a solid foundation for the entire project.

By the end of this phase you should have:

- Complete project structure
- GitHub repository
- Flutter application initialized
- FastAPI backend initialized
- Python virtual environment
- Supabase project
- Development environment configured
- Initial documentation

> **Important**
>
> No AI development happens during this phase.

---

# 🏗 Final Architecture Overview

```
Flutter
      │
      ▼
FastAPI Backend
      │
      ▼
AI Engine (Future)
      │
      ▼
Supabase
```

This phase only builds the highlighted components:

✅ Flutter

✅ FastAPI

✅ Supabase

---

# 📂 Step 1 — Create GitHub Repository

## Repository Name

```
ai-clinical-decision-support-system
```

### Repository Description

```
AI-powered Clinical Decision Support System for Chest X-ray Disease Detection using Flutter, FastAPI, PyTorch and Supabase.
```

---

## Repository Settings

Enable

- Public (recommended for portfolio)
- README
- MIT License
- Python .gitignore

---

## Initial Branch

```
main
```

---

## Clone Repository

```
git clone <repository-url>
```

---

# 📂 Step 2 — Create Project Structure

Inside the repository create:

```
AI-Clinical-CDSS/

│

├── frontend/

├── backend/

├── ai/

├── datasets/

├── docs/

├── scripts/

├── assets/

└── README.md
```

---

## Folder Explanation

### frontend/

Flutter application.

---

### backend/

FastAPI application.

---

### ai/

Contains every AI-related module.

```
ai/

xray/

blood/

symptoms/

models/

training/

utils/

```

Although only X-ray is implemented now, create the future folders now.

---

### datasets/

Stores datasets only.

Never mix datasets with source code.

---

### docs/

Contains:

- Architecture
- SRS
- Literature Survey
- API Documentation
- Report
- Presentation

---

### scripts/

Contains helper scripts.

Examples

- Dataset cleaner
- Model converter
- Data downloader

---

### assets/

Stores

- Logos
- Icons
- Images
- UI Assets

---

# 📱 Step 3 — Initialize Flutter

Navigate

```
frontend/
```

Create Flutter application.

Since this project follows the VGV architecture, initialize it using your preferred VGV project structure.

---

## Configure

- Material 3
- Riverpod
- GoRouter
- Theme
- Lints

---

## Initial Features

Create empty features

```
authentication

dashboard

prediction

history

profile
```

No implementation is required.

---

# 🐍 Step 4 — Initialize Backend

Navigate

```
backend/
```

---

## Create Virtual Environment

Windows

```
python -m venv venv
```

Activate

```
venv\Scripts\activate
```

---

## Install Packages

```
fastapi

uvicorn

python-dotenv

python-multipart

pillow

supabase

pydantic

httpx
```

Later phases will add AI packages.

---

## Save Dependencies

```
pip freeze > requirements.txt
```

---

# 📂 Step 5 — Backend Structure

Create

```
backend/

app/

│

├── api/

├── core/

├── database/

├── services/

├── schemas/

├── models/

├── utils/

├── ai/

└── main.py
```

No code yet.

Only structure.

---

# ☁ Step 6 — Create Supabase Project

Create project.

Suggested name

```
clinical-cdss
```

Save

- URL
- API Key
- Database Password

---

## Create Storage Buckets

```
xray-images
```

Later

```
heatmaps
```

---

## Create Database Tables

Create

### users

| Column | Type |
|---------|------|
| id | uuid |
| email | text |
| name | text |

---

### predictions

| Column | Type |
|---------|------|
| id | uuid |
| user_id | uuid |
| module | text |
| disease | text |
| confidence | numeric |
| image_url | text |
| heatmap_url | text |
| created_at | timestamp |

The **module** field is future-proof.

Possible values

```
XRAY

BLOOD

SYMPTOMS
```

---

# ⚙ Step 7 — Environment Variables

Create

```
.env
```

Never commit this file.

Add

```
SUPABASE_URL=

SUPABASE_KEY=

MODEL_PATH=

SECRET_KEY=

API_VERSION=v1
```

---

Create

```
.env.example
```

without actual secrets.

---

# 📝 Step 8 — Documentation

Update README.

Include

- Project overview
- Objectives
- Folder structure
- Architecture
- Tech stack
- Future roadmap

---

# 🔧 Step 9 — Verify Everything

Check

Flutter

```
flutter doctor
```

Python

```
python --version
```

Git

```
git --version
```

FastAPI

```
uvicorn --version
```

Everything should work before proceeding.

---

# 📦 Step 10 — First Commit

```
git add .
```

```
git commit -m "Initial project setup"
```

```
git push
```

---

# 📋 Deliverables

At the end of this phase you should have

- GitHub Repository
- Flutter Project
- FastAPI Project
- Supabase Project
- Virtual Environment
- Folder Structure
- README
- requirements.txt
- Environment Variables
- Initial Commit

---

# ✅ Checklist

- [ ] GitHub Repository Created
- [ ] Repository Cloned
- [ ] Folder Structure Created
- [ ] Flutter Initialized
- [ ] FastAPI Initialized
- [ ] Virtual Environment Created
- [ ] Python Packages Installed
- [ ] Supabase Created
- [ ] Storage Bucket Created
- [ ] Database Tables Created
- [ ] Environment Variables Configured
- [ ] README Created
- [ ] First Commit Pushed

---

# 🚀 Milestone

At the end of Phase 1:

```
Project Foundation Complete
```

The repository should look professional, every required service should be configured, and the project should be ready for backend development.

No AI functionality is expected yet.

---

# 📖 Best Practices

- Keep commits small and meaningful.
- Never commit `.env` or secrets.
- Maintain a clean folder structure.
- Follow consistent naming conventions.
- Build with future scalability in mind.
- Test every setup step before moving to the next phase.

---

# ➡ Next Phase

**Phase 2 — Backend Foundation**

In the next phase you will:

- Build the FastAPI architecture
- Implement API versioning
- Configure logging
- Implement exception handling
- Create service and router layers
- Build the first REST API endpoints