"""
Master Unified Test Orchestrator
Phase 07 - Testing and Quality Assurance

Runs:
1. AI Pipeline Tests (test_ai_pipeline.py)
2. FastAPI Endpoint Tests (test_endpoints.py)
3. End-to-End System Integration Tests (test_end_to_end_system.py)
4. AI Inference Latency Benchmark (benchmark_inference.py)
5. Flutter Static Analysis & Widget Tests (flutter analyze & flutter test)
"""

import os
import sys
import subprocess
import time

# Ensure UTF-8 on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")
PYTHON_EXE = sys.executable
if not os.path.exists(PYTHON_EXE) or "backend" not in PYTHON_EXE:
    for candidate in ["env", "venv"]:
        cand_path = os.path.join(BACKEND_DIR, candidate, "Scripts", "python.exe")
        if os.path.exists(cand_path):
            PYTHON_EXE = cand_path
            break

def run_step(title, cmd, cwd):
    print(f"\n================================================================")
    print(f"  RUNNING: {title}")
    print(f"  Command: {' '.join(cmd)}")
    print(f"  Directory: {cwd}")
    print(f"================================================================")
    t0 = time.perf_counter()
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        shell=(sys.platform == "win32")
    )
    t1 = time.perf_counter()
    elapsed = t1 - t0

    if result.stdout:
        print(result.stdout.strip())
    if result.stderr and result.returncode != 0:
        print("STDERR:")
        print(result.stderr.strip())

    if result.returncode == 0:
        print(f"\n  [PASS] {title} completed successfully in {elapsed:.2f}s")
        return True
    else:
        print(f"\n  [FAIL] {title} failed with exit code {result.returncode}")
        return False

def main():
    print("################################################################")
    print("   AI CLINICAL DECISION SUPPORT SYSTEM (AI-CDSS)")
    print("   MASTER QUALITY ASSURANCE & TEST SUITE RUNNER")
    print("################################################################")

    results = {}

    # 1. AI Pipeline Tests
    results["AI Core & Grad-CAM Pipeline"] = run_step(
        "AI Core Pipeline Tests",
        [PYTHON_EXE, "tests/test_ai_pipeline.py"],
        cwd=BACKEND_DIR
    )

    # 2. FastAPI Endpoint Tests
    results["FastAPI Endpoint Integration"] = run_step(
        "FastAPI Endpoint Tests",
        [PYTHON_EXE, "tests/test_endpoints.py"],
        cwd=BACKEND_DIR
    )

    # 3. End-to-End System Tests
    results["End-to-End System Integration"] = run_step(
        "End-to-End Integration Tests",
        [PYTHON_EXE, "tests/test_end_to_end_system.py"],
        cwd=BACKEND_DIR
    )

    # 4. Latency Benchmark
    results["AI Inference Latency Benchmark"] = run_step(
        "AI Inference Latency Benchmark",
        [PYTHON_EXE, os.path.join(ROOT_DIR, "scripts", "benchmark_inference.py")],
        cwd=ROOT_DIR
    )

    # 5. Flutter Static Analysis
    results["Flutter Static Analysis"] = run_step(
        "Flutter Static Analysis (flutter analyze)",
        ["flutter", "analyze"],
        cwd=FRONTEND_DIR
    )

    # 6. Flutter Widget & Unit Tests
    results["Flutter Widget & Unit Tests"] = run_step(
        "Flutter Widget Tests (flutter test)",
        ["flutter", "test"],
        cwd=FRONTEND_DIR
    )

    # Summary Report
    print("\n\n################################################################")
    print("   QUALITY ASSURANCE SUMMARY REPORT")
    print("################################################################")
    all_passed = True
    for name, passed in results.items():
        status = "PASSED [OK]" if passed else "FAILED [X]"
        if not passed:
            all_passed = False
        print(f"  - {name:<36} : {status}")

    print("----------------------------------------------------------------")
    if all_passed:
        print("  ALL 6/6 TEST SUITES PASSED CLEANLY! Phase 07 QA VERIFIED!")
    else:
        print("  SOME TESTS FAILED! Review output above.")
    print("################################################################\n")

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
