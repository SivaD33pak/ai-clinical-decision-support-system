import os
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from fastapi.testclient import TestClient

# Ensure backend root is in sys.path
backend_root = Path(__file__).parent.parent
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

from app.main import app

client = TestClient(app)

def run_tests():
    print("--- 1. Testing Root Endpoint GET / ---")
    r = client.get("/")
    print("Status:", r.status_code, "Body:", r.json())
    assert r.status_code == 200

    print("\n--- 2. Testing API v1 Health GET /api/v1/health ---")
    r = client.get("/api/v1/health")
    print("Status:", r.status_code, "Body:", r.json())
    assert r.status_code == 200

    print("\n--- 3. Testing Auth Login POST /api/v1/auth/login ---")
    r = client.post("/api/v1/auth/login", json={"email": "doctor@hospital.org", "password": "securepassword123"})
    print("Status:", r.status_code, "Body:", r.json())
    assert r.status_code == 200

    print("\n--- 4. Testing Auth Register POST /api/v1/auth/register ---")
    r = client.post("/api/v1/auth/register", json={"email": "newdoctor@hospital.org", "password": "securepassword123", "name": "Dr. Siva"})
    print("Status:", r.status_code, "Body:", r.json())
    assert r.status_code == 201

    print("\n--- 5. Testing Image Upload POST /api/v1/prediction/upload ---")
    import io
    from PIL import Image
    buf = io.BytesIO()
    Image.new("RGB", (224, 224), color=(128, 128, 128)).save(buf, format="PNG")
    sample_img = buf.getvalue()
    r = client.post("/api/v1/prediction/upload", files={"file": ("sample_chest_xray.png", sample_img, "image/png")})
    print("Status:", r.status_code, "Body:", r.json())
    assert r.status_code == 201
    upload_id = r.json()["data"]["upload_id"]

    print("\n--- 6. Testing Disease Prediction POST /api/v1/prediction ---")
    r = client.post("/api/v1/prediction", json={"upload_id": upload_id, "user_id": "user_default_001", "module": "XRAY"})
    print("Status:", r.status_code, "Body:", r.json())
    assert r.status_code == 200

    print("\n--- 7. Testing Prediction History List GET /api/v1/history ---")
    r = client.get("/api/v1/history?user_id=user_default_001")
    print("Status:", r.status_code, "Body:", r.json())
    assert r.status_code == 200

    print("\n--- 8. Testing History Detail GET /api/v1/history/pred_demo_001 ---")
    r = client.get("/api/v1/history/pred_demo_001")
    print("Status:", r.status_code, "Body:", r.json())
    assert r.status_code == 200

    print("\n[SUCCESS] ALL ENDPOINT INTEGRATION TESTS PASSED CLEANLY!")

if __name__ == "__main__":
    run_tests()
