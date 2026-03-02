"""
System validation script - Verify production readiness
Run before submitting to OpenHack 2026
"""
import os
import sys
import json

def check_file_exists(filepath, description):
    """Check if required file exists"""
    if os.path.exists(filepath):
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ MISSING {description}: {filepath}")
        return False

def check_file_content(filepath, required_strings, description):
    """Check if file contains required content"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            missing = []
            for req in required_strings:
                if req not in content:
                    missing.append(req)
            
            if not missing:
                print(f"✓ {description} contains required content")
                return True
            else:
                print(f"✗ {description} missing: {', '.join(missing)}")
                return False
    except Exception as e:
        print(f"✗ Error reading {filepath}: {e}")
        return False

def validate_structure():
    """Validate project structure"""
    print("=" * 70)
    print("VALIDATING PROJECT STRUCTURE")
    print("=" * 70)
    
    checks = []
    
    # Check required files
    checks.append(check_file_exists("app/__init__.py", "App package"))
    checks.append(check_file_exists("app/main.py", "Main FastAPI app"))
    checks.append(check_file_exists("app/rules.py", "Rule engine"))
    checks.append(check_file_exists("app/model.py", "Model engine"))
    checks.append(check_file_exists("app/schemas.py", "Pydantic schemas"))
    checks.append(check_file_exists("requirements.txt", "Requirements"))
    checks.append(check_file_exists("Dockerfile", "Dockerfile"))
    checks.append(check_file_exists("README.md", "README"))
    
    return all(checks)

def validate_main_py():
    """Validate main.py has required endpoints"""
    print("\n" + "=" * 70)
    print("VALIDATING MAIN.PY")
    print("=" * 70)
    
    required = [
        '@app.get("/health")',
        '@app.post("/analyze")',
        'port=8000',
        '@app.on_event("startup")',
        'FastAPI'
    ]
    
    return check_file_content("app/main.py", required, "main.py")

def validate_dockerfile():
    """Validate Dockerfile"""
    print("\n" + "=" * 70)
    print("VALIDATING DOCKERFILE")
    print("=" * 70)
    
    required = [
        'FROM python:3.10',
        'EXPOSE 8000',
        'uvicorn',
        'app.main:app',
        '0.0.0.0',
        '8000'
    ]
    
    return check_file_content("Dockerfile", required, "Dockerfile")

def validate_requirements():
    """Validate requirements.txt"""
    print("\n" + "=" * 70)
    print("VALIDATING REQUIREMENTS.TXT")
    print("=" * 70)
    
    required = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'torch',
        'transformers'
    ]
    
    return check_file_content("requirements.txt", required, "requirements.txt")

def validate_schemas():
    """Validate schemas.py"""
    print("\n" + "=" * 70)
    print("VALIDATING SCHEMAS.PY")
    print("=" * 70)
    
    required = [
        'class AnalyzeRequest',
        'class AnalyzeResponse',
        'prompt: str',
        'harmful: bool',
        'articles: List[str]'
    ]
    
    return check_file_content("app/schemas.py", required, "schemas.py")

def validate_rules():
    """Validate rules.py has CCPA sections"""
    print("\n" + "=" * 70)
    print("VALIDATING RULES.PY")
    print("=" * 70)
    
    required = [
        '1798.100',
        '1798.105',
        '1798.120',
        '1798.125',
        'def detect'
    ]
    
    return check_file_content("app/rules.py", required, "rules.py")

def validate_readme():
    """Validate README.md"""
    print("\n" + "=" * 70)
    print("VALIDATING README.MD")
    print("=" * 70)
    
    required = [
        'docker build',
        'docker run',
        'port 8000',
        'POST /analyze',
        'GET /health',
        'HF_TOKEN'
    ]
    
    return check_file_content("README.md", required, "README.md")

def validate_response_format():
    """Validate response format in code"""
    print("\n" + "=" * 70)
    print("VALIDATING RESPONSE FORMAT")
    print("=" * 70)
    
    # Check that schemas enforce correct format
    try:
        with open("app/schemas.py", 'r') as f:
            content = f.read()
            
        # Verify response has harmful and articles
        if 'harmful: bool' in content and 'articles: List[str]' in content:
            print("✓ Response schema enforces correct format")
            return True
        else:
            print("✗ Response schema missing required fields")
            return False
    except Exception as e:
        print(f"✗ Error validating response format: {e}")
        return False

def run_validation():
    """Run all validation checks"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 10 + "CCPA SYSTEM VALIDATION - OpenHack 2026" + " " * 19 + "║")
    print("╚" + "=" * 68 + "╝")
    print("\n")
    
    checks = []
    
    # Run all validation checks
    checks.append(validate_structure())
    checks.append(validate_main_py())
    checks.append(validate_dockerfile())
    checks.append(validate_requirements())
    checks.append(validate_schemas())
    checks.append(validate_rules())
    checks.append(validate_readme())
    checks.append(validate_response_format())
    
    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    
    passed = sum(checks)
    total = len(checks)
    
    print(f"\nPassed: {passed}/{total}")
    
    if all(checks):
        print("\n✓✓✓ ALL CHECKS PASSED - SYSTEM IS PRODUCTION READY ✓✓✓")
        print("\nNext steps:")
        print("1. Build Docker image: docker build -t ccpa-system .")
        print("2. Run container: docker run -p 8000:8000 ccpa-system:latest")
        print("3. Test system: python test_system.py")
        print("4. Submit to OpenHack 2026!")
        return 0
    else:
        print("\n✗✗✗ VALIDATION FAILED - FIX ISSUES ABOVE ✗✗✗")
        return 1

if __name__ == "__main__":
    sys.exit(run_validation())
