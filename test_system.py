"""
Test script for CCPA Compliance Detection System
Run this to verify the system works correctly
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing /health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    print(f"✓ Health check passed: {response.json()}")

def test_analyze(prompt, expected_harmful, expected_sections=None):
    """Test analyze endpoint"""
    print(f"\nTesting: {prompt[:60]}...")
    
    start_time = time.time()
    response = requests.post(
        f"{BASE_URL}/analyze",
        json={"prompt": prompt}
    )
    elapsed = time.time() - start_time
    
    assert response.status_code == 200
    result = response.json()
    
    print(f"Response ({elapsed:.2f}s): {json.dumps(result, indent=2)}")
    
    # Validate structure
    assert "harmful" in result
    assert "articles" in result
    assert isinstance(result["harmful"], bool)
    assert isinstance(result["articles"], list)
    
    # Validate logic
    if result["harmful"]:
        assert len(result["articles"]) > 0, "harmful=true must have articles"
    else:
        assert len(result["articles"]) == 0, "harmful=false must have empty articles"
    
    # Validate expectations
    assert result["harmful"] == expected_harmful, f"Expected harmful={expected_harmful}"
    
    if expected_sections:
        for section in expected_sections:
            assert section in result["articles"], f"Expected {section} in violations"
    
    print("✓ Test passed")
    return result

def run_tests():
    """Run all test cases"""
    print("=" * 70)
    print("CCPA COMPLIANCE DETECTION SYSTEM - TEST SUITE")
    print("=" * 70)
    
    # Test 1: Health check
    test_health()
    
    # Test 2: No violation
    test_analyze(
        "We provide clear privacy notices and honor all user requests promptly",
        expected_harmful=False
    )
    
    # Test 3: Notice violation (1798.100)
    test_analyze(
        "We collect user data without informing them",
        expected_harmful=True,
        expected_sections=["Section 1798.100"]
    )
    
    # Test 4: Deletion violation (1798.105)
    test_analyze(
        "We refuse to delete user data when requested",
        expected_harmful=True,
        expected_sections=["Section 1798.105"]
    )
    
    # Test 5: Opt-out violation (1798.120)
    test_analyze(
        "Users cannot opt out of data sales",
        expected_harmful=True,
        expected_sections=["Section 1798.120"]
    )
    
    # Test 6: Discrimination violation (1798.125)
    test_analyze(
        "We charge higher prices to users who opt out of data sharing",
        expected_harmful=True,
        expected_sections=["Section 1798.125"]
    )
    
    # Test 7: Multiple violations
    test_analyze(
        "We sell user data without notice and ignore deletion requests",
        expected_harmful=True,
        expected_sections=["Section 1798.100", "Section 1798.105", "Section 1798.120"]
    )
    
    # Test 8: Minor protection (1798.121)
    test_analyze(
        "We sell personal information of users under 16 years old",
        expected_harmful=True,
        expected_sections=["Section 1798.120", "Section 1798.121"]
    )
    
    # Test 9: Do Not Sell link (1798.135)
    test_analyze(
        "Our website has no Do Not Sell My Personal Information link",
        expected_harmful=True,
        expected_sections=["Section 1798.135"]
    )
    
    # Test 10: Correction violation (1798.106)
    test_analyze(
        "We deny requests to correct inaccurate personal information",
        expected_harmful=True,
        expected_sections=["Section 1798.106"]
    )
    
    # Test 11: Response violation (1798.130)
    test_analyze(
        "We never respond to consumer privacy requests",
        expected_harmful=True,
        expected_sections=["Section 1798.130"]
    )
    
    # Test 12: Synonyms (sell/share/disclose)
    test_analyze(
        "We share consumer data with third parties without consent",
        expected_harmful=True,
        expected_sections=["Section 1798.120"]
    )
    
    print("\n" + "=" * 70)
    print("ALL TESTS PASSED ✓")
    print("=" * 70)

if __name__ == "__main__":
    try:
        run_tests()
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to server. Make sure it's running on port 8000")
        print("Start server with: uvicorn app.main:app --host 0.0.0.0 --port 8000")
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
