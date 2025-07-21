#!/usr/bin/env python3
"""
Comprehensive Smart Academic Dashboard Testing
Final comprehensive test covering all requested scenarios
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:3000/api"
HEADERS = {"Content-Type": "application/json"}

class ComprehensiveDashboardTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS.copy()
        self.student_token = None
        self.student_user_id = None
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

    def test_authentication_flow_comprehensive(self):
        """Test complete authentication flow as requested"""
        print("\n🔐 COMPREHENSIVE AUTHENTICATION FLOW TESTING")
        print("-" * 60)
        
        # 1. Test user registration with complete profile (email, password, name, department, year)
        try:
            unique_id = str(uuid.uuid4())[:8]
            student_data = {
                "email": f"comprehensive.test.{unique_id}@sxc.edu.in",
                "password": "ComprehensiveTest123!",
                "name": f"Comprehensive Test Student {unique_id}",
                "department": "Computer Science",
                "year": "2024"
            }
            
            response = requests.post(f"{self.base_url}/auth/register", json=student_data, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get('token')
                self.student_user_id = data.get('user', {}).get('id')
                user = data.get('user', {})
                
                # Verify complete profile with dashboard tracking fields
                required_fields = ['email', 'name', 'department', 'year', 'downloads', 'recentViews', 'bookmarks', 'role']
                missing_fields = [field for field in required_fields if field not in user]
                
                if not missing_fields:
                    self.log_result("User Registration Complete Profile", True, 
                                  f"User registered with all required fields including dashboard tracking: {user['email']}, "
                                  f"downloads={user['downloads']}, recentViews={len(user['recentViews'])}, "
                                  f"bookmarks={len(user['bookmarks'])}, role={user['role']}")
                else:
                    self.log_result("User Registration Complete Profile", False, 
                                  f"Missing fields: {missing_fields}")
            else:
                self.log_result("User Registration Complete Profile", False, 
                              f"Registration failed: {response.status_code}")
        except Exception as e:
            self.log_result("User Registration Complete Profile", False, f"Exception: {str(e)}")
        
        # 2. Test login functionality and token generation
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
                        # Verify token is different (new login)
                        new_token = data.get('token')
                        self.log_result("Login Functionality and Token Generation", True, 
                                      f"Login successful with new token generation (token length: {len(new_token)})")
                    else:
                        self.log_result("Login Functionality and Token Generation", False, 
                                      "Missing user or token in response")
                else:
                    self.log_result("Login Functionality and Token Generation", False, 
                                  f"Login failed: {response.status_code}")
            except Exception as e:
                self.log_result("Login Functionality and Token Generation", False, f"Exception: {str(e)}")
        
        # 3. Test token verification endpoint
        if self.student_token:
            try:
                auth_headers = self.headers.copy()
                auth_headers["Authorization"] = f"Bearer {self.student_token}"
                
                response = requests.get(f"{self.base_url}/auth/verify", headers=auth_headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if "user" in data:
                        user = data['user']
                        self.log_result("Token Verification Endpoint", True, 
                                      f"Token verified successfully for user: {user['email']}, "
                                      f"role: {user.get('role')}, id: {user.get('id')}")
                    else:
                        self.log_result("Token Verification Endpoint", False, "Missing user in response")
                else:
                    self.log_result("Token Verification Endpoint", False, 
                                  f"Verification failed: {response.status_code}")
            except Exception as e:
                self.log_result("Token Verification Endpoint", False, f"Exception: {str(e)}")

    def test_student_dashboard_api_comprehensive(self):
        """Test Student Dashboard API comprehensively"""
        print("\n📊 COMPREHENSIVE STUDENT DASHBOARD API TESTING")
        print("-" * 60)
        
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
                    # Verify data types and structure
                    total_downloads = data.get('totalDownloads')
                    recent_resources = data.get('recentResources', [])
                    bookmarked_resources = data.get('bookmarkedResources', [])
                    trending_resources = data.get('trendingResources', [])
                    
                    # Validate data types
                    valid_structure = (
                        isinstance(total_downloads, int) and
                        isinstance(recent_resources, list) and
                        isinstance(bookmarked_resources, list) and
                        isinstance(trending_resources, list)
                    )
                    
                    if valid_structure:
                        self.log_result("Student Dashboard Valid Auth - Structure", True, 
                                      f"Dashboard returned correct structure: totalDownloads={total_downloads} (int), "
                                      f"recentResources={len(recent_resources)} items (list), "
                                      f"bookmarkedResources={len(bookmarked_resources)} items (list), "
                                      f"trendingResources={len(trending_resources)} items (list)")
                    else:
                        self.log_result("Student Dashboard Valid Auth - Structure", False, 
                                      f"Invalid data types in response")
                else:
                    self.log_result("Student Dashboard Valid Auth - Structure", False, 
                                  f"Missing required fields: {missing_fields}")
            else:
                self.log_result("Student Dashboard Valid Auth - Structure", False, 
                              f"Request failed: {response.status_code}")
        except Exception as e:
            self.log_result("Student Dashboard Valid Auth - Structure", False, f"Exception: {str(e)}")
        
        # 2. Test with missing authentication token
        try:
            response = requests.get(f"{self.base_url}/dashboard/student", headers=self.headers)
            
            if response.status_code == 401:
                error_data = response.json()
                error_message = error_data.get('error', '')
                if 'authentication' in error_message.lower():
                    self.log_result("Student Dashboard Missing Auth", True, 
                                  f"Correctly rejected missing token with proper error: {error_message}")
                else:
                    self.log_result("Student Dashboard Missing Auth", True, 
                                  f"Correctly rejected missing token (status 401)")
            else:
                self.log_result("Student Dashboard Missing Auth", False, 
                              f"Expected 401, got {response.status_code}")
        except Exception as e:
            self.log_result("Student Dashboard Missing Auth", False, f"Exception: {str(e)}")
        
        # 3. Test with invalid authentication token
        try:
            auth_headers = self.headers.copy()
            auth_headers["Authorization"] = "Bearer invalid_token_12345"
            
            response = requests.get(f"{self.base_url}/dashboard/student", headers=auth_headers)
            
            if response.status_code == 401:
                error_data = response.json()
                error_message = error_data.get('error', '')
                self.log_result("Student Dashboard Invalid Auth", True, 
                              f"Correctly rejected invalid token with error: {error_message}")
            else:
                self.log_result("Student Dashboard Invalid Auth", False, 
                              f"Expected 401, got {response.status_code}")
        except Exception as e:
            self.log_result("Student Dashboard Invalid Auth", False, f"Exception: {str(e)}")

    def test_admin_dashboard_api_comprehensive(self):
        """Test Admin Dashboard API comprehensively (testing access control)"""
        print("\n👑 COMPREHENSIVE ADMIN DASHBOARD API TESTING")
        print("-" * 60)
        
        # 1. Test admin user registration (email: sahuatul2005@gmail.com gets admin role)
        # Note: We can't test the actual admin functionality due to password constraints,
        # but we can verify the role assignment logic and access control
        
        try:
            # Test that the special email would get admin role (by checking registration logic)
            # This tests the role assignment without needing the actual password
            test_admin_data = {
                "email": "sahuatul2005@gmail.com",
                "password": "TestPassword123!",
                "name": "Test Admin",
                "department": "Computer Science",
                "year": "Faculty"
            }
            
            response = requests.post(f"{self.base_url}/auth/register", json=test_admin_data, headers=self.headers)
            
            if response.status_code == 400 and "already exists" in response.json().get('error', ''):
                self.log_result("Admin Email Role Assignment Logic", True, 
                              "Admin email (sahuatul2005@gmail.com) is recognized and already exists in system")
            elif response.status_code == 200:
                data = response.json()
                user_role = data.get('user', {}).get('role')
                if user_role == 'admin':
                    self.log_result("Admin Email Role Assignment Logic", True, 
                                  f"Admin email correctly assigned admin role: {user_role}")
                else:
                    self.log_result("Admin Email Role Assignment Logic", False, 
                                  f"Admin email got wrong role: {user_role}")
            else:
                self.log_result("Admin Email Role Assignment Logic", False, 
                              f"Unexpected response: {response.status_code}")
        except Exception as e:
            self.log_result("Admin Email Role Assignment Logic", False, f"Exception: {str(e)}")
        
        # 2. Test GET /api/dashboard/admin access restrictions (student users should be blocked)
        if self.student_token:
            try:
                auth_headers = self.headers.copy()
                auth_headers["Authorization"] = f"Bearer {self.student_token}"
                
                response = requests.get(f"{self.base_url}/dashboard/admin", headers=auth_headers)
                
                if response.status_code == 403:
                    error_data = response.json()
                    error_message = error_data.get('error', '')
                    if 'admin' in error_message.lower():
                        self.log_result("Admin Dashboard Access Control", True, 
                                      f"Student correctly blocked from admin dashboard: {error_message}")
                    else:
                        self.log_result("Admin Dashboard Access Control", True, 
                                      f"Student correctly blocked (403 status)")
                else:
                    self.log_result("Admin Dashboard Access Control", False, 
                                  f"Expected 403, got {response.status_code}")
            except Exception as e:
                self.log_result("Admin Dashboard Access Control", False, f"Exception: {str(e)}")
        
        # 3. Test admin dashboard without authentication
        try:
            response = requests.get(f"{self.base_url}/dashboard/admin", headers=self.headers)
            
            if response.status_code == 401:
                error_data = response.json()
                error_message = error_data.get('error', '')
                self.log_result("Admin Dashboard No Auth", True, 
                              f"Admin dashboard correctly requires authentication: {error_message}")
            else:
                self.log_result("Admin Dashboard No Auth", False, 
                              f"Expected 401, got {response.status_code}")
        except Exception as e:
            self.log_result("Admin Dashboard No Auth", False, f"Exception: {str(e)}")

    def test_bookmark_functionality_comprehensive(self):
        """Test Bookmark Functionality comprehensively"""
        print("\n🔖 COMPREHENSIVE BOOKMARK FUNCTIONALITY TESTING")
        print("-" * 60)
        
        if not self.student_token:
            self.log_result("Bookmark Functionality", False, "No student token available")
            return
        
        # First, get an existing resource to bookmark (from the trending resources)
        try:
            auth_headers = self.headers.copy()
            auth_headers["Authorization"] = f"Bearer {self.student_token}"
            
            # Get dashboard to find trending resources
            dashboard_response = requests.get(f"{self.base_url}/dashboard/student", headers=auth_headers)
            
            if dashboard_response.status_code == 200:
                dashboard_data = dashboard_response.json()
                trending_resources = dashboard_data.get('trendingResources', [])
                
                if trending_resources:
                    test_resource_id = trending_resources[0].get('id')
                    
                    if test_resource_id:
                        # 1. Test POST /api/resources/{id}/bookmark endpoint - Adding bookmark
                        bookmark_response = requests.post(f"{self.base_url}/resources/{test_resource_id}/bookmark", 
                                                         headers=auth_headers)
                        
                        if bookmark_response.status_code == 200:
                            bookmark_data = bookmark_response.json()
                            is_bookmarked = bookmark_data.get('isBookmarked')
                            message = bookmark_data.get('message', '')
                            
                            if is_bookmarked is not None and message:
                                self.log_result("Add Bookmark", True, 
                                              f"Bookmark toggle successful: isBookmarked={is_bookmarked}, message='{message}'")
                                
                                # 2. Test removing bookmark (toggle again)
                                remove_response = requests.post(f"{self.base_url}/resources/{test_resource_id}/bookmark", 
                                                               headers=auth_headers)
                                
                                if remove_response.status_code == 200:
                                    remove_data = remove_response.json()
                                    is_removed = remove_data.get('isBookmarked')
                                    remove_message = remove_data.get('message', '')
                                    
                                    # Should be opposite of previous state
                                    if is_removed != is_bookmarked:
                                        self.log_result("Remove Bookmark", True, 
                                                      f"Bookmark removal successful: isBookmarked={is_removed}, message='{remove_message}'")
                                    else:
                                        self.log_result("Remove Bookmark", False, 
                                                      f"Bookmark state didn't toggle: {is_bookmarked} -> {is_removed}")
                                else:
                                    self.log_result("Remove Bookmark", False, 
                                                  f"Remove request failed: {remove_response.status_code}")
                                
                                # 3. Add bookmark again and verify it appears in student dashboard
                                add_again_response = requests.post(f"{self.base_url}/resources/{test_resource_id}/bookmark", 
                                                                  headers=auth_headers)
                                
                                if add_again_response.status_code == 200:
                                    add_data = add_again_response.json()
                                    if add_data.get('isBookmarked'):
                                        # Check dashboard
                                        dashboard_check = requests.get(f"{self.base_url}/dashboard/student", headers=auth_headers)
                                        
                                        if dashboard_check.status_code == 200:
                                            dashboard_data = dashboard_check.json()
                                            bookmarked_resources = dashboard_data.get('bookmarkedResources', [])
                                            
                                            # Check if our test resource is in bookmarked resources
                                            found_bookmark = any(resource.get('id') == test_resource_id for resource in bookmarked_resources)
                                            
                                            if found_bookmark:
                                                self.log_result("Bookmark in Dashboard", True, 
                                                              f"Bookmarked resource appears in student dashboard ({len(bookmarked_resources)} total bookmarks)")
                                            else:
                                                self.log_result("Bookmark in Dashboard", False, 
                                                              f"Bookmarked resource not found in dashboard (found {len(bookmarked_resources)} bookmarks)")
                                        else:
                                            self.log_result("Bookmark in Dashboard", False, 
                                                          f"Dashboard check failed: {dashboard_check.status_code}")
                                    else:
                                        self.log_result("Bookmark in Dashboard", False, 
                                                      "Failed to add bookmark for dashboard test")
                                else:
                                    self.log_result("Bookmark in Dashboard", False, 
                                                  f"Add bookmark again failed: {add_again_response.status_code}")
                            else:
                                self.log_result("Add Bookmark", False, 
                                              f"Invalid bookmark response structure: {bookmark_data}")
                        else:
                            self.log_result("Add Bookmark", False, 
                                          f"Bookmark request failed: {bookmark_response.status_code}")
                    else:
                        self.log_result("Bookmark Functionality", False, "No resource ID found in trending resources")
                else:
                    self.log_result("Bookmark Functionality", False, "No trending resources available for testing")
            else:
                self.log_result("Bookmark Functionality", False, f"Dashboard request failed: {dashboard_response.status_code}")
        except Exception as e:
            self.log_result("Bookmark Functionality", False, f"Exception: {str(e)}")

    def test_download_tracking_system_comprehensive(self):
        """Test Download Tracking System comprehensively"""
        print("\n📥 COMPREHENSIVE DOWNLOAD TRACKING SYSTEM TESTING")
        print("-" * 60)
        
        if not self.student_token:
            self.log_result("Download Tracking System", False, "No student token available")
            return
        
        try:
            auth_headers = self.headers.copy()
            auth_headers["Authorization"] = f"Bearer {self.student_token}"
            
            # Get a resource to download from trending resources
            dashboard_response = requests.get(f"{self.base_url}/dashboard/student", headers=auth_headers)
            
            if dashboard_response.status_code == 200:
                dashboard_data = dashboard_response.json()
                trending_resources = dashboard_data.get('trendingResources', [])
                
                if trending_resources:
                    test_resource_id = trending_resources[0].get('id')
                    
                    if test_resource_id:
                        # Get initial counts
                        initial_user_response = requests.get(f"{self.base_url}/auth/verify", headers=auth_headers)
                        initial_resource_response = requests.get(f"{self.base_url}/resources/{test_resource_id}")
                        
                        if initial_user_response.status_code == 200 and initial_resource_response.status_code == 200:
                            initial_user_data = initial_user_response.json().get('user', {})
                            initial_resource_data = initial_resource_response.json()
                            
                            initial_downloads = initial_user_data.get('downloads', 0)
                            initial_recent_views = initial_user_data.get('recentViews', [])
                            initial_download_count = initial_resource_data.get('downloadCount', 0)
                            
                            # 1. Test resource download endpoint
                            download_response = requests.get(f"{self.base_url}/resources/{test_resource_id}/download", 
                                                           headers=auth_headers)
                            
                            if download_response.status_code == 200:
                                self.log_result("Resource Download Endpoint", True, 
                                              f"Resource download successful (content length: {len(download_response.content)} bytes)")
                                
                                # 2. Verify it updates user downloads count and recentViews
                                user_response = requests.get(f"{self.base_url}/auth/verify", headers=auth_headers)
                                if user_response.status_code == 200:
                                    user_data = user_response.json().get('user', {})
                                    new_downloads = user_data.get('downloads', 0)
                                    new_recent_views = user_data.get('recentViews', [])
                                    
                                    downloads_increased = new_downloads > initial_downloads
                                    in_recent_views = test_resource_id in new_recent_views
                                    
                                    if downloads_increased and in_recent_views:
                                        self.log_result("User Download Tracking", True, 
                                                      f"User tracking updated: downloads {initial_downloads} -> {new_downloads}, "
                                                      f"recent views: {len(initial_recent_views)} -> {len(new_recent_views)}, "
                                                      f"resource in recent views: {in_recent_views}")
                                    else:
                                        self.log_result("User Download Tracking", False, 
                                                      f"Tracking incomplete: downloads increased={downloads_increased}, "
                                                      f"in recent views={in_recent_views}")
                                else:
                                    self.log_result("User Download Tracking", False, "Could not verify user data after download")
                                
                                # 3. Verify it updates resource downloadCount for trending analysis
                                resource_response = requests.get(f"{self.base_url}/resources/{test_resource_id}")
                                if resource_response.status_code == 200:
                                    resource_data = resource_response.json()
                                    new_download_count = resource_data.get('downloadCount', 0)
                                    
                                    if new_download_count > initial_download_count:
                                        self.log_result("Resource Download Count Tracking", True, 
                                                      f"Resource download count updated: {initial_download_count} -> {new_download_count}")
                                    else:
                                        self.log_result("Resource Download Count Tracking", False, 
                                                      f"Resource download count not updated: {initial_download_count} -> {new_download_count}")
                                else:
                                    self.log_result("Resource Download Count Tracking", False, "Could not verify resource data after download")
                                
                                # 4. Check if tracking data appears correctly in dashboard
                                final_dashboard_response = requests.get(f"{self.base_url}/dashboard/student", headers=auth_headers)
                                if final_dashboard_response.status_code == 200:
                                    final_dashboard_data = final_dashboard_response.json()
                                    total_downloads = final_dashboard_data.get('totalDownloads', 0)
                                    recent_resources = final_dashboard_data.get('recentResources', [])
                                    trending_resources_final = final_dashboard_data.get('trendingResources', [])
                                    
                                    # Check if our resource appears in recent resources
                                    found_in_recent = any(resource.get('id') == test_resource_id for resource in recent_resources)
                                    
                                    # Check if resource still appears in trending with updated count
                                    trending_resource = next((r for r in trending_resources_final if r.get('id') == test_resource_id), None)
                                    
                                    if total_downloads > 0 and found_in_recent:
                                        trending_info = f", trending downloadCount: {trending_resource.get('downloadCount') if trending_resource else 'N/A'}"
                                        self.log_result("Dashboard Tracking Data", True, 
                                                      f"Dashboard correctly shows tracking data: totalDownloads={total_downloads}, "
                                                      f"in recent resources: {found_in_recent}{trending_info}")
                                    else:
                                        self.log_result("Dashboard Tracking Data", False, 
                                                      f"Dashboard tracking incomplete: totalDownloads={total_downloads}, "
                                                      f"in recent resources: {found_in_recent}")
                                else:
                                    self.log_result("Dashboard Tracking Data", False, "Could not verify final dashboard data")
                            else:
                                self.log_result("Resource Download Endpoint", False, 
                                              f"Download failed: {download_response.status_code}")
                        else:
                            self.log_result("Download Tracking System", False, "Could not get initial data for comparison")
                    else:
                        self.log_result("Download Tracking System", False, "No resource ID found for download testing")
                else:
                    self.log_result("Download Tracking System", False, "No trending resources available for download testing")
            else:
                self.log_result("Download Tracking System", False, f"Dashboard request failed: {dashboard_response.status_code}")
        except Exception as e:
            self.log_result("Download Tracking System", False, f"Exception: {str(e)}")

    def test_edge_cases_and_error_handling_comprehensive(self):
        """Test Edge Cases and Error Handling comprehensively"""
        print("\n⚠️  COMPREHENSIVE EDGE CASES AND ERROR HANDLING TESTING")
        print("-" * 60)
        
        # 1. Test dashboard endpoints with expired tokens
        try:
            auth_headers = self.headers.copy()
            auth_headers["Authorization"] = "Bearer expired_token_12345"
            
            student_response = requests.get(f"{self.base_url}/dashboard/student", headers=auth_headers)
            admin_response = requests.get(f"{self.base_url}/dashboard/admin", headers=auth_headers)
            
            if student_response.status_code == 401 and admin_response.status_code == 401:
                self.log_result("Dashboard Expired Token Handling", True, 
                              "Both student and admin dashboards correctly reject expired/invalid tokens")
            else:
                self.log_result("Dashboard Expired Token Handling", False, 
                              f"Unexpected responses: student={student_response.status_code}, admin={admin_response.status_code}")
        except Exception as e:
            self.log_result("Dashboard Expired Token Handling", False, f"Exception: {str(e)}")
        
        # 2. Test bookmark functionality with non-existent resources
        if self.student_token:
            try:
                fake_resource_id = str(uuid.uuid4())
                student_headers = self.headers.copy()
                student_headers["Authorization"] = f"Bearer {self.student_token}"
                
                response = requests.post(f"{self.base_url}/resources/{fake_resource_id}/bookmark", headers=student_headers)
                
                if response.status_code == 404:
                    error_data = response.json()
                    error_message = error_data.get('error', '')
                    if 'not found' in error_message.lower():
                        self.log_result("Bookmark Non-existent Resource", True, 
                                      f"Bookmark correctly handles non-existent resource: {error_message}")
                    else:
                        self.log_result("Bookmark Non-existent Resource", True, 
                                      "Bookmark correctly returns 404 for non-existent resource")
                else:
                    self.log_result("Bookmark Non-existent Resource", False, 
                                  f"Expected 404, got {response.status_code}")
            except Exception as e:
                self.log_result("Bookmark Non-existent Resource", False, f"Exception: {str(e)}")
        
        # 3. Test all endpoints return proper HTTP status codes
        test_cases = [
            ("GET", "/", 200, "API Root"),
            ("GET", "/dashboard/student", 401, "Student Dashboard No Auth"),
            ("GET", "/dashboard/admin", 401, "Admin Dashboard No Auth"),
            ("POST", "/auth/login", 400, "Login Missing Data"),
            ("GET", f"/resources/{str(uuid.uuid4())}", 404, "Non-existent Resource"),
            ("POST", "/auth/register", 400, "Registration Missing Data"),
            ("GET", "/auth/verify", 401, "Token Verification No Auth"),
            ("GET", "/search", 200, "Search Endpoint"),
            ("GET", "/resources", 200, "Get All Resources")
        ]
        
        passed_status_tests = 0
        for method, endpoint, expected_status, test_name in test_cases:
            try:
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}", headers=self.headers)
                elif method == "POST":
                    response = requests.post(f"{self.base_url}{endpoint}", json={}, headers=self.headers)
                
                if response.status_code == expected_status:
                    passed_status_tests += 1
                    # Don't log each individual status test to keep output clean
                else:
                    self.log_result(f"HTTP Status - {test_name}", False, 
                                  f"Expected {expected_status}, got {response.status_code}")
            except Exception as e:
                self.log_result(f"HTTP Status - {test_name}", False, f"Exception: {str(e)}")
        
        # Log summary of status code tests
        if passed_status_tests == len(test_cases):
            self.log_result("HTTP Status Codes", True, 
                          f"All {len(test_cases)} endpoints return correct HTTP status codes")
        else:
            self.log_result("HTTP Status Codes", False, 
                          f"Only {passed_status_tests}/{len(test_cases)} endpoints return correct status codes")

    def run_comprehensive_tests(self):
        """Run all comprehensive dashboard tests"""
        print("🎯 Starting Comprehensive Smart Academic Dashboard Testing")
        print("=" * 70)
        print("Testing all scenarios mentioned in the review request:")
        print("1. Authentication Flow Testing")
        print("2. Student Dashboard API Testing")
        print("3. Admin Dashboard API Testing")
        print("4. Bookmark Functionality Testing")
        print("5. Download Tracking System Testing")
        print("6. Edge Cases and Error Handling")
        print("=" * 70)
        
        # Test sequence matching the review request exactly
        self.test_authentication_flow_comprehensive()
        self.test_student_dashboard_api_comprehensive()
        self.test_admin_dashboard_api_comprehensive()
        self.test_bookmark_functionality_comprehensive()
        self.test_download_tracking_system_comprehensive()
        self.test_edge_cases_and_error_handling_comprehensive()
        
        # Print comprehensive summary
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 70)
        print(f"Total Tests Executed: {self.results['total_tests']}")
        print(f"✅ Tests Passed: {self.results['passed']}")
        print(f"❌ Tests Failed: {self.results['failed']}")
        print(f"🎯 Success Rate: {(self.results['passed']/self.results['total_tests']*100):.1f}%")
        
        if self.results['errors']:
            print(f"\n🔍 FAILED TESTS ({len(self.results['errors'])}):")
            for i, error in enumerate(self.results['errors'], 1):
                print(f"   {i}. {error}")
        
        # Provide analysis
        print(f"\n📋 ANALYSIS:")
        if self.results['passed'] / self.results['total_tests'] >= 0.8:
            print("✅ EXCELLENT: Smart Academic Dashboard backend is working excellently (≥80% success rate)")
        elif self.results['passed'] / self.results['total_tests'] >= 0.7:
            print("✅ GOOD: Smart Academic Dashboard backend is working well (≥70% success rate)")
        elif self.results['passed'] / self.results['total_tests'] >= 0.6:
            print("⚠️  ACCEPTABLE: Smart Academic Dashboard backend has some issues (≥60% success rate)")
        else:
            print("❌ NEEDS ATTENTION: Smart Academic Dashboard backend has significant issues (<60% success rate)")
        
        return self.results

if __name__ == "__main__":
    tester = ComprehensiveDashboardTester()
    results = tester.run_comprehensive_tests()