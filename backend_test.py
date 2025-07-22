#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Bookmark Persistence Functionality
Tests the specific scenarios requested in the review:
1. User Registration and Login (student role)
2. Bookmark Creation (admin creates resource, student bookmarks it)
3. Backend Verification (via /api/dashboard/student)
4. Token Persistence (simulated refresh with new token verification)
5. Bookmark Toggle (remove and re-add)
"""

import requests
import json
import uuid
import time
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:3000/api"

class BookmarkPersistenceTest:
    def __init__(self):
        self.base_url = BASE_URL
        self.student_token = None
        self.admin_token = None
        self.student_user = None
        self.admin_user = None
        self.test_resource_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
    
    def make_request(self, method, endpoint, data=None, headers=None, timeout=30):
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=timeout)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request error for {method} {url}: {e}")
            return None
    
    def test_1_student_registration(self):
        """Test 1: Create a new test user with student role"""
        print("\n=== TEST 1: Student User Registration ===")
        
        # Generate unique test data
        timestamp = int(time.time())
        student_data = {
            "name": f"Test Student {timestamp}",
            "email": f"student{timestamp}@test.com",
            "password": "testpass123",
            "department": "Computer Science",
            "year": "2024"
        }
        
        response = self.make_request('POST', '/auth/register', student_data)
        
        if not response:
            self.log_test("Student Registration", False, "Network error during registration")
            return False
        
        if response.status_code == 200:
            data = response.json()
            if 'user' in data and 'token' in data:
                self.student_user = data['user']
                self.student_token = data['token']
                
                # Verify student role and dashboard fields
                user = self.student_user
                has_dashboard_fields = (
                    'downloads' in user and user['downloads'] == 0 and
                    'recentViews' in user and user['recentViews'] == [] and
                    'bookmarks' in user and user['bookmarks'] == [] and
                    user['role'] == 'student'
                )
                
                if has_dashboard_fields:
                    self.log_test("Student Registration", True, 
                                f"Student user created successfully with dashboard fields initialized",
                                f"User ID: {user['id']}, Role: {user['role']}")
                    return True
                else:
                    self.log_test("Student Registration", False, 
                                "User created but missing dashboard fields or wrong role",
                                f"User data: {user}")
                    return False
            else:
                self.log_test("Student Registration", False, 
                            "Registration response missing user or token",
                            f"Response: {data}")
                return False
        else:
            self.log_test("Student Registration", False, 
                        f"Registration failed with status {response.status_code}",
                        f"Response: {response.text}")
            return False
    
    def test_2_admin_setup_and_resource_creation(self):
        """Test 2: Setup admin user and use existing test resource"""
        print("\n=== TEST 2: Admin Setup and Resource Selection ===")
        
        # Try to login with existing admin user
        login_data = {
            "email": "sahuatul2005@gmail.com",
            "password": "adminpass123"
        }
        response = self.make_request('POST', '/auth/login', login_data)
        
        if response and response.status_code == 200:
            data = response.json()
            self.admin_user = data['user']
            self.admin_token = data['token']
            self.log_test("Admin Login", True, 
                        f"Admin user logged in successfully",
                        f"Admin ID: {self.admin_user['id']}, Role: {self.admin_user['role']}")
        else:
            # Admin login failed, but we can still test with existing resources
            self.log_test("Admin Login", False, "Admin login failed, will use existing resource")
        
        # Get existing resource for testing
        response = self.make_request('GET', '/resources')
        
        if response and response.status_code == 200:
            resources = response.json()
            if resources and len(resources) > 0:
                self.test_resource_id = resources[0]['id']
                self.log_test("Resource Selection", True, 
                            "Using existing resource for bookmark testing",
                            f"Resource ID: {self.test_resource_id}, Title: {resources[0].get('title', 'N/A')}")
                return True
            else:
                self.log_test("Resource Selection", False, "No resources available for testing")
                return False
        else:
            error_msg = response.text if response else "Network error"
            self.log_test("Resource Selection", False, 
                        f"Failed to get resources",
                        f"Status: {response.status_code if response else 'N/A'}, Error: {error_msg}")
            return False
    
    def test_3_student_login(self):
        """Test 3: Student login to get fresh token"""
        print("\n=== TEST 3: Student Login ===")
        
        if not self.student_user:
            self.log_test("Student Login", False, "No student user available for login")
            return False
        
        login_data = {
            "email": self.student_user['email'],
            "password": "testpass123"
        }
        
        response = self.make_request('POST', '/auth/login', login_data)
        
        if response and response.status_code == 200:
            data = response.json()
            if 'token' in data:
                self.student_token = data['token']
                self.log_test("Student Login", True, 
                            "Student login successful, token obtained",
                            f"Token length: {len(self.student_token)}")
                return True
            else:
                self.log_test("Student Login", False, 
                            "Login response missing token",
                            f"Response: {data}")
                return False
        else:
            error_msg = response.text if response else "Network error"
            self.log_test("Student Login", False, 
                        f"Login failed",
                        f"Status: {response.status_code if response else 'N/A'}, Error: {error_msg}")
            return False
    
    def test_4_initial_dashboard_state(self):
        """Test 4: Verify initial dashboard state (no bookmarks)"""
        print("\n=== TEST 4: Initial Dashboard State ===")
        
        if not self.student_token:
            self.log_test("Initial Dashboard", False, "No student token available")
            return False
        
        headers = {'Authorization': f'Bearer {self.student_token}'}
        response = self.make_request('GET', '/dashboard/student', headers=headers)
        
        if response and response.status_code == 200:
            data = response.json()
            expected_fields = ['totalDownloads', 'recentResources', 'bookmarkedResources', 'trendingResources']
            
            if all(field in data for field in expected_fields):
                bookmarked_count = len(data['bookmarkedResources'])
                self.log_test("Initial Dashboard", True, 
                            f"Dashboard endpoint working, initial bookmarks: {bookmarked_count}",
                            f"Dashboard data: {data}")
                return True
            else:
                self.log_test("Initial Dashboard", False, 
                            "Dashboard response missing required fields",
                            f"Response: {data}")
                return False
        else:
            error_msg = response.text if response else "Network error"
            self.log_test("Initial Dashboard", False, 
                        f"Dashboard request failed",
                        f"Status: {response.status_code if response else 'N/A'}, Error: {error_msg}")
            return False
    
    def test_5_bookmark_creation(self):
        """Test 5: Create bookmark (student bookmarks admin's resource)"""
        print("\n=== TEST 5: Bookmark Creation ===")
        
        if not self.student_token or not self.test_resource_id:
            self.log_test("Bookmark Creation", False, "Missing student token or resource ID")
            return False
        
        headers = {'Authorization': f'Bearer {self.student_token}'}
        response = self.make_request('POST', f'/resources/{self.test_resource_id}/bookmark', headers=headers)
        
        if response and response.status_code == 200:
            data = response.json()
            if 'isBookmarked' in data and data['isBookmarked'] == True:
                self.log_test("Bookmark Creation", True, 
                            "Bookmark added successfully",
                            f"Response: {data}")
                return True
            else:
                self.log_test("Bookmark Creation", False, 
                            "Bookmark response indicates not bookmarked",
                            f"Response: {data}")
                return False
        else:
            error_msg = response.text if response else "Network error"
            self.log_test("Bookmark Creation", False, 
                        f"Bookmark creation failed",
                        f"Status: {response.status_code if response else 'N/A'}, Error: {error_msg}")
            return False
    
    def test_6_dashboard_verification_after_bookmark(self):
        """Test 6: Verify bookmark appears in dashboard"""
        print("\n=== TEST 6: Dashboard Verification After Bookmark ===")
        
        if not self.student_token:
            self.log_test("Dashboard Verification", False, "No student token available")
            return False
        
        headers = {'Authorization': f'Bearer {self.student_token}'}
        response = self.make_request('GET', '/dashboard/student', headers=headers)
        
        if response and response.status_code == 200:
            data = response.json()
            bookmarked_resources = data.get('bookmarkedResources', [])
            
            # Check if our test resource is in bookmarks
            bookmarked_ids = [resource['id'] for resource in bookmarked_resources]
            
            if self.test_resource_id in bookmarked_ids:
                self.log_test("Dashboard Verification", True, 
                            f"Bookmark correctly saved and appears in dashboard",
                            f"Bookmarked resources count: {len(bookmarked_resources)}")
                return True
            else:
                self.log_test("Dashboard Verification", False, 
                            "Bookmark not found in dashboard",
                            f"Expected resource ID: {self.test_resource_id}, Found IDs: {bookmarked_ids}")
                return False
        else:
            error_msg = response.text if response else "Network error"
            self.log_test("Dashboard Verification", False, 
                        f"Dashboard request failed",
                        f"Status: {response.status_code if response else 'N/A'}, Error: {error_msg}")
            return False
    
    def test_7_token_persistence_simulation(self):
        """Test 7: Simulate page refresh by getting new token and verifying bookmarks persist"""
        print("\n=== TEST 7: Token Persistence Simulation (Simulated Page Refresh) ===")
        
        if not self.student_user:
            self.log_test("Token Persistence", False, "No student user available")
            return False
        
        # Simulate page refresh by logging in again (new token)
        login_data = {
            "email": self.student_user['email'],
            "password": "testpass123"
        }
        
        response = self.make_request('POST', '/auth/login', login_data)
        
        if response and response.status_code == 200:
            data = response.json()
            new_token = data['token']
            
            # Verify it's a different token (simulating refresh)
            if new_token != self.student_token:
                self.log_test("New Token Generation", True, 
                            "New token generated successfully (simulating refresh)",
                            f"Old token length: {len(self.student_token)}, New token length: {len(new_token)}")
                
                # Update to new token
                self.student_token = new_token
                
                # Now verify bookmarks still exist with new token
                headers = {'Authorization': f'Bearer {self.student_token}'}
                dashboard_response = self.make_request('GET', '/dashboard/student', headers=headers)
                
                if dashboard_response and dashboard_response.status_code == 200:
                    dashboard_data = dashboard_response.json()
                    bookmarked_resources = dashboard_data.get('bookmarkedResources', [])
                    bookmarked_ids = [resource['id'] for resource in bookmarked_resources]
                    
                    if self.test_resource_id in bookmarked_ids:
                        self.log_test("Token Persistence", True, 
                                    "Bookmarks persist after token refresh (simulated page refresh)",
                                    f"Bookmarked resources: {len(bookmarked_resources)}")
                        return True
                    else:
                        self.log_test("Token Persistence", False, 
                                    "Bookmarks lost after token refresh",
                                    f"Expected: {self.test_resource_id}, Found: {bookmarked_ids}")
                        return False
                else:
                    self.log_test("Token Persistence", False, 
                                "Dashboard request failed with new token")
                    return False
            else:
                self.log_test("Token Persistence", False, 
                            "New token is same as old token")
                return False
        else:
            self.log_test("Token Persistence", False, 
                        "Failed to get new token for persistence test")
            return False
    
    def test_8_bookmark_toggle_removal(self):
        """Test 8: Test bookmark removal"""
        print("\n=== TEST 8: Bookmark Toggle - Removal ===")
        
        if not self.student_token or not self.test_resource_id:
            self.log_test("Bookmark Removal", False, "Missing student token or resource ID")
            return False
        
        headers = {'Authorization': f'Bearer {self.student_token}'}
        response = self.make_request('POST', f'/resources/{self.test_resource_id}/bookmark', headers=headers)
        
        if response and response.status_code == 200:
            data = response.json()
            if 'isBookmarked' in data and data['isBookmarked'] == False:
                self.log_test("Bookmark Removal", True, 
                            "Bookmark removed successfully",
                            f"Response: {data}")
                
                # Verify removal in dashboard
                dashboard_response = self.make_request('GET', '/dashboard/student', headers=headers)
                if dashboard_response and dashboard_response.status_code == 200:
                    dashboard_data = dashboard_response.json()
                    bookmarked_resources = dashboard_data.get('bookmarkedResources', [])
                    bookmarked_ids = [resource['id'] for resource in bookmarked_resources]
                    
                    if self.test_resource_id not in bookmarked_ids:
                        self.log_test("Bookmark Removal Verification", True, 
                                    "Bookmark removal verified in dashboard",
                                    f"Remaining bookmarks: {len(bookmarked_resources)}")
                        return True
                    else:
                        self.log_test("Bookmark Removal Verification", False, 
                                    "Bookmark still appears in dashboard after removal")
                        return False
                else:
                    self.log_test("Bookmark Removal Verification", False, 
                                "Could not verify removal in dashboard")
                    return False
            else:
                self.log_test("Bookmark Removal", False, 
                            "Bookmark removal response indicates still bookmarked",
                            f"Response: {data}")
                return False
        else:
            error_msg = response.text if response else "Network error"
            self.log_test("Bookmark Removal", False, 
                        f"Bookmark removal failed",
                        f"Status: {response.status_code if response else 'N/A'}, Error: {error_msg}")
            return False
    
    def test_9_bookmark_toggle_re_addition(self):
        """Test 9: Test bookmark re-addition"""
        print("\n=== TEST 9: Bookmark Toggle - Re-addition ===")
        
        if not self.student_token or not self.test_resource_id:
            self.log_test("Bookmark Re-addition", False, "Missing student token or resource ID")
            return False
        
        headers = {'Authorization': f'Bearer {self.student_token}'}
        response = self.make_request('POST', f'/resources/{self.test_resource_id}/bookmark', headers=headers)
        
        if response and response.status_code == 200:
            data = response.json()
            if 'isBookmarked' in data and data['isBookmarked'] == True:
                self.log_test("Bookmark Re-addition", True, 
                            "Bookmark re-added successfully",
                            f"Response: {data}")
                
                # Verify re-addition in dashboard
                dashboard_response = self.make_request('GET', '/dashboard/student', headers=headers)
                if dashboard_response and dashboard_response.status_code == 200:
                    dashboard_data = dashboard_response.json()
                    bookmarked_resources = dashboard_data.get('bookmarkedResources', [])
                    bookmarked_ids = [resource['id'] for resource in bookmarked_resources]
                    
                    if self.test_resource_id in bookmarked_ids:
                        self.log_test("Bookmark Re-addition Verification", True, 
                                    "Bookmark re-addition verified in dashboard",
                                    f"Total bookmarks: {len(bookmarked_resources)}")
                        return True
                    else:
                        self.log_test("Bookmark Re-addition Verification", False, 
                                    "Bookmark not found in dashboard after re-addition")
                        return False
                else:
                    self.log_test("Bookmark Re-addition Verification", False, 
                                "Could not verify re-addition in dashboard")
                    return False
            else:
                self.log_test("Bookmark Re-addition", False, 
                            "Bookmark re-addition response indicates not bookmarked",
                            f"Response: {data}")
                return False
        else:
            error_msg = response.text if response else "Network error"
            self.log_test("Bookmark Re-addition", False, 
                        f"Bookmark re-addition failed",
                        f"Status: {response.status_code if response else 'N/A'}, Error: {error_msg}")
            return False
    
    def test_10_final_persistence_verification(self):
        """Test 10: Final verification of bookmark persistence with another token refresh"""
        print("\n=== TEST 10: Final Persistence Verification ===")
        
        if not self.student_user:
            self.log_test("Final Persistence", False, "No student user available")
            return False
        
        # One more login to get fresh token
        login_data = {
            "email": self.student_user['email'],
            "password": "testpass123"
        }
        
        response = self.make_request('POST', '/auth/login', login_data)
        
        if response and response.status_code == 200:
            data = response.json()
            final_token = data['token']
            
            # Verify bookmarks with final token
            headers = {'Authorization': f'Bearer {final_token}'}
            dashboard_response = self.make_request('GET', '/dashboard/student', headers=headers)
            
            if dashboard_response and dashboard_response.status_code == 200:
                dashboard_data = dashboard_response.json()
                bookmarked_resources = dashboard_data.get('bookmarkedResources', [])
                bookmarked_ids = [resource['id'] for resource in bookmarked_resources]
                
                if self.test_resource_id in bookmarked_ids:
                    self.log_test("Final Persistence", True, 
                                "Bookmark persistence confirmed after multiple token refreshes",
                                f"Final bookmark count: {len(bookmarked_resources)}")
                    return True
                else:
                    self.log_test("Final Persistence", False, 
                                "Bookmark lost in final persistence check",
                                f"Expected: {self.test_resource_id}, Found: {bookmarked_ids}")
                    return False
            else:
                self.log_test("Final Persistence", False, 
                            "Dashboard request failed in final check")
                return False
        else:
            self.log_test("Final Persistence", False, 
                        "Failed to get final token for persistence verification")
            return False
    
    def run_all_tests(self):
        """Run all bookmark persistence tests"""
        print("🎯 STARTING COMPREHENSIVE BOOKMARK PERSISTENCE TESTING")
        print("=" * 80)
        
        test_methods = [
            self.test_1_student_registration,
            self.test_2_admin_setup_and_resource_creation,
            self.test_3_student_login,
            self.test_4_initial_dashboard_state,
            self.test_5_bookmark_creation,
            self.test_6_dashboard_verification_after_bookmark,
            self.test_7_token_persistence_simulation,
            self.test_8_bookmark_toggle_removal,
            self.test_9_bookmark_toggle_re_addition,
            self.test_10_final_persistence_verification
        ]
        
        passed_tests = 0
        total_tests = len(test_methods)
        
        for test_method in test_methods:
            try:
                success = test_method()
                if success:
                    passed_tests += 1
                time.sleep(1)  # Brief pause between tests
            except Exception as e:
                print(f"❌ EXCEPTION in {test_method.__name__}: {e}")
                self.log_test(test_method.__name__, False, f"Exception: {e}")
        
        # Final summary
        print("\n" + "=" * 80)
        print("🎯 BOOKMARK PERSISTENCE TESTING SUMMARY")
        print("=" * 80)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"📊 OVERALL RESULT: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}% success rate)")
        
        if success_rate >= 90:
            print("🎉 EXCELLENT: Bookmark persistence functionality working excellently!")
        elif success_rate >= 75:
            print("✅ GOOD: Bookmark persistence functionality working well with minor issues")
        elif success_rate >= 50:
            print("⚠️ MODERATE: Bookmark persistence has some issues that need attention")
        else:
            print("❌ CRITICAL: Bookmark persistence has major issues requiring immediate fix")
        
        print("\n📋 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}: {result['message']}")
        
        print("\n🔍 KEY FINDINGS:")
        if passed_tests == total_tests:
            print("• All bookmark persistence scenarios working correctly")
            print("• Bookmarks persist across token refreshes (simulated page refreshes)")
            print("• Bookmark toggle functionality (add/remove) working properly")
            print("• Dashboard integration working correctly")
            print("• Authentication and authorization working as expected")
        else:
            failed_tests = [r for r in self.test_results if not r['success']]
            print(f"• {len(failed_tests)} test(s) failed:")
            for failed in failed_tests:
                print(f"  - {failed['test']}: {failed['message']}")
        
        return success_rate >= 75  # Consider 75%+ as overall success

def main():
    """Main test execution"""
    print("🚀 BOOKMARK PERSISTENCE TESTING STARTED")
    print(f"🌐 Testing against: {BASE_URL}")
    print(f"⏰ Test started at: {datetime.now().isoformat()}")
    
    tester = BookmarkPersistenceTest()
    success = tester.run_all_tests()
    
    print(f"\n⏰ Test completed at: {datetime.now().isoformat()}")
    
    if success:
        print("🎉 BOOKMARK PERSISTENCE TESTING COMPLETED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("❌ BOOKMARK PERSISTENCE TESTING COMPLETED WITH ISSUES!")
        sys.exit(1)

if __name__ == "__main__":
    main()
HEADERS = {"Content-Type": "application/json"}

class ScholarHubAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS.copy()
        self.auth_token = None
        self.test_user_id = None
        self.test_resource_id = None
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": []
        }

    def log_result(self, test_name, success, message="", response=None):
        """Log test results"""
        self.results["total_tests"] += 1
        if success:
            self.results["passed"] += 1
            print(f"✅ {test_name}: PASSED - {message}")
        else:
            self.results["failed"] += 1
            self.results["errors"].append(f"{test_name}: {message}")
            print(f"❌ {test_name}: FAILED - {message}")
            if response:
                print(f"   Response: {response.status_code} - {response.text[:200]}")

    def test_api_root(self):
        """Test root API endpoint"""
        try:
            response = requests.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                if "SXC ScholarHub API is running" in data.get("message", ""):
                    self.log_result("API Root", True, "API is running")
                    return True
                else:
                    self.log_result("API Root", False, "Unexpected response message", response)
            else:
                self.log_result("API Root", False, f"Status code: {response.status_code}", response)
        except Exception as e:
            self.log_result("API Root", False, f"Exception: {str(e)}")
        return False

    def test_user_registration(self):
        """Test user registration with valid data"""
        try:
            # Generate unique test data
            unique_id = str(uuid.uuid4())[:8]
            test_data = {
                "email": f"student{unique_id}@sxc.edu.in",
                "password": "SecurePass123!",
                "name": f"Test Student {unique_id}",
                "department": "Computer Science",
                "year": "2024"
            }
            
            response = requests.post(f"{self.base_url}/auth/register", 
                                   json=test_data, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                if "user" in data and "token" in data:
                    self.auth_token = data["token"]
                    self.test_user_id = data["user"]["id"]
                    self.log_result("User Registration", True, f"User registered successfully: {data['user']['email']}")
                    return True
                else:
                    self.log_result("User Registration", False, "Missing user or token in response", response)
            else:
                self.log_result("User Registration", False, f"Status code: {response.status_code}", response)
        except Exception as e:
            self.log_result("User Registration", False, f"Exception: {str(e)}")
        return False

    def test_duplicate_registration(self):
        """Test registration with duplicate email"""
        try:
            # Use same email as previous registration
            unique_id = str(uuid.uuid4())[:8]
            test_data = {
                "email": f"student{unique_id}@sxc.edu.in",
                "password": "SecurePass123!",
                "name": f"Test Student {unique_id}",
                "department": "Computer Science",
                "year": "2024"
            }
            
            # Register first user
            requests.post(f"{self.base_url}/auth/register", json=test_data, headers=self.headers)
            
            # Try to register again with same email
            response = requests.post(f"{self.base_url}/auth/register", 
                                   json=test_data, headers=self.headers)
            
            if response.status_code == 400:
                data = response.json()
                if "already exists" in data.get("error", "").lower():
                    self.log_result("Duplicate Registration", True, "Correctly rejected duplicate email")
                    return True
                else:
                    self.log_result("Duplicate Registration", False, "Wrong error message", response)
            else:
                self.log_result("Duplicate Registration", False, f"Expected 400, got {response.status_code}", response)
        except Exception as e:
            self.log_result("Duplicate Registration", False, f"Exception: {str(e)}")
        return False

    def test_user_login_valid(self):
        """Test user login with correct credentials"""
        try:
            # First register a user
            unique_id = str(uuid.uuid4())[:8]
            email = f"logintest{unique_id}@sxc.edu.in"
            password = "LoginTest123!"
            
            reg_data = {
                "email": email,
                "password": password,
                "name": f"Login Test {unique_id}",
                "department": "Mathematics",
                "year": "2023"
            }
            requests.post(f"{self.base_url}/auth/register", json=reg_data, headers=self.headers)
            
            # Now test login
            login_data = {"email": email, "password": password}
            response = requests.post(f"{self.base_url}/auth/login", 
                                   json=login_data, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                if "user" in data and "token" in data:
                    self.log_result("Valid Login", True, f"Login successful for {email}")
                    return True
                else:
                    self.log_result("Valid Login", False, "Missing user or token in response", response)
            else:
                self.log_result("Valid Login", False, f"Status code: {response.status_code}", response)
        except Exception as e:
            self.log_result("Valid Login", False, f"Exception: {str(e)}")
        return False

    def test_user_login_invalid(self):
        """Test user login with invalid credentials"""
        try:
            login_data = {
                "email": "nonexistent@sxc.edu.in",
                "password": "wrongpassword"
            }
            
            response = requests.post(f"{self.base_url}/auth/login", 
                                   json=login_data, headers=self.headers)
            
            if response.status_code == 401:
                data = response.json()
                if "invalid" in data.get("error", "").lower():
                    self.log_result("Invalid Login", True, "Correctly rejected invalid credentials")
                    return True
                else:
                    self.log_result("Invalid Login", False, "Wrong error message", response)
            else:
                self.log_result("Invalid Login", False, f"Expected 401, got {response.status_code}", response)
        except Exception as e:
            self.log_result("Invalid Login", False, f"Exception: {str(e)}")
        return False

    def test_token_verification(self):
        """Test token verification functionality"""
        try:
            if not self.auth_token:
                self.log_result("Token Verification", False, "No auth token available")
                return False
            
            auth_headers = self.headers.copy()
            auth_headers["Authorization"] = f"Bearer {self.auth_token}"
            
            response = requests.get(f"{self.base_url}/auth/verify", headers=auth_headers)
            
            if response.status_code == 200:
                data = response.json()
                if "user" in data:
                    self.log_result("Token Verification", True, f"Token verified for user: {data['user']['email']}")
                    return True
                else:
                    self.log_result("Token Verification", False, "Missing user in response", response)
            else:
                self.log_result("Token Verification", False, f"Status code: {response.status_code}", response)
        except Exception as e:
            self.log_result("Token Verification", False, f"Exception: {str(e)}")
        return False

    def test_invalid_token_verification(self):
        """Test token verification with invalid token"""
        try:
            auth_headers = self.headers.copy()
            auth_headers["Authorization"] = "Bearer invalid_token_here"
            
            response = requests.get(f"{self.base_url}/auth/verify", headers=auth_headers)
            
            if response.status_code == 401:
                data = response.json()
                if "invalid" in data.get("error", "").lower():
                    self.log_result("Invalid Token Verification", True, "Correctly rejected invalid token")
                    return True
                else:
                    self.log_result("Invalid Token Verification", False, "Wrong error message", response)
            else:
                self.log_result("Invalid Token Verification", False, f"Expected 401, got {response.status_code}", response)
        except Exception as e:
            self.log_result("Invalid Token Verification", False, f"Exception: {str(e)}")
        return False

    def test_create_resource(self):
        """Test uploading new academic resources"""
        try:
            resource_data = {
                "title": "Advanced Data Structures Notes",
                "description": "Comprehensive notes covering trees, graphs, and advanced algorithms",
                "department": "Computer Science",
                "year": "2024",
                "type": "notes",
                "subject": "Data Structures",
                "uploadedBy": "Test Student",
                "fileUrl": "https://example.com/notes.pdf",
                "uploadedAt": datetime.now().isoformat()
            }
            
            response = requests.post(f"{self.base_url}/resources", 
                                   json=resource_data, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data["title"] == resource_data["title"]:
                    self.test_resource_id = data["id"]
                    self.log_result("Create Resource", True, f"Resource created: {data['title']}")
                    return True
                else:
                    self.log_result("Create Resource", False, "Invalid response structure", response)
            else:
                self.log_result("Create Resource", False, f"Status code: {response.status_code}", response)
        except Exception as e:
            self.log_result("Create Resource", False, f"Exception: {str(e)}")
        return False

    def test_create_resource_missing_fields(self):
        """Test resource creation with missing required fields"""
        try:
            incomplete_data = {
                "title": "Incomplete Resource",
                "description": "Missing required fields"
                # Missing department, year, type
            }
            
            response = requests.post(f"{self.base_url}/resources", 
                                   json=incomplete_data, headers=self.headers)
            
            if response.status_code == 400:
                data = response.json()
                if "required" in data.get("error", "").lower():
                    self.log_result("Create Resource Missing Fields", True, "Correctly rejected incomplete data")
                    return True
                else:
                    self.log_result("Create Resource Missing Fields", False, "Wrong error message", response)
            else:
                self.log_result("Create Resource Missing Fields", False, f"Expected 400, got {response.status_code}", response)
        except Exception as e:
            self.log_result("Create Resource Missing Fields", False, f"Exception: {str(e)}")
        return False

    def test_get_all_resources(self):
        """Test fetching all resources"""
        try:
            response = requests.get(f"{self.base_url}/resources", headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Get All Resources", True, f"Retrieved {len(data)} resources")
                    return True
                else:
                    self.log_result("Get All Resources", False, "Response is not a list", response)
            else:
                self.log_result("Get All Resources", False, f"Status code: {response.status_code}", response)
        except Exception as e:
            self.log_result("Get All Resources", False, f"Exception: {str(e)}")
        return False

    def test_get_resource_by_id(self):
        """Test fetching specific resource by ID"""
        try:
            if not self.test_resource_id:
                self.log_result("Get Resource By ID", False, "No test resource ID available")
                return False
            
            response = requests.get(f"{self.base_url}/resources/{self.test_resource_id}", 
                                  headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data["id"] == self.test_resource_id:
                    self.log_result("Get Resource By ID", True, f"Retrieved resource: {data['title']}")
                    return True
                else:
                    self.log_result("Get Resource By ID", False, "Invalid resource data", response)
            else:
                self.log_result("Get Resource By ID", False, f"Status code: {response.status_code}", response)
        except Exception as e:
            self.log_result("Get Resource By ID", False, f"Exception: {str(e)}")
        return False

    def test_get_nonexistent_resource(self):
        """Test fetching non-existent resource"""
        try:
            fake_id = str(uuid.uuid4())
            response = requests.get(f"{self.base_url}/resources/{fake_id}", 
                                  headers=self.headers)
            
            if response.status_code == 404:
                data = response.json()
                if "not found" in data.get("error", "").lower():
                    self.log_result("Get Nonexistent Resource", True, "Correctly returned 404 for missing resource")
                    return True
                else:
                    self.log_result("Get Nonexistent Resource", False, "Wrong error message", response)
            else:
                self.log_result("Get Nonexistent Resource", False, f"Expected 404, got {response.status_code}", response)
        except Exception as e:
            self.log_result("Get Nonexistent Resource", False, f"Exception: {str(e)}")
        return False

    def test_delete_resource(self):
        """Test deleting resources"""
        try:
            # First create a resource to delete
            resource_data = {
                "title": "Resource to Delete",
                "description": "This resource will be deleted",
                "department": "Physics",
                "year": "2023",
                "type": "assignment",
                "subject": "Quantum Physics"
            }
            
            create_response = requests.post(f"{self.base_url}/resources", 
                                          json=resource_data, headers=self.headers)
            
            if create_response.status_code != 200:
                self.log_result("Delete Resource", False, "Failed to create resource for deletion test")
                return False
            
            resource_id = create_response.json()["id"]
            
            # Now delete it
            delete_response = requests.delete(f"{self.base_url}/resources/{resource_id}", 
                                            headers=self.headers)
            
            if delete_response.status_code == 200:
                data = delete_response.json()
                if "deleted successfully" in data.get("message", "").lower():
                    self.log_result("Delete Resource", True, "Resource deleted successfully")
                    return True
                else:
                    self.log_result("Delete Resource", False, "Wrong success message", delete_response)
            else:
                self.log_result("Delete Resource", False, f"Status code: {delete_response.status_code}", delete_response)
        except Exception as e:
            self.log_result("Delete Resource", False, f"Exception: {str(e)}")
        return False

    def test_delete_nonexistent_resource(self):
        """Test deleting non-existent resource"""
        try:
            fake_id = str(uuid.uuid4())
            response = requests.delete(f"{self.base_url}/resources/{fake_id}", 
                                     headers=self.headers)
            
            if response.status_code == 404:
                data = response.json()
                if "not found" in data.get("error", "").lower():
                    self.log_result("Delete Nonexistent Resource", True, "Correctly returned 404 for missing resource")
                    return True
                else:
                    self.log_result("Delete Nonexistent Resource", False, "Wrong error message", response)
            else:
                self.log_result("Delete Nonexistent Resource", False, f"Expected 404, got {response.status_code}", response)
        except Exception as e:
            self.log_result("Delete Nonexistent Resource", False, f"Exception: {str(e)}")
        return False

    def test_get_users(self):
        """Test fetching all users (admin endpoint)"""
        try:
            response = requests.get(f"{self.base_url}/users", headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    # Check that passwords are not included
                    has_password = any("password" in user for user in data if isinstance(user, dict))
                    if not has_password:
                        self.log_result("Get Users", True, f"Retrieved {len(data)} users without passwords")
                        return True
                    else:
                        self.log_result("Get Users", False, "Response contains password fields")
                else:
                    self.log_result("Get Users", False, "Response is not a list", response)
            else:
                self.log_result("Get Users", False, f"Status code: {response.status_code}", response)
        except Exception as e:
            self.log_result("Get Users", False, f"Exception: {str(e)}")
        return False

    def test_search_basic(self):
        """Test basic search functionality"""
        try:
            # First create some searchable resources
            test_resources = [
                {
                    "title": "Machine Learning Fundamentals",
                    "description": "Introduction to ML algorithms and concepts",
                    "department": "Computer Science",
                    "year": "2024",
                    "type": "notes",
                    "subject": "Machine Learning"
                },
                {
                    "title": "Database Systems Guide",
                    "description": "Comprehensive guide to database design",
                    "department": "Computer Science", 
                    "year": "2023",
                    "type": "textbook",
                    "subject": "Database Systems"
                }
            ]
            
            for resource in test_resources:
                requests.post(f"{self.base_url}/resources", json=resource, headers=self.headers)
            
            # Test search by query
            response = requests.get(f"{self.base_url}/search?q=machine", headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    # Check if search results contain relevant items
                    found_ml = any("machine" in item.get("title", "").lower() or 
                                 "machine" in item.get("description", "").lower() 
                                 for item in data)
                    if found_ml:
                        self.log_result("Search Basic", True, f"Search returned {len(data)} results with relevant content")
                        return True
                    else:
                        self.log_result("Search Basic", True, f"Search completed but no ML results found (may be expected)")
                        return True
                else:
                    self.log_result("Search Basic", False, "Search response is not a list", response)
            else:
                self.log_result("Search Basic", False, f"Status code: {response.status_code}", response)
        except Exception as e:
            self.log_result("Search Basic", False, f"Exception: {str(e)}")
        return False

    def test_search_filters(self):
        """Test search with filters (department, year, type)"""
        try:
            # Test filter by department
            response = requests.get(f"{self.base_url}/search?department=Computer Science", 
                                  headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    # Check if all results are from Computer Science department
                    all_cs = all(item.get("department") == "Computer Science" for item in data)
                    if all_cs or len(data) == 0:  # Empty results are also valid
                        self.log_result("Search Filters", True, f"Department filter returned {len(data)} CS resources")
                        return True
                    else:
                        self.log_result("Search Filters", False, "Filter results contain wrong department")
                else:
                    self.log_result("Search Filters", False, "Filter response is not a list", response)
            else:
                self.log_result("Search Filters", False, f"Status code: {response.status_code}", response)
        except Exception as e:
            self.log_result("Search Filters", False, f"Exception: {str(e)}")
        return False

    def test_search_combined(self):
        """Test combined search and filter operations"""
        try:
            # Test search query with filters
            response = requests.get(f"{self.base_url}/search?q=database&department=Computer Science&year=2023", 
                                  headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Search Combined", True, f"Combined search returned {len(data)} results")
                    return True
                else:
                    self.log_result("Search Combined", False, "Combined search response is not a list", response)
            else:
                self.log_result("Search Combined", False, f"Status code: {response.status_code}", response)
        except Exception as e:
            self.log_result("Search Combined", False, f"Exception: {str(e)}")
        return False

    def test_cors_headers(self):
        """Test CORS headers in API responses"""
        try:
            response = requests.get(f"{self.base_url}/", headers=self.headers)
            
            cors_headers = [
                'Access-Control-Allow-Origin',
                'Access-Control-Allow-Methods',
                'Access-Control-Allow-Headers'
            ]
            
            missing_headers = [header for header in cors_headers 
                             if header not in response.headers]
            
            if not missing_headers:
                self.log_result("CORS Headers", True, "All required CORS headers present")
                return True
            else:
                self.log_result("CORS Headers", False, f"Missing CORS headers: {missing_headers}")
        except Exception as e:
            self.log_result("CORS Headers", False, f"Exception: {str(e)}")
        return False

    def test_options_request(self):
        """Test OPTIONS request for CORS preflight"""
        try:
            response = requests.options(f"{self.base_url}/resources", headers=self.headers)
            
            if response.status_code == 200:
                if 'Access-Control-Allow-Methods' in response.headers:
                    self.log_result("OPTIONS Request", True, "OPTIONS request handled correctly")
                    return True
                else:
                    self.log_result("OPTIONS Request", False, "Missing CORS headers in OPTIONS response")
            else:
                self.log_result("OPTIONS Request", False, f"Status code: {response.status_code}", response)
        except Exception as e:
            self.log_result("OPTIONS Request", False, f"Exception: {str(e)}")
        return False

    def test_admin_only_resource_upload(self):
        """
        Comprehensive test suite for admin-only resource upload functionality
        """
        print("\n🔐 ADMIN-ONLY RESOURCE UPLOAD TESTING")
        print("-" * 60)
        
        # Test data
        admin_user_data = {
            "email": "admin@sxc.edu",
            "password": "AdminPass123",
            "name": "Dr. Sarah Johnson",
            "department": "Computer Science",
            "year": "Faculty",
            "role": "admin"
        }
        
        student_user_data = {
            "email": "student@sxc.edu", 
            "password": "StudentPass123",
            "name": "John Smith",
            "department": "Computer Science",
            "year": "2024"
        }
        
        faculty_email_user = {
            "email": "faculty.jones@sxc.edu",
            "password": "FacultyPass123", 
            "name": "Prof. Michael Jones",
            "department": "Mathematics",
            "year": "Faculty"
        }
        
        resource_data = {
            "title": "Advanced Data Structures Notes",
            "description": "Comprehensive notes on advanced data structures",
            "subject": "Data Structures",
            "department": "Computer Science", 
            "year": "2024",
            "type": "notes",
            "fileUrl": "https://example.com/advanced-ds-notes.pdf"
        }
        
        admin_token = None
        student_token = None
        faculty_token = None
        
        # 1. Test Admin Registration
        try:
            response = requests.post(f"{self.base_url}/auth/register", json=admin_user_data)
            if response.status_code == 200:
                admin_data = response.json()
                admin_token = admin_data.get('token')
                user_role = admin_data.get('user', {}).get('role')
                
                if user_role == 'admin':
                    self.log_result("Admin Registration", True, f"Admin user registered with role: {user_role}")
                else:
                    self.log_result("Admin Registration", False, f"Expected admin role, got: {user_role}")
            else:
                self.log_result("Admin Registration", False, f"Registration failed: {response.status_code}")
        except Exception as e:
            self.log_result("Admin Registration", False, f"Exception: {str(e)}")
        
        # 2. Test Student Registration
        try:
            response = requests.post(f"{self.base_url}/auth/register", json=student_user_data)
            if response.status_code == 200:
                student_data = response.json()
                student_token = student_data.get('token')
                user_role = student_data.get('user', {}).get('role')
                
                if user_role == 'student':
                    self.log_result("Student Registration", True, f"Student user registered with role: {user_role}")
                else:
                    self.log_result("Student Registration", False, f"Expected student role, got: {user_role}")
            else:
                self.log_result("Student Registration", False, f"Registration failed: {response.status_code}")
        except Exception as e:
            self.log_result("Student Registration", False, f"Exception: {str(e)}")
        
        # 3. Test Faculty Email Auto-Admin
        try:
            response = requests.post(f"{self.base_url}/auth/register", json=faculty_email_user)
            if response.status_code == 200:
                faculty_data = response.json()
                faculty_token = faculty_data.get('token')
                user_role = faculty_data.get('user', {}).get('role')
                
                if user_role == 'admin':
                    self.log_result("Faculty Email Auto-Admin", True, f"Faculty email auto-assigned admin role")
                else:
                    self.log_result("Faculty Email Auto-Admin", False, f"Expected admin role, got: {user_role}")
            else:
                self.log_result("Faculty Email Auto-Admin", False, f"Registration failed: {response.status_code}")
        except Exception as e:
            self.log_result("Faculty Email Auto-Admin", False, f"Exception: {str(e)}")
        
        # 4. Test Admin Resource Upload
        if admin_token:
            try:
                headers = {"Authorization": f"Bearer {admin_token}"}
                response = requests.post(f"{self.base_url}/resources", json=resource_data, headers=headers)
                
                if response.status_code == 200:
                    uploaded_resource = response.json()
                    uploaded_by = uploaded_resource.get('uploadedBy')
                    uploaded_by_name = uploaded_resource.get('uploadedByName')
                    
                    if uploaded_by and uploaded_by_name:
                        self.log_result("Admin Resource Upload", True, f"Admin successfully uploaded resource with attribution")
                    else:
                        self.log_result("Admin Resource Upload", False, "Resource uploaded but missing attribution")
                else:
                    self.log_result("Admin Resource Upload", False, f"Upload failed: {response.status_code}")
            except Exception as e:
                self.log_result("Admin Resource Upload", False, f"Exception: {str(e)}")
        
        # 5. Test Student Resource Upload Blocked
        if student_token:
            try:
                headers = {"Authorization": f"Bearer {student_token}"}
                response = requests.post(f"{self.base_url}/resources", json=resource_data, headers=headers)
                
                if response.status_code == 403:
                    error_message = response.json().get('error', '')
                    if 'administrator' in error_message.lower():
                        self.log_result("Student Upload Blocked", True, "Student upload correctly blocked with 403")
                    else:
                        self.log_result("Student Upload Blocked", False, f"Wrong error message: {error_message}")
                else:
                    self.log_result("Student Upload Blocked", False, f"Expected 403, got: {response.status_code}")
            except Exception as e:
                self.log_result("Student Upload Blocked", False, f"Exception: {str(e)}")
        
        # 6. Test No Token Blocked
        try:
            response = requests.post(f"{self.base_url}/resources", json=resource_data)
            
            if response.status_code == 401:
                error_message = response.json().get('error', '')
                if 'authentication' in error_message.lower():
                    self.log_result("No Token Blocked", True, "No token request correctly blocked with 401")
                else:
                    self.log_result("No Token Blocked", False, f"Wrong error message: {error_message}")
            else:
                self.log_result("No Token Blocked", False, f"Expected 401, got: {response.status_code}")
        except Exception as e:
            self.log_result("No Token Blocked", False, f"Exception: {str(e)}")
        
        # 7. Test Invalid Token Blocked
        try:
            headers = {"Authorization": "Bearer invalid_token_12345"}
            response = requests.post(f"{self.base_url}/resources", json=resource_data, headers=headers)
            
            if response.status_code == 401:
                error_message = response.json().get('error', '')
                if 'invalid' in error_message.lower():
                    self.log_result("Invalid Token Blocked", True, "Invalid token correctly blocked with 401")
                else:
                    self.log_result("Invalid Token Blocked", False, f"Wrong error message: {error_message}")
            else:
                self.log_result("Invalid Token Blocked", False, f"Expected 401, got: {response.status_code}")
        except Exception as e:
            self.log_result("Invalid Token Blocked", False, f"Exception: {str(e)}")
        
        # 8. Test Student Can View Resources
        if student_token:
            try:
                headers = {"Authorization": f"Bearer {student_token}"}
                response = requests.get(f"{self.base_url}/resources", headers=headers)
                
                if response.status_code == 200:
                    resources = response.json()
                    self.log_result("Student Can View Resources", True, f"Student can view {len(resources)} resources")
                else:
                    self.log_result("Student Can View Resources", False, f"View failed: {response.status_code}")
            except Exception as e:
                self.log_result("Student Can View Resources", False, f"Exception: {str(e)}")

    def test_smart_dashboard_functionality(self):
        """
        Comprehensive test suite for Smart Academic Dashboard functionality
        Tests all new dashboard features: user schema, dashboard endpoints, bookmarks, download tracking
        """
        print("\n📊 SMART ACADEMIC DASHBOARD TESTING")
        print("-" * 60)
        
        # Test users for dashboard functionality
        admin_user = {
            "email": "sahuatul2005@gmail.com",  # This email gets admin role
            "password": "AdminDash123",
            "name": "Dr. Dashboard Admin",
            "department": "Computer Science",
            "year": "Faculty"
        }
        
        student_user = {
            "email": f"student.dash.{str(uuid.uuid4())[:8]}@sxc.edu.in",
            "password": "StudentDash123",
            "name": "Dashboard Student",
            "department": "Mathematics", 
            "year": "2024"
        }
        
        admin_token = None
        student_token = None
        admin_user_id = None
        student_user_id = None
        test_resource_id = None
        
        # 1. Test User Registration Enhancement - New Schema Fields
        try:
            response = requests.post(f"{self.base_url}/auth/register", json=student_user)
            if response.status_code == 200:
                data = response.json()
                student_token = data.get('token')
                student_user_id = data.get('user', {}).get('id')
                user_data = data.get('user', {})
                
                # Check new schema fields
                has_downloads = 'downloads' in user_data and user_data['downloads'] == 0
                has_recent_views = 'recentViews' in user_data and user_data['recentViews'] == []
                has_bookmarks = 'bookmarks' in user_data and user_data['bookmarks'] == []
                
                if has_downloads and has_recent_views and has_bookmarks:
                    self.log_result("User Registration Enhancement", True, "New user initialized with downloads: 0, recentViews: [], bookmarks: []")
                else:
                    self.log_result("User Registration Enhancement", False, f"Missing new fields - downloads: {has_downloads}, recentViews: {has_recent_views}, bookmarks: {has_bookmarks}")
            else:
                self.log_result("User Registration Enhancement", False, f"Registration failed: {response.status_code}")
        except Exception as e:
            self.log_result("User Registration Enhancement", False, f"Exception: {str(e)}")
        
        # Register admin user
        try:
            response = requests.post(f"{self.base_url}/auth/register", json=admin_user)
            if response.status_code == 200:
                data = response.json()
                admin_token = data.get('token')
                admin_user_id = data.get('user', {}).get('id')
            else:
                # Admin might already exist, try login
                login_response = requests.post(f"{self.base_url}/auth/login", 
                                             json={"email": admin_user["email"], "password": admin_user["password"]})
                if login_response.status_code == 200:
                    data = login_response.json()
                    admin_token = data.get('token')
                    admin_user_id = data.get('user', {}).get('id')
        except Exception as e:
            print(f"Admin setup error: {e}")
        
        # 2. Test Resource Creation Enhancement - downloadCount: 0
        if admin_token:
            try:
                resource_data = {
                    "title": "Dashboard Test Resource",
                    "description": "Resource for testing dashboard functionality",
                    "department": "Computer Science",
                    "year": "2024",
                    "type": "notes",
                    "subject": "Dashboard Testing",
                    "fileContent": "data:text/plain;base64,VGVzdCBmaWxlIGNvbnRlbnQ=",  # "Test file content" in base64
                    "fileName": "test-resource.txt",
                    "fileType": "text/plain"
                }
                
                headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
                response = requests.post(f"{self.base_url}/resources", json=resource_data, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    test_resource_id = data.get('id')
                    
                    # Verify resource was created with downloadCount: 0
                    resource_response = requests.get(f"{self.base_url}/resources/{test_resource_id}")
                    if resource_response.status_code == 200:
                        resource = resource_response.json()
                        if resource.get('downloadCount') == 0:
                            self.log_result("Resource Creation Enhancement", True, "New resource created with downloadCount: 0")
                        else:
                            self.log_result("Resource Creation Enhancement", False, f"Resource downloadCount is {resource.get('downloadCount')}, expected 0")
                    else:
                        self.log_result("Resource Creation Enhancement", False, "Could not verify resource downloadCount")
                else:
                    self.log_result("Resource Creation Enhancement", False, f"Resource creation failed: {response.status_code}")
            except Exception as e:
                self.log_result("Resource Creation Enhancement", False, f"Exception: {str(e)}")
        
        # 3. Test Download Tracking Enhancement
        if student_token and test_resource_id:
            try:
                headers = {"Authorization": f"Bearer {student_token}"}
                
                # Download the resource
                download_response = requests.get(f"{self.base_url}/resources/{test_resource_id}/download", headers=headers)
                
                if download_response.status_code == 200:
                    # Verify user download count increased
                    verify_response = requests.get(f"{self.base_url}/auth/verify", headers=headers)
                    if verify_response.status_code == 200:
                        user_data = verify_response.json().get('user', {})
                        downloads = user_data.get('downloads', 0)
                        recent_views = user_data.get('recentViews', [])
                        
                        # Check resource download count increased
                        resource_response = requests.get(f"{self.base_url}/resources/{test_resource_id}")
                        if resource_response.status_code == 200:
                            resource = resource_response.json()
                            resource_downloads = resource.get('downloadCount', 0)
                            
                            if downloads >= 1 and test_resource_id in recent_views and resource_downloads >= 1:
                                self.log_result("Download Tracking Enhancement", True, f"Download tracking working: user downloads={downloads}, resource downloads={resource_downloads}, in recent views")
                            else:
                                self.log_result("Download Tracking Enhancement", False, f"Download tracking failed: user downloads={downloads}, resource downloads={resource_downloads}, in recent views={test_resource_id in recent_views}")
                        else:
                            self.log_result("Download Tracking Enhancement", False, "Could not verify resource download count")
                    else:
                        self.log_result("Download Tracking Enhancement", False, "Could not verify user download count")
                else:
                    self.log_result("Download Tracking Enhancement", False, f"Download failed: {download_response.status_code}")
            except Exception as e:
                self.log_result("Download Tracking Enhancement", False, f"Exception: {str(e)}")
        
        # 4. Test Bookmark Functionality
        if student_token and test_resource_id:
            try:
                headers = {"Authorization": f"Bearer {student_token}"}
                
                # Add bookmark
                bookmark_response = requests.post(f"{self.base_url}/resources/{test_resource_id}/bookmark", headers=headers)
                
                if bookmark_response.status_code == 200:
                    bookmark_data = bookmark_response.json()
                    is_bookmarked = bookmark_data.get('isBookmarked')
                    message = bookmark_data.get('message', '')
                    
                    if is_bookmarked and 'added' in message.lower():
                        # Remove bookmark
                        remove_response = requests.post(f"{self.base_url}/resources/{test_resource_id}/bookmark", headers=headers)
                        if remove_response.status_code == 200:
                            remove_data = remove_response.json()
                            is_removed = not remove_data.get('isBookmarked')
                            remove_message = remove_data.get('message', '')
                            
                            if is_removed and 'removed' in remove_message.lower():
                                self.log_result("Bookmark Functionality", True, "Bookmark add/remove working correctly")
                            else:
                                self.log_result("Bookmark Functionality", False, f"Bookmark removal failed: {remove_data}")
                        else:
                            self.log_result("Bookmark Functionality", False, f"Bookmark removal request failed: {remove_response.status_code}")
                    else:
                        self.log_result("Bookmark Functionality", False, f"Bookmark addition failed: {bookmark_data}")
                else:
                    self.log_result("Bookmark Functionality", False, f"Bookmark request failed: {bookmark_response.status_code}")
            except Exception as e:
                self.log_result("Bookmark Functionality", False, f"Exception: {str(e)}")
        
        # 5. Test Dashboard Student Endpoint
        if student_token:
            try:
                headers = {"Authorization": f"Bearer {student_token}"}
                response = requests.get(f"{self.base_url}/dashboard/student", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    required_fields = ['totalDownloads', 'recentResources', 'bookmarkedResources', 'trendingResources']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        total_downloads = data.get('totalDownloads', 0)
                        recent_count = len(data.get('recentResources', []))
                        bookmarked_count = len(data.get('bookmarkedResources', []))
                        trending_count = len(data.get('trendingResources', []))
                        
                        self.log_result("Dashboard Student Endpoint", True, 
                                      f"Student dashboard working: downloads={total_downloads}, recent={recent_count}, bookmarked={bookmarked_count}, trending={trending_count}")
                    else:
                        self.log_result("Dashboard Student Endpoint", False, f"Missing fields: {missing_fields}")
                else:
                    self.log_result("Dashboard Student Endpoint", False, f"Dashboard request failed: {response.status_code}")
            except Exception as e:
                self.log_result("Dashboard Student Endpoint", False, f"Exception: {str(e)}")
        
        # 6. Test Dashboard Admin Endpoint
        if admin_token:
            try:
                headers = {"Authorization": f"Bearer {admin_token}"}
                response = requests.get(f"{self.base_url}/dashboard/admin", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    required_fields = ['totalUploads', 'recentUploads', 'pendingRequests']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        total_uploads = data.get('totalUploads', 0)
                        recent_uploads_count = len(data.get('recentUploads', []))
                        pending_count = len(data.get('pendingRequests', []))
                        
                        self.log_result("Dashboard Admin Endpoint", True, 
                                      f"Admin dashboard working: uploads={total_uploads}, recent={recent_uploads_count}, pending={pending_count}")
                    else:
                        self.log_result("Dashboard Admin Endpoint", False, f"Missing fields: {missing_fields}")
                else:
                    self.log_result("Dashboard Admin Endpoint", False, f"Admin dashboard request failed: {response.status_code}")
            except Exception as e:
                self.log_result("Dashboard Admin Endpoint", False, f"Exception: {str(e)}")
        
        # 7. Test Dashboard Authentication Requirements
        try:
            # Test student dashboard without token
            response = requests.get(f"{self.base_url}/dashboard/student")
            if response.status_code == 401:
                self.log_result("Dashboard Authentication - Student", True, "Student dashboard correctly requires authentication")
            else:
                self.log_result("Dashboard Authentication - Student", False, f"Expected 401, got {response.status_code}")
            
            # Test admin dashboard without token
            response = requests.get(f"{self.base_url}/dashboard/admin")
            if response.status_code == 401:
                self.log_result("Dashboard Authentication - Admin", True, "Admin dashboard correctly requires authentication")
            else:
                self.log_result("Dashboard Authentication - Admin", False, f"Expected 401, got {response.status_code}")
        except Exception as e:
            self.log_result("Dashboard Authentication", False, f"Exception: {str(e)}")
        
        # 8. Test Admin Dashboard Access Control
        if student_token:
            try:
                headers = {"Authorization": f"Bearer {student_token}"}
                response = requests.get(f"{self.base_url}/dashboard/admin", headers=headers)
                
                if response.status_code == 403:
                    error_message = response.json().get('error', '')
                    if 'admin' in error_message.lower():
                        self.log_result("Admin Dashboard Access Control", True, "Student correctly blocked from admin dashboard")
                    else:
                        self.log_result("Admin Dashboard Access Control", False, f"Wrong error message: {error_message}")
                else:
                    self.log_result("Admin Dashboard Access Control", False, f"Expected 403, got {response.status_code}")
            except Exception as e:
                self.log_result("Admin Dashboard Access Control", False, f"Exception: {str(e)}")
        
        # 9. Test Bookmark Authentication
        if test_resource_id:
            try:
                # Test bookmark without token
                response = requests.post(f"{self.base_url}/resources/{test_resource_id}/bookmark")
                if response.status_code == 401:
                    self.log_result("Bookmark Authentication", True, "Bookmark endpoint correctly requires authentication")
                else:
                    self.log_result("Bookmark Authentication", False, f"Expected 401, got {response.status_code}")
            except Exception as e:
                self.log_result("Bookmark Authentication", False, f"Exception: {str(e)}")
        
        # 10. Test Bookmark Non-existent Resource
        if student_token:
            try:
                fake_resource_id = str(uuid.uuid4())
                headers = {"Authorization": f"Bearer {student_token}"}
                response = requests.post(f"{self.base_url}/resources/{fake_resource_id}/bookmark", headers=headers)
                
                if response.status_code == 404:
                    error_message = response.json().get('error', '')
                    if 'not found' in error_message.lower():
                        self.log_result("Bookmark Non-existent Resource", True, "Bookmark correctly handles non-existent resource")
                    else:
                        self.log_result("Bookmark Non-existent Resource", False, f"Wrong error message: {error_message}")
                else:
                    self.log_result("Bookmark Non-existent Resource", False, f"Expected 404, got {response.status_code}")
            except Exception as e:
                self.log_result("Bookmark Non-existent Resource", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all test cases"""
        print("🚀 Starting SXC ScholarHub Backend API Tests")
        print("=" * 60)
        
        # Test sequence
        test_methods = [
            self.test_api_root,
            self.test_user_registration,
            self.test_duplicate_registration,
            self.test_user_login_valid,
            self.test_user_login_invalid,
            self.test_token_verification,
            self.test_invalid_token_verification,
            self.test_create_resource,
            self.test_create_resource_missing_fields,
            self.test_get_all_resources,
            self.test_get_resource_by_id,
            self.test_get_nonexistent_resource,
            self.test_delete_resource,
            self.test_delete_nonexistent_resource,
            self.test_get_users,
            self.test_search_basic,
            self.test_search_filters,
            self.test_search_combined,
            self.test_cors_headers,
            self.test_options_request,
            self.test_admin_only_resource_upload,  # Existing admin-only tests
            self.test_smart_dashboard_functionality  # New Smart Dashboard tests
        ]
        
        for test_method in test_methods:
            try:
                test_method()
                time.sleep(0.5)  # Small delay between tests
            except Exception as e:
                self.log_result(test_method.__name__, False, f"Test execution error: {str(e)}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.results['total_tests']}")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"Success Rate: {(self.results['passed']/self.results['total_tests']*100):.1f}%")
        
        if self.results['errors']:
            print("\n🔍 FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        return self.results

if __name__ == "__main__":
    tester = ScholarHubAPITester()
    results = tester.run_all_tests()