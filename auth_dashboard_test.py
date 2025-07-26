#!/usr/bin/env python3
"""
Focused Backend API Testing for Authentication System and Dashboard Functionality
Testing specifically as requested in the review request.
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:3000/api"

# Test data as requested
TEST_USER_DATA = {
    "email": "test@example.com",
    "password": "password123",
    "name": "Test User",
    "department": "Computer Science",
    "year": "First Year"
}

# Admin test data
ADMIN_USER_DATA = {
    "email": "sahuatul2005@gmail.com",  # This email gets admin role per backend logic
    "password": "password123",
    "name": "Admin User",
    "department": "Computer Science", 
    "year": "Faculty"
}

class AuthDashboardTester:
    def __init__(self):
        self.session = requests.Session()
        self.student_token = None
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()
        
    def test_api_connectivity(self):
        """Test basic API connectivity"""
        try:
            response = self.session.get(f"{BASE_URL}/")
            if response.status_code == 200:
                data = response.json()
                if "lScholarHub API" in data.get("message", ""):
                    self.log_test("API Connectivity", True, f"API is running: {data['message']}")
                    return True
                else:
                    self.log_test("API Connectivity", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("API Connectivity", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("API Connectivity", False, f"Exception: {str(e)}")
            return False
    
    def test_user_registration(self):
        """Test user registration with the provided test data"""
        try:
            # Test student registration
            response = self.session.post(f"{BASE_URL}/auth/register", json=TEST_USER_DATA)
            
            if response.status_code == 200:
                data = response.json()
                if "user" in data and "token" in data:
                    user = data["user"]
                    self.student_token = data["token"]
                    
                    # Verify user data
                    expected_fields = ["id", "email", "name", "department", "year", "role", "downloads", "recentViews", "bookmarks"]
                    missing_fields = [field for field in expected_fields if field not in user]
                    
                    if not missing_fields:
                        # Verify dashboard tracking fields are initialized
                        if (user["downloads"] == 0 and 
                            user["recentViews"] == [] and 
                            user["bookmarks"] == [] and
                            user["role"] == "student"):
                            self.log_test("User Registration", True, 
                                        f"User created successfully with ID: {user['id']}, Role: {user['role']}, Dashboard fields initialized")
                            return True
                        else:
                            self.log_test("User Registration", False, 
                                        f"Dashboard fields not properly initialized: downloads={user['downloads']}, recentViews={user['recentViews']}, bookmarks={user['bookmarks']}")
                            return False
                    else:
                        self.log_test("User Registration", False, f"Missing fields: {missing_fields}")
                        return False
                else:
                    self.log_test("User Registration", False, f"Missing user or token in response: {data}")
                    return False
            elif response.status_code == 400 and "already exists" in response.text:
                # User already exists, try to login instead
                login_response = self.session.post(f"{BASE_URL}/auth/login", json={
                    "email": TEST_USER_DATA["email"],
                    "password": TEST_USER_DATA["password"]
                })
                if login_response.status_code == 200:
                    data = login_response.json()
                    self.student_token = data["token"]
                    self.log_test("User Registration", True, "User already exists, logged in successfully")
                    return True
                else:
                    self.log_test("User Registration", False, f"User exists but login failed: {login_response.text}")
                    return False
            else:
                self.log_test("User Registration", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("User Registration", False, f"Exception: {str(e)}")
            return False
    
    def test_admin_registration(self):
        """Test admin user registration"""
        try:
            response = self.session.post(f"{BASE_URL}/auth/register", json=ADMIN_USER_DATA)
            
            if response.status_code == 200:
                data = response.json()
                if "user" in data and "token" in data:
                    user = data["user"]
                    self.admin_token = data["token"]
                    
                    if user["role"] == "admin":
                        self.log_test("Admin Registration", True, 
                                    f"Admin user created successfully with ID: {user['id']}, Role: {user['role']}")
                        return True
                    else:
                        self.log_test("Admin Registration", False, 
                                    f"Expected admin role but got: {user['role']}")
                        return False
                else:
                    self.log_test("Admin Registration", False, f"Missing user or token in response: {data}")
                    return False
            elif response.status_code == 400 and "already exists" in response.text:
                # Admin already exists, try to login
                login_response = self.session.post(f"{BASE_URL}/auth/login", json={
                    "email": ADMIN_USER_DATA["email"],
                    "password": ADMIN_USER_DATA["password"]
                })
                if login_response.status_code == 200:
                    data = login_response.json()
                    self.admin_token = data["token"]
                    if data["user"]["role"] == "admin":
                        self.log_test("Admin Registration", True, "Admin user already exists, logged in successfully")
                        return True
                    else:
                        self.log_test("Admin Registration", False, f"Expected admin role but got: {data['user']['role']}")
                        return False
                else:
                    self.log_test("Admin Registration", False, f"Admin exists but login failed: {login_response.text}")
                    return False
            else:
                self.log_test("Admin Registration", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Registration", False, f"Exception: {str(e)}")
            return False
    
    def test_user_login(self):
        """Test user login functionality"""
        try:
            login_data = {
                "email": TEST_USER_DATA["email"],
                "password": TEST_USER_DATA["password"]
            }
            
            response = self.session.post(f"{BASE_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "user" in data and "token" in data:
                    # Verify token format (should be base64 encoded)
                    token = data["token"]
                    if len(token) > 20:  # Basic token length check
                        self.student_token = token  # Update token
                        self.log_test("User Login", True, 
                                    f"Login successful, token received (length: {len(token)})")
                        return True
                    else:
                        self.log_test("User Login", False, f"Token seems invalid: {token}")
                        return False
                else:
                    self.log_test("User Login", False, f"Missing user or token in response: {data}")
                    return False
            else:
                self.log_test("User Login", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("User Login", False, f"Exception: {str(e)}")
            return False
    
    def test_token_verification(self):
        """Test token verification endpoint"""
        if not self.student_token:
            self.log_test("Token Verification", False, "No student token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            response = self.session.get(f"{BASE_URL}/auth/verify", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "user" in data:
                    user = data["user"]
                    if user["email"] == TEST_USER_DATA["email"]:
                        self.log_test("Token Verification", True, 
                                    f"Token verified successfully for user: {user['email']}")
                        return True
                    else:
                        self.log_test("Token Verification", False, 
                                    f"Token verified but wrong user: {user['email']}")
                        return False
                else:
                    self.log_test("Token Verification", False, f"Missing user in response: {data}")
                    return False
            else:
                self.log_test("Token Verification", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Token Verification", False, f"Exception: {str(e)}")
            return False
    
    def test_student_dashboard_endpoint(self):
        """Test student dashboard endpoint"""
        if not self.student_token:
            self.log_test("Student Dashboard Endpoint", False, "No student token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            response = self.session.get(f"{BASE_URL}/dashboard/student", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                required_fields = ["totalDownloads", "recentResources", "bookmarkedResources", "trendingResources"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    # Verify data types
                    if (isinstance(data["totalDownloads"], int) and
                        isinstance(data["recentResources"], list) and
                        isinstance(data["bookmarkedResources"], list) and
                        isinstance(data["trendingResources"], list)):
                        
                        self.log_test("Student Dashboard Endpoint", True, 
                                    f"Dashboard data structure correct: totalDownloads={data['totalDownloads']}, "
                                    f"recentResources={len(data['recentResources'])}, "
                                    f"bookmarkedResources={len(data['bookmarkedResources'])}, "
                                    f"trendingResources={len(data['trendingResources'])}")
                        return True
                    else:
                        self.log_test("Student Dashboard Endpoint", False, 
                                    f"Incorrect data types in response: {data}")
                        return False
                else:
                    self.log_test("Student Dashboard Endpoint", False, f"Missing required fields: {missing_fields}")
                    return False
            else:
                self.log_test("Student Dashboard Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Student Dashboard Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_admin_dashboard_endpoint(self):
        """Test admin dashboard endpoint"""
        if not self.admin_token:
            self.log_test("Admin Dashboard Endpoint", False, "No admin token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{BASE_URL}/dashboard/admin", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                required_fields = ["totalUploads", "recentUploads", "pendingRequests"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    # Verify data types
                    if (isinstance(data["totalUploads"], int) and
                        isinstance(data["recentUploads"], list) and
                        isinstance(data["pendingRequests"], list)):
                        
                        self.log_test("Admin Dashboard Endpoint", True, 
                                    f"Admin dashboard data structure correct: totalUploads={data['totalUploads']}, "
                                    f"recentUploads={len(data['recentUploads'])}, "
                                    f"pendingRequests={len(data['pendingRequests'])}")
                        return True
                    else:
                        self.log_test("Admin Dashboard Endpoint", False, 
                                    f"Incorrect data types in response: {data}")
                        return False
                else:
                    self.log_test("Admin Dashboard Endpoint", False, f"Missing required fields: {missing_fields}")
                    return False
            else:
                self.log_test("Admin Dashboard Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Dashboard Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_student_access_to_admin_dashboard(self):
        """Test that student users cannot access admin dashboard"""
        if not self.student_token:
            self.log_test("Student Access to Admin Dashboard (Should Fail)", False, "No student token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            response = self.session.get(f"{BASE_URL}/dashboard/admin", headers=headers)
            
            if response.status_code == 403:
                self.log_test("Student Access to Admin Dashboard (Should Fail)", True, 
                            "Student correctly blocked from admin dashboard with 403 Forbidden")
                return True
            else:
                self.log_test("Student Access to Admin Dashboard (Should Fail)", False, 
                            f"Expected 403 but got HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Student Access to Admin Dashboard (Should Fail)", False, f"Exception: {str(e)}")
            return False
    
    def test_unauthenticated_dashboard_access(self):
        """Test that unauthenticated users cannot access dashboard endpoints"""
        try:
            # Test student dashboard without token
            response = self.session.get(f"{BASE_URL}/dashboard/student")
            
            if response.status_code == 401:
                self.log_test("Unauthenticated Dashboard Access (Should Fail)", True, 
                            "Unauthenticated access correctly blocked with 401 Unauthorized")
                return True
            else:
                self.log_test("Unauthenticated Dashboard Access (Should Fail)", False, 
                            f"Expected 401 but got HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Unauthenticated Dashboard Access (Should Fail)", False, f"Exception: {str(e)}")
            return False
    
    def test_invalid_token_access(self):
        """Test dashboard access with invalid token"""
        try:
            headers = {"Authorization": "Bearer invalid_token_12345"}
            response = self.session.get(f"{BASE_URL}/dashboard/student", headers=headers)
            
            if response.status_code == 401:
                self.log_test("Invalid Token Access (Should Fail)", True, 
                            "Invalid token correctly rejected with 401 Unauthorized")
                return True
            else:
                self.log_test("Invalid Token Access (Should Fail)", False, 
                            f"Expected 401 but got HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Invalid Token Access (Should Fail)", False, f"Exception: {str(e)}")
            return False
    
    def run_focused_tests(self):
        """Run focused authentication and dashboard tests as requested"""
        print("🚀 Starting Focused Authentication & Dashboard Testing")
        print("Testing specifically as requested in the review request")
        print("=" * 80)
        print()
        
        # Test sequence as requested
        tests = [
            ("API Connectivity Check", self.test_api_connectivity),
            ("1. User Registration - Create Test User", self.test_user_registration),
            ("2. User Login - Verify Token Return", self.test_user_login),
            ("Token Verification", self.test_token_verification),
            ("Admin User Setup", self.test_admin_registration),
            ("3. Student Dashboard Endpoint (/api/dashboard/student)", self.test_student_dashboard_endpoint),
            ("4. Admin Dashboard Endpoint (/api/dashboard/admin)", self.test_admin_dashboard_endpoint),
            ("Student Access to Admin Dashboard (Should Fail)", self.test_student_access_to_admin_dashboard),
            ("Unauthenticated Dashboard Access (Should Fail)", self.test_unauthenticated_dashboard_access),
            ("Invalid Token Access (Should Fail)", self.test_invalid_token_access)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"Running: {test_name}")
            print("-" * 40)
            if test_func():
                passed += 1
            time.sleep(0.5)  # Small delay between tests
        
        # Summary
        print("=" * 80)
        print("🎯 FOCUSED TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (passed / total) * 100
        print(f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
        print()
        
        # Detailed results
        for result in self.test_results:
            print(f"{result['status']}: {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
        
        print()
        print("=" * 80)
        
        if success_rate >= 90:
            print("🎉 EXCELLENT: Authentication and Dashboard system working perfectly!")
            print("✅ Ready for frontend Dashboard click issue fix testing")
        elif success_rate >= 80:
            print("✅ GOOD: Most functionality working, minor issues detected")
            print("⚠️  Some issues may affect frontend Dashboard functionality")
        elif success_rate >= 60:
            print("⚠️  WARNING: Some critical issues found")
            print("❌ Frontend Dashboard may have issues")
        else:
            print("❌ CRITICAL: Major issues detected, system needs attention")
            print("❌ Frontend Dashboard will likely not work properly")
        
        print("=" * 80)
        
        # Print token information for frontend testing
        if self.student_token:
            print(f"📋 Student Token Available: {self.student_token[:20]}...")
        if self.admin_token:
            print(f"📋 Admin Token Available: {self.admin_token[:20]}...")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = AuthDashboardTester()
    success = tester.run_focused_tests()
    sys.exit(0 if success else 1)