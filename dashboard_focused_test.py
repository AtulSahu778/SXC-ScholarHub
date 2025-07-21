#!/usr/bin/env python3
"""
Focused Smart Academic Dashboard Testing
Tests the specific scenarios mentioned in the review request
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:3000/api"
HEADERS = {"Content-Type": "application/json"}

class DashboardTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS.copy()
        self.admin_token = None
        self.student_token = None
        self.admin_user_id = None
        self.student_user_id = None
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

    def test_authentication_flow(self):
        """Test complete authentication flow as requested"""
        print("\n🔐 AUTHENTICATION FLOW TESTING")
        print("-" * 50)
        
        # 1. Test user registration with complete profile
        try:
            unique_id = str(uuid.uuid4())[:8]
            student_data = {
                "email": f"student.test.{unique_id}@sxc.edu.in",
                "password": "StudentPass123!",
                "name": f"Test Student {unique_id}",
                "department": "Computer Science",
                "year": "2024"
            }
            
            response = requests.post(f"{self.base_url}/auth/register", json=student_data, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get('token')
                self.student_user_id = data.get('user', {}).get('id')
                user = data.get('user', {})
                
                # Verify complete profile
                required_fields = ['email', 'name', 'department', 'year', 'downloads', 'recentViews', 'bookmarks']
                missing_fields = [field for field in required_fields if field not in user]
                
                if not missing_fields:
                    self.log_result("User Registration Complete Profile", True, 
                                  f"User registered with all required fields: {user['email']}")
                else:
                    self.log_result("User Registration Complete Profile", False, 
                                  f"Missing fields: {missing_fields}")
            else:
                self.log_result("User Registration Complete Profile", False, 
                              f"Registration failed: {response.status_code}")
        except Exception as e:
            self.log_result("User Registration Complete Profile", False, f"Exception: {str(e)}")
        
        # 2. Test admin registration with special email
        try:
            admin_data = {
                "email": "sahuatul2005@gmail.com",  # This email gets admin role
                "password": "AdminPass123!",
                "name": "Admin User",
                "department": "Computer Science",
                "year": "Faculty"
            }
            
            response = requests.post(f"{self.base_url}/auth/register", json=admin_data, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                self.admin_user_id = data.get('user', {}).get('id')
                user_role = data.get('user', {}).get('role')
                
                if user_role == 'admin':
                    self.log_result("Admin Registration", True, f"Admin user registered with role: {user_role}")
                else:
                    self.log_result("Admin Registration", False, f"Expected admin role, got: {user_role}")
            elif response.status_code == 400 and "already exists" in response.json().get('error', ''):
                # Admin already exists, try login
                login_response = requests.post(f"{self.base_url}/auth/login", 
                                             json={"email": admin_data["email"], "password": admin_data["password"]})
                if login_response.status_code == 200:
                    data = login_response.json()
                    self.admin_token = data.get('token')
                    self.admin_user_id = data.get('user', {}).get('id')
                    self.log_result("Admin Registration", True, "Admin user logged in (already existed)")
                else:
                    self.log_result("Admin Registration", False, "Admin login failed")
            else:
                self.log_result("Admin Registration", False, f"Registration failed: {response.status_code}")
        except Exception as e:
            self.log_result("Admin Registration", False, f"Exception: {str(e)}")
        
        # 3. Test login functionality and token generation
        if self.student_token:
            try:
                login_data = {
                    "email": student_data["email"],
                    "password": student_data["password"]
                }
                
                response = requests.post(f"{self.base_url}/auth/login", json=login_data, headers=self.headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if "user" in data and "token" in data:
                        self.log_result("Login Functionality", True, "Login successful with token generation")
                    else:
                        self.log_result("Login Functionality", False, "Missing user or token in response")
                else:
                    self.log_result("Login Functionality", False, f"Login failed: {response.status_code}")
            except Exception as e:
                self.log_result("Login Functionality", False, f"Exception: {str(e)}")
        
        # 4. Test token verification endpoint
        if self.student_token:
            try:
                auth_headers = self.headers.copy()
                auth_headers["Authorization"] = f"Bearer {self.student_token}"
                
                response = requests.get(f"{self.base_url}/auth/verify", headers=auth_headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if "user" in data:
                        self.log_result("Token Verification", True, f"Token verified for user: {data['user']['email']}")
                    else:
                        self.log_result("Token Verification", False, "Missing user in response")
                else:
                    self.log_result("Token Verification", False, f"Verification failed: {response.status_code}")
            except Exception as e:
                self.log_result("Token Verification", False, f"Exception: {str(e)}")

    def test_student_dashboard_api(self):
        """Test Student Dashboard API as requested"""
        print("\n📊 STUDENT DASHBOARD API TESTING")
        print("-" * 50)
        
        if not self.student_token:
            self.log_result("Student Dashboard API", False, "No student token available")
            return
        
        # 1. Test GET /api/dashboard/student with valid authentication
        try:
            auth_headers = self.headers.copy()
            auth_headers["Authorization"] = f"Bearer {self.student_token}"
            
            response = requests.get(f"{self.base_url}/dashboard/student", headers=auth_headers)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['totalDownloads', 'recentResources', 'bookmarkedResources', 'trendingResources']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    self.log_result("Student Dashboard Valid Auth", True, 
                                  f"Dashboard returned all required fields: totalDownloads={data.get('totalDownloads')}, "
                                  f"recent={len(data.get('recentResources', []))}, "
                                  f"bookmarked={len(data.get('bookmarkedResources', []))}, "
                                  f"trending={len(data.get('trendingResources', []))}")
                else:
                    self.log_result("Student Dashboard Valid Auth", False, f"Missing fields: {missing_fields}")
            else:
                self.log_result("Student Dashboard Valid Auth", False, f"Request failed: {response.status_code}")
        except Exception as e:
            self.log_result("Student Dashboard Valid Auth", False, f"Exception: {str(e)}")
        
        # 2. Test with missing authentication token
        try:
            response = requests.get(f"{self.base_url}/dashboard/student", headers=self.headers)
            
            if response.status_code == 401:
                self.log_result("Student Dashboard Missing Auth", True, "Correctly rejected missing token")
            else:
                self.log_result("Student Dashboard Missing Auth", False, f"Expected 401, got {response.status_code}")
        except Exception as e:
            self.log_result("Student Dashboard Missing Auth", False, f"Exception: {str(e)}")
        
        # 3. Test with invalid authentication token
        try:
            auth_headers = self.headers.copy()
            auth_headers["Authorization"] = "Bearer invalid_token_12345"
            
            response = requests.get(f"{self.base_url}/dashboard/student", headers=auth_headers)
            
            if response.status_code == 401:
                self.log_result("Student Dashboard Invalid Auth", True, "Correctly rejected invalid token")
            else:
                self.log_result("Student Dashboard Invalid Auth", False, f"Expected 401, got {response.status_code}")
        except Exception as e:
            self.log_result("Student Dashboard Invalid Auth", False, f"Exception: {str(e)}")

    def test_admin_dashboard_api(self):
        """Test Admin Dashboard API as requested"""
        print("\n👑 ADMIN DASHBOARD API TESTING")
        print("-" * 50)
        
        if not self.admin_token:
            self.log_result("Admin Dashboard API", False, "No admin token available")
            return
        
        # 1. Test GET /api/dashboard/admin with admin authentication
        try:
            auth_headers = self.headers.copy()
            auth_headers["Authorization"] = f"Bearer {self.admin_token}"
            
            response = requests.get(f"{self.base_url}/dashboard/admin", headers=auth_headers)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['totalUploads', 'recentUploads', 'pendingRequests']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    self.log_result("Admin Dashboard Valid Auth", True, 
                                  f"Admin dashboard returned all required fields: totalUploads={data.get('totalUploads')}, "
                                  f"recentUploads={len(data.get('recentUploads', []))}, "
                                  f"pendingRequests={len(data.get('pendingRequests', []))}")
                else:
                    self.log_result("Admin Dashboard Valid Auth", False, f"Missing fields: {missing_fields}")
            else:
                self.log_result("Admin Dashboard Valid Auth", False, f"Request failed: {response.status_code}")
        except Exception as e:
            self.log_result("Admin Dashboard Valid Auth", False, f"Exception: {str(e)}")
        
        # 2. Test access restrictions (student users should be blocked)
        if self.student_token:
            try:
                auth_headers = self.headers.copy()
                auth_headers["Authorization"] = f"Bearer {self.student_token}"
                
                response = requests.get(f"{self.base_url}/dashboard/admin", headers=auth_headers)
                
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

    def test_bookmark_functionality(self):
        """Test Bookmark Functionality as requested"""
        print("\n🔖 BOOKMARK FUNCTIONALITY TESTING")
        print("-" * 50)
        
        if not self.student_token or not self.admin_token:
            self.log_result("Bookmark Functionality", False, "Missing required tokens")
            return
        
        # First create a test resource
        try:
            resource_data = {
                "title": "Bookmark Test Resource",
                "description": "Resource for testing bookmark functionality",
                "department": "Computer Science",
                "year": "2024",
                "type": "notes",
                "subject": "Testing",
                "fileContent": "data:text/plain;base64,VGVzdCBmaWxlIGNvbnRlbnQ=",  # "Test file content" in base64
                "fileName": "bookmark-test.txt",
                "fileType": "text/plain"
            }
            
            admin_headers = self.headers.copy()
            admin_headers["Authorization"] = f"Bearer {self.admin_token}"
            
            response = requests.post(f"{self.base_url}/resources", json=resource_data, headers=admin_headers)
            
            if response.status_code == 200:
                self.test_resource_id = response.json().get('id')
                self.log_result("Create Test Resource for Bookmark", True, f"Resource created: {self.test_resource_id}")
            else:
                self.log_result("Create Test Resource for Bookmark", False, f"Resource creation failed: {response.status_code}")
                return
        except Exception as e:
            self.log_result("Create Test Resource for Bookmark", False, f"Exception: {str(e)}")
            return
        
        # 1. Test POST /api/resources/{id}/bookmark endpoint - Adding bookmark
        try:
            student_headers = self.headers.copy()
            student_headers["Authorization"] = f"Bearer {self.student_token}"
            
            response = requests.post(f"{self.base_url}/resources/{self.test_resource_id}/bookmark", headers=student_headers)
            
            if response.status_code == 200:
                data = response.json()
                is_bookmarked = data.get('isBookmarked')
                message = data.get('message', '')
                
                if is_bookmarked and 'added' in message.lower():
                    self.log_result("Add Bookmark", True, f"Bookmark added successfully: {message}")
                else:
                    self.log_result("Add Bookmark", False, f"Unexpected response: {data}")
            else:
                self.log_result("Add Bookmark", False, f"Request failed: {response.status_code}")
        except Exception as e:
            self.log_result("Add Bookmark", False, f"Exception: {str(e)}")
        
        # 2. Test removing bookmark
        try:
            response = requests.post(f"{self.base_url}/resources/{self.test_resource_id}/bookmark", headers=student_headers)
            
            if response.status_code == 200:
                data = response.json()
                is_bookmarked = data.get('isBookmarked')
                message = data.get('message', '')
                
                if not is_bookmarked and 'removed' in message.lower():
                    self.log_result("Remove Bookmark", True, f"Bookmark removed successfully: {message}")
                else:
                    self.log_result("Remove Bookmark", False, f"Unexpected response: {data}")
            else:
                self.log_result("Remove Bookmark", False, f"Request failed: {response.status_code}")
        except Exception as e:
            self.log_result("Remove Bookmark", False, f"Exception: {str(e)}")
        
        # 3. Verify bookmarked resources appear in student dashboard
        try:
            # Add bookmark again
            requests.post(f"{self.base_url}/resources/{self.test_resource_id}/bookmark", headers=student_headers)
            
            # Check dashboard
            dashboard_response = requests.get(f"{self.base_url}/dashboard/student", headers=student_headers)
            
            if dashboard_response.status_code == 200:
                dashboard_data = dashboard_response.json()
                bookmarked_resources = dashboard_data.get('bookmarkedResources', [])
                
                # Check if our test resource is in bookmarked resources
                found_bookmark = any(resource.get('id') == self.test_resource_id for resource in bookmarked_resources)
                
                if found_bookmark:
                    self.log_result("Bookmark in Dashboard", True, "Bookmarked resource appears in student dashboard")
                else:
                    self.log_result("Bookmark in Dashboard", False, "Bookmarked resource not found in dashboard")
            else:
                self.log_result("Bookmark in Dashboard", False, f"Dashboard request failed: {dashboard_response.status_code}")
        except Exception as e:
            self.log_result("Bookmark in Dashboard", False, f"Exception: {str(e)}")

    def test_download_tracking_system(self):
        """Test Download Tracking System as requested"""
        print("\n📥 DOWNLOAD TRACKING SYSTEM TESTING")
        print("-" * 50)
        
        if not self.student_token or not self.test_resource_id:
            self.log_result("Download Tracking System", False, "Missing required tokens or resource ID")
            return
        
        # 1. Test resource download endpoint
        try:
            student_headers = self.headers.copy()
            student_headers["Authorization"] = f"Bearer {self.student_token}"
            
            # Get initial counts
            initial_user_response = requests.get(f"{self.base_url}/auth/verify", headers=student_headers)
            initial_user_data = initial_user_response.json().get('user', {})
            initial_downloads = initial_user_data.get('downloads', 0)
            initial_recent_views = initial_user_data.get('recentViews', [])
            
            initial_resource_response = requests.get(f"{self.base_url}/resources/{self.test_resource_id}")
            initial_resource_data = initial_resource_response.json()
            initial_download_count = initial_resource_data.get('downloadCount', 0)
            
            # Download the resource
            download_response = requests.get(f"{self.base_url}/resources/{self.test_resource_id}/download", headers=student_headers)
            
            if download_response.status_code == 200:
                self.log_result("Resource Download Endpoint", True, "Resource download successful")
                
                # 2. Verify it updates user downloads count and recentViews
                user_response = requests.get(f"{self.base_url}/auth/verify", headers=student_headers)
                if user_response.status_code == 200:
                    user_data = user_response.json().get('user', {})
                    new_downloads = user_data.get('downloads', 0)
                    new_recent_views = user_data.get('recentViews', [])
                    
                    if new_downloads > initial_downloads and self.test_resource_id in new_recent_views:
                        self.log_result("User Download Tracking", True, 
                                      f"User download count increased from {initial_downloads} to {new_downloads}, "
                                      f"resource added to recent views")
                    else:
                        self.log_result("User Download Tracking", False, 
                                      f"Download count: {initial_downloads} -> {new_downloads}, "
                                      f"In recent views: {self.test_resource_id in new_recent_views}")
                else:
                    self.log_result("User Download Tracking", False, "Could not verify user data")
                
                # 3. Verify it updates resource downloadCount for trending analysis
                resource_response = requests.get(f"{self.base_url}/resources/{self.test_resource_id}")
                if resource_response.status_code == 200:
                    resource_data = resource_response.json()
                    new_download_count = resource_data.get('downloadCount', 0)
                    
                    if new_download_count > initial_download_count:
                        self.log_result("Resource Download Count Tracking", True, 
                                      f"Resource download count increased from {initial_download_count} to {new_download_count}")
                    else:
                        self.log_result("Resource Download Count Tracking", False, 
                                      f"Download count unchanged: {initial_download_count} -> {new_download_count}")
                else:
                    self.log_result("Resource Download Count Tracking", False, "Could not verify resource data")
                
                # 4. Check if tracking data appears correctly in dashboard
                dashboard_response = requests.get(f"{self.base_url}/dashboard/student", headers=student_headers)
                if dashboard_response.status_code == 200:
                    dashboard_data = dashboard_response.json()
                    total_downloads = dashboard_data.get('totalDownloads', 0)
                    recent_resources = dashboard_data.get('recentResources', [])
                    trending_resources = dashboard_data.get('trendingResources', [])
                    
                    # Check if our resource appears in recent resources
                    found_in_recent = any(resource.get('id') == self.test_resource_id for resource in recent_resources)
                    
                    # Check if resource appears in trending (should have download count > 0)
                    found_in_trending = any(resource.get('id') == self.test_resource_id for resource in trending_resources)
                    
                    if total_downloads > 0 and found_in_recent:
                        self.log_result("Dashboard Tracking Data", True, 
                                      f"Dashboard shows correct tracking: totalDownloads={total_downloads}, "
                                      f"in recent={found_in_recent}, in trending={found_in_trending}")
                    else:
                        self.log_result("Dashboard Tracking Data", False, 
                                      f"Dashboard tracking incomplete: totalDownloads={total_downloads}, "
                                      f"in recent={found_in_recent}")
                else:
                    self.log_result("Dashboard Tracking Data", False, "Could not verify dashboard data")
            else:
                self.log_result("Resource Download Endpoint", False, f"Download failed: {download_response.status_code}")
        except Exception as e:
            self.log_result("Download Tracking System", False, f"Exception: {str(e)}")

    def test_edge_cases_and_error_handling(self):
        """Test Edge Cases and Error Handling as requested"""
        print("\n⚠️  EDGE CASES AND ERROR HANDLING TESTING")
        print("-" * 50)
        
        # 1. Test dashboard endpoints with expired tokens (simulate with invalid token)
        try:
            auth_headers = self.headers.copy()
            auth_headers["Authorization"] = "Bearer expired_token_12345"
            
            response = requests.get(f"{self.base_url}/dashboard/student", headers=auth_headers)
            
            if response.status_code == 401:
                self.log_result("Dashboard Expired Token", True, "Dashboard correctly rejects expired/invalid tokens")
            else:
                self.log_result("Dashboard Expired Token", False, f"Expected 401, got {response.status_code}")
        except Exception as e:
            self.log_result("Dashboard Expired Token", False, f"Exception: {str(e)}")
        
        # 2. Test bookmark functionality with non-existent resources
        if self.student_token:
            try:
                fake_resource_id = str(uuid.uuid4())
                student_headers = self.headers.copy()
                student_headers["Authorization"] = f"Bearer {self.student_token}"
                
                response = requests.post(f"{self.base_url}/resources/{fake_resource_id}/bookmark", headers=student_headers)
                
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
        
        # 3. Test all endpoints return proper HTTP status codes
        test_cases = [
            ("GET", "/", 200, "API Root"),
            ("GET", "/dashboard/student", 401, "Student Dashboard No Auth"),
            ("GET", "/dashboard/admin", 401, "Admin Dashboard No Auth"),
            ("POST", "/auth/login", 400, "Login Missing Data"),
            ("GET", f"/resources/{str(uuid.uuid4())}", 404, "Non-existent Resource")
        ]
        
        for method, endpoint, expected_status, test_name in test_cases:
            try:
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}", headers=self.headers)
                elif method == "POST":
                    response = requests.post(f"{self.base_url}{endpoint}", json={}, headers=self.headers)
                
                if response.status_code == expected_status:
                    self.log_result(f"HTTP Status - {test_name}", True, f"Correct status code: {response.status_code}")
                else:
                    self.log_result(f"HTTP Status - {test_name}", False, f"Expected {expected_status}, got {response.status_code}")
            except Exception as e:
                self.log_result(f"HTTP Status - {test_name}", False, f"Exception: {str(e)}")

    def run_focused_tests(self):
        """Run all focused dashboard tests"""
        print("🎯 Starting Focused Smart Academic Dashboard Tests")
        print("=" * 60)
        
        # Test sequence matching the review request
        self.test_authentication_flow()
        self.test_student_dashboard_api()
        self.test_admin_dashboard_api()
        self.test_bookmark_functionality()
        self.test_download_tracking_system()
        self.test_edge_cases_and_error_handling()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 FOCUSED TEST SUMMARY")
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
    tester = DashboardTester()
    results = tester.run_focused_tests()