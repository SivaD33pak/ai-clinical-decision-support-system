"""
End-to-End System Integration Test Suite
Phase 06 - System Integration Engineering Specification

Tests the entire unified flow:
1. Auth & Session Management (FastAPI + Supabase)
2. Chest X-Ray Image Upload & Cloud Storage (FastAPI + Supabase Storage Bucket)
3. AI Inference & Explainability (FastAPI + DenseNet121 + Grad-CAM)
4. Cloud Database Persistence (FastAPI + Supabase PostgreSQL)
5. Patient History Query & Inspection (FastAPI + Supabase DB)
6. Response Envelope Contract Verification (Flutter App BLoC Compatibility)
"""

import os
import sys
import io

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image
from fastapi.testclient import TestClient

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from app.main import app

client = TestClient(app)

def create_dummy_chest_xray():
    img = Image.new("RGB", (224, 224), color=(30, 30, 30))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()

def run_system_integration_test():
    print("================================================================")
    print("  AI-CDSS Phase 06: End-to-End System Integration Test")
    print("================================================================")

    # 1. Doctor Authentication Contract
    print("\n[Step 1] Authenticating Clinician...")
    login_resp = client.post("/api/v1/auth/login", json={
        "email": "doctor@hospital.org",
        "password": "securepassword123"
    })
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    login_data = login_resp.json()
    assert login_data["success"] is True
    user_id = login_data["data"]["user"]["id"]
    print(f"  -> Clinician Authenticated: ID={user_id}, Name={login_data['data']['user']['name']}")

    # 2. Chest X-Ray Upload Contract
    print("\n[Step 2] Uploading Patient Chest X-Ray...")
    image_bytes = create_dummy_chest_xray()
    files = {"file": ("patient_scan_001.png", image_bytes, "image/png")}
    upload_resp = client.post("/api/v1/prediction/upload", files=files)
    assert upload_resp.status_code == 201, f"Upload failed: {upload_resp.text}"
    upload_data = upload_resp.json()
    upload_id = upload_data["data"]["upload_id"]
    public_url = upload_data["data"]["public_url"]
    print(f"  -> Upload Successful: ID={upload_id}")
    print(f"  -> Public Cloud URL: {public_url}")

    # 3. AI Inference & Explainability Contract
    print("\n[Step 3] Executing AI Model Prediction & Grad-CAM Heatmap...")
    predict_payload = {
        "upload_id": upload_id,
        "user_id": user_id,
        "module": "XRAY"
    }
    predict_resp = client.post("/api/v1/prediction", json=predict_payload)
    assert predict_resp.status_code == 200, f"Prediction failed: {predict_resp.text}"
    pred_data = predict_resp.json()["data"]
    prediction_id = pred_data["prediction_id"]
    disease = pred_data["disease"]
    confidence_str = pred_data["confidence_formatted"]
    model_name = pred_data["model"]
    disclaimer = pred_data["disclaimer"]
    breakdown = pred_data["predictions_breakdown"]
    heatmap_url = pred_data["heatmap_url"]

    print(f"  -> Prediction ID: {prediction_id}")
    print(f"  -> Primary Diagnosis: {disease}")
    print(f"  -> Confidence: {confidence_str}")
    print(f"  -> Model: {model_name}")
    print(f"  -> Grad-CAM Heatmap: {heatmap_url}")
    print(f"  -> Breakdown: {breakdown}")
    print(f"  -> Disclaimer: {disclaimer}")

    assert disease in ["Normal", "Pneumonia", "Tuberculosis"]
    assert len(breakdown) == 3
    assert disclaimer.startswith("⚠️")

    # 4. Cloud Database & History Verification Contract
    print("\n[Step 4] Querying Patient Prediction History from Supabase...")
    history_resp = client.get(f"/api/v1/history?user_id={user_id}")
    assert history_resp.status_code == 200, f"History query failed: {history_resp.text}"
    history_data = history_resp.json()["data"]
    items = history_data["items"]
    print(f"  -> Found {len(items)} historical scan records for clinician.")
    assert len(items) >= 1

    # 5. History Record Lookup
    print("\n[Step 5] Inspecting Specific Scan Details by ID...")
    detail_resp = client.get(f"/api/v1/history/{prediction_id}")
    assert detail_resp.status_code == 200, f"Detail lookup failed: {detail_resp.text}"
    detail_data = detail_resp.json()["data"]
    assert detail_data["id"] == prediction_id
    assert detail_data["disease"] == disease
    print(f"  -> Record verified with full clinical integrity: {detail_data['id']}")

    print("\n================================================================")
    print("  [SUCCESS] PHASE 06 SYSTEM INTEGRATION VERIFIED 100%!")
    print("================================================================")

if __name__ == "__main__":
    run_system_integration_test()
