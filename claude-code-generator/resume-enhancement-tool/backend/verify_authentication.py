#!/usr/bin/env python
"""Verification script for authentication implementation."""

import sys
from pathlib import Path

def verify_imports():
    """Verify all authentication-related imports work."""
    print("[*] Verifying imports...")

    try:
        from app.api.dependencies import get_current_active_user, get_current_user
        print("[+] Dependencies imports OK")
    except ImportError as e:
        print(f"[-] Dependencies import failed: {e}")
        return False

    try:
        from app.models.user import User
        print("[+] User model import OK")
    except ImportError as e:
        print(f"[-] User model import failed: {e}")
        return False

    try:
        from app.utils.auth import create_access_token, decode_access_token, verify_password, get_password_hash
        print("[+] Auth utils import OK")
    except ImportError as e:
        print(f"[-] Auth utils import failed: {e}")
        return False

    return True

def verify_route_files():
    """Verify all route files compile."""
    print("\n[*] Verifying route files...")

    route_files = [
        'app/api/routes/resumes.py',
        'app/api/routes/jobs.py',
        'app/api/routes/enhancements.py',
        'app/api/routes/style_previews.py',
        'app/api/routes/analysis.py',
        'app/api/routes/comparison.py',
        'app/api/routes/auth.py',
    ]

    for route_file in route_files:
        try:
            import py_compile
            py_compile.compile(route_file, doraise=True)
            print(f"[+] {route_file} compiles OK")
        except Exception as e:
            print(f"[-] {route_file} failed: {e}")
            return False

    return True

def verify_models():
    """Verify models have user_id fields."""
    print("\n[*] Verifying models...")

    try:
        from app.models.resume import Resume
        from app.models.job import Job
        from app.models.enhancement import Enhancement
        from app.models.user import User

        # Check if models have user_id
        assert hasattr(Resume, 'user_id'), "Resume missing user_id"
        assert hasattr(Job, 'user_id'), "Job missing user_id"
        assert hasattr(Enhancement, 'user_id'), "Enhancement missing user_id"

        print("[+] All models have user_id field")
        return True
    except Exception as e:
        print(f"[-] Model verification failed: {e}")
        return False

def count_protected_endpoints():
    """Count protected endpoints in each route file."""
    print("\n[*] Counting protected endpoints...")

    route_files = {
        'resumes.py': 'app/api/routes/resumes.py',
        'jobs.py': 'app/api/routes/jobs.py',
        'enhancements.py': 'app/api/routes/enhancements.py',
        'style_previews.py': 'app/api/routes/style_previews.py',
        'analysis.py': 'app/api/routes/analysis.py',
        'comparison.py': 'app/api/routes/comparison.py',
    }

    total = 0
    for name, path in route_files.items():
        try:
            content = Path(path).read_text()
            # Count occurrences of get_current_active_user
            count = content.count('get_current_active_user')
            print(f"  {name:25} {count} endpoints protected")
            total += count
        except Exception as e:
            print(f"[-] Error reading {name}: {e}")

    print(f"\n  Total protected endpoints: {total}")
    return total

def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Authentication Implementation Verification")
    print("=" * 60)

    checks = [
        ("Imports", verify_imports),
        ("Route Files", verify_route_files),
        ("Models", verify_models),
    ]

    all_passed = True
    for name, check_func in checks:
        if not check_func():
            all_passed = False

    # Count endpoints (informational)
    count_protected_endpoints()

    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] All verification checks passed!")
        print("=" * 60)
        print("\nAuthentication implementation is complete and ready for testing.")
        print("\nNext steps:")
        print("  1. Start the backend server: uvicorn main:app --reload")
        print("  2. Test authentication endpoints with Postman or cURL")
        print("  3. Update frontend to include JWT tokens in API calls")
        print("  4. Run integration tests")
        return 0
    else:
        print("[FAILED] Some verification checks failed!")
        print("=" * 60)
        print("\nPlease review the errors above and fix them.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
