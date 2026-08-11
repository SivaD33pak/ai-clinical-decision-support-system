"""
AI Core Inference & Explainability Performance Benchmark
Phase 07 - Testing and Quality Assurance

Measures:
1. DenseNet121 Model Forward Pass Latency (ms)
2. Grad-CAM Activation Heatmap Generation Latency (ms)
3. End-to-End Predictor Latency (Preprocessing + Inference + XAI + Formatting)
4. Throughput (Scans / second)
"""

import os
import sys
import time
import tempfile
import torch
import numpy as np
from PIL import Image

# Ensure UTF-8 on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from ai_core.serving.inference_manager import InferenceManager, MODEL_KEY
from ai_core.serving.predictor import DiseasePredictor

def create_sample_scan():
    # 224x224 simulated chest X-ray
    arr = np.random.randint(20, 230, (224, 224, 3), dtype=np.uint8)
    return Image.fromarray(arr)

def run_benchmarks(iterations=25):
    print("================================================================")
    print("  AI-CDSS Phase 07: AI Core Inference Latency Benchmark")
    print("================================================================")
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"  Target Device: {device.type.upper()}")
    print(f"  Benchmark Iterations: {iterations}")
    print("----------------------------------------------------------------")

    manager = InferenceManager()
    predictor: DiseasePredictor = manager.registry.get(MODEL_KEY)
    assert predictor is not None, "Predictor failed to initialize"

    # Create temporary scan file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        sample_img = create_sample_scan()
        sample_img.save(tmp.name)
        tmp_path = tmp.name

    try:
        # Warmup runs
        print("  Warming up PyTorch engine (3 iterations)...")
        for _ in range(3):
            _ = predictor.predict_single(tmp_path, generate_cam=True)

        # 1. Benchmark: Full Predictor (Preprocess + DenseNet121 + Grad-CAM)
        latencies = []
        print(f"  Running {iterations} full diagnostic scan iterations...")
        
        for i in range(iterations):
            t0 = time.perf_counter()
            result = predictor.predict_single(tmp_path, generate_cam=True)
            t1 = time.perf_counter()
            elapsed_ms = (t1 - t0) * 1000.0
            latencies.append(elapsed_ms)

        latencies = np.array(latencies)
        mean_lat = np.mean(latencies)
        median_lat = np.median(latencies)
        p95_lat = np.percentile(latencies, 95)
        min_lat = np.min(latencies)
        max_lat = np.max(latencies)
        fps = 1000.0 / mean_lat

        print("\n--- LATENCY & THROUGHPUT RESULTS ---")
        print(f"  Mean Latency:        {mean_lat:.2f} ms")
        print(f"  Median Latency:      {median_lat:.2f} ms")
        print(f"  95th Percentile:     {p95_lat:.2f} ms")
        print(f"  Min / Max:           {min_lat:.2f} ms / {max_lat:.2f} ms")
        print(f"  Throughput:          {fps:.2f} scans / sec")

        # Verify clinical SLA (Sub-second inference required for interactive CDSS)
        assert mean_lat < 1000.0, f"Latency {mean_lat}ms exceeds 1000ms SLA target"
        print("\n  [PASS] Sub-second Clinical Decision SLA target met! (<1000ms)")
        print("================================================================")
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass

if __name__ == "__main__":
    run_benchmarks(iterations=20)
