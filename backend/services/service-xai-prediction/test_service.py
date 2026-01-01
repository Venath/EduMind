#!/usr/bin/env python3
"""Quick test script for backend service"""

import sys
import time

print("=" * 60)
print("BACKEND SERVICE QUICK TEST")
print("=" * 60)

# Test 1: Basic imports
print("\n[1/4] Testing basic imports...")
start = time.time()
try:
    import numpy as np
    import xgboost

    print(f"   ✓ Core libraries imported ({time.time()-start:.2f}s)")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    sys.exit(1)

# Test 2: Load service
print("\n[2/4] Loading academic risk service...")
start = time.time()
try:
    from app.Services.academic_risk_service import academic_risk_service

    print(f"   ✓ Service loaded ({time.time()-start:.2f}s)")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    sys.exit(1)

# Test 3: Check model
print("\n[3/4] Verifying model...")
if academic_risk_service.model is not None:
    print(f"   ✓ Model: Loaded")
    print(f"   ✓ Features: {len(academic_risk_service.feature_names)}")
    print(f"   ✓ Accuracy: {academic_risk_service.metadata['accuracy']*100:.1f}%")
else:
    print("   ✗ Model not loaded")
    sys.exit(1)

# Test 4: Quick prediction
print("\n[4/4] Testing prediction...")
start = time.time()
try:
    import asyncio

    from app.schemas.academic_risk import AcademicRiskRequest

    async def test():
        req = AcademicRiskRequest(
            student_id="test",
            avg_grade=65.0,
            grade_consistency=80.0,
            grade_range=25.0,
            num_assessments=8,
            assessment_completion_rate=0.8,
            studied_credits=60,
            num_of_prev_attempts=0,
            low_performance=0,
            low_engagement=0,
            has_previous_attempts=0,
        )
        result = await academic_risk_service.predict(req)
        return result

    result = asyncio.run(test())
    print(f"   ✓ Prediction works ({time.time()-start:.2f}s)")
    print(f"   ✓ Risk: {result.risk_level}")
    print(f"   ✓ Confidence: {result.confidence:.1%}")

except Exception as e:
    print(f"   ✗ Failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED - SERVICE IS READY!")
print("=" * 60)
print("\nYou can now start the API server:")
print("  uvicorn app.main:app --reload --port 8000")
