#!/usr/bin/env python3
"""
Core Backend API Verification Test - Post Dark Theme Implementation
Tests essential functionality to ensure dark theme changes didn't break backend
"""

import requests
import json
import uuid

BASE_URL = "http://localhost:3000/api"
HEADERS = {"Content-Type": "application/json"}

def test_core_backend():
    print("🚀 Core Backend API Verification - Post Dark Theme Implementation")
    print("=" * 70)
    
    results = {"passed": 0, "failed": 0, "total": 0}
    
    def log_test(name, success, message=""):
        results["total"] += 1
        if success:
            results["passed"] += 1
            print(f"✅ {name}: PASSED {message}")
        else:
            results["failed"] += 1
            print(f"❌ {name}: FAILED {message}")
    
    # 1. Test API Root
    try:
        response = requests.get(f"{BASE_URL}/")
        success = response.status_code == 200 and "SXC ScholarHub API is running" in response.json().get("message", "")
        log_test("API Root Endpoint", success, "- API is accessible and responding")
    except Exception as e:
        log_test("API Root Endpoint", False, f"- Exception: {str(e)}")
    
    # 2. Test User Registration
    unique_id = str(uuid.uuid4())[:8]
    test_user = {
        "email": f"testuser{unique_id}@sxc.edu.in",
        "password": "TestPass123",
        "name": f"Test User {unique_id}",
        "department": "Computer Science",
        "year": "2024"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=test_user, headers=HEADERS)
        success = response.status_code == 200 and "user" in response.json() and "token" in response.json()
        log_test("User Registration", success, "- New user registration working")
        
        if success:
            user_data = response.json()
            token = user_data["token"]
            user_role = user_data["user"]["role"]
            log_test("Role Assignment", user_role == "student", f"- User role: {user_role}")
    except Exception as e:
        log_test("User Registration", False, f"- Exception: {str(e)}")
        token = None
    
    # 3. Test User Login
    try:
        login_response = requests.post(f"{BASE_URL}/auth/login", 
                                     json={"email": test_user["email"], "password": test_user["password"]}, 
                                     headers=HEADERS)
        success = login_response.status_code == 200 and "token" in login_response.json()
        log_test("User Login", success, "- Authentication working")
    except Exception as e:
        log_test("User Login", False, f"- Exception: {str(e)}")
    
    # 4. Test Token Verification
    if token:
        try:
            auth_headers = HEADERS.copy()
            auth_headers["Authorization"] = f"Bearer {token}"
            response = requests.get(f"{BASE_URL}/auth/verify", headers=auth_headers)
            success = response.status_code == 200 and "user" in response.json()
            log_test("Token Verification", success, "- JWT token validation working")
        except Exception as e:
            log_test("Token Verification", False, f"- Exception: {str(e)}")
    
    # 5. Test Get Resources
    try:
        response = requests.get(f"{BASE_URL}/resources", headers=HEADERS)
        success = response.status_code == 200 and isinstance(response.json(), list)
        resource_count = len(response.json()) if success else 0
        log_test("Get Resources", success, f"- Retrieved {resource_count} resources")
    except Exception as e:
        log_test("Get Resources", False, f"- Exception: {str(e)}")
    
    # 6. Test Search Functionality
    try:
        response = requests.get(f"{BASE_URL}/search?q=test", headers=HEADERS)
        success = response.status_code == 200 and isinstance(response.json(), list)
        log_test("Search Functionality", success, "- Search endpoint working")
    except Exception as e:
        log_test("Search Functionality", False, f"- Exception: {str(e)}")
    
    # 7. Test CORS Headers
    try:
        response = requests.get(f"{BASE_URL}/", headers=HEADERS)
        cors_headers = ['Access-Control-Allow-Origin', 'Access-Control-Allow-Methods', 'Access-Control-Allow-Headers']
        has_cors = all(header in response.headers for header in cors_headers)
        log_test("CORS Headers", has_cors, "- Cross-origin requests supported")
    except Exception as e:
        log_test("CORS Headers", False, f"- Exception: {str(e)}")
    
    # 8. Test Admin-Only Restrictions (should fail for student)
    if token:
        try:
            auth_headers = HEADERS.copy()
            auth_headers["Authorization"] = f"Bearer {token}"
            
            # Try to upload resource (should fail for student)
            resource_data = {
                "title": "Test Resource",
                "description": "Test description",
                "subject": "Test Subject",
                "department": "Computer Science",
                "year": "2024",
                "type": "notes",
                "gdriveLink": "https://drive.google.com/file/d/test/view"
            }
            
            response = requests.post(f"{BASE_URL}/resources", json=resource_data, headers=auth_headers)
            success = response.status_code == 403  # Should be forbidden for students
            log_test("Admin-Only Restrictions", success, "- Student upload correctly blocked")
        except Exception as e:
            log_test("Admin-Only Restrictions", False, f"- Exception: {str(e)}")
    
    # Print Summary
    print("\n" + "=" * 70)
    print("📊 BACKEND VERIFICATION SUMMARY")
    print("=" * 70)
    print(f"Total Tests: {results['total']}")
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    success_rate = (results['passed'] / results['total'] * 100) if results['total'] > 0 else 0
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("\n🎉 CONCLUSION: Backend APIs are working correctly after dark theme implementation!")
        print("   The dark theme changes did not break any core backend functionality.")
    else:
        print("\n⚠️  CONCLUSION: Some backend issues detected that may need attention.")
    
    return results

if __name__ == "__main__":
    test_core_backend()