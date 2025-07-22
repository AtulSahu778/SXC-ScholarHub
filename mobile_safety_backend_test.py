#!/usr/bin/env python3
"""
Mobile Safety Backend Integration Test for SXC ScholarHub
Tests that mobile safety improvements haven't broken backend API integration

This test specifically validates:
1. User authentication (login/register) with mobile-safe token handling
2. Dashboard API endpoints with timeout handling
3. Bookmark functionality with mobile error handling
4. All existing functionality to ensure no regressions

Focus: Ensure mobile safety improvements don't break backend integration
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Configuration - Use localhost for internal testing
BASE_URL = "http://localhost:3000/api"
HEADERS = {"Content-Type": "application/json"}

class MobileSafetyBackendTester:
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

    def test_api_connectivity(self):
        """Test basic API connectivity after mobile safety changes"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "SXC ScholarHub API is running" in data.get("message", ""):
                    self.log_result("API Connectivity", True, "API is accessible and running")
                    return True
                else:
                    self.log_result("API Connectivity", False, "Unexpected API response", response)
            else:
                self.log_result("API Connectivity", False, f"Status code: {response.status_code}", response)
        except Exception as e:
            self.log_result("API Connectivity", False, f"Connection error: {str(e)}")
        return False

    def test_mobile_safe_user_registration(self):
        """Test user registration with mobile-safe token handling"""
        try:
            # Generate unique test data
            unique_id = str(uuid.uuid4())[:8]
            test_data = {
                "email": f"mobile.test.{unique_id}@sxc.edu.in",
                "password": "MobileTest123!",
                "name": f"Mobile Test User {unique_id}",
                "department": "Computer Science",
                "year": "Third Year"
            }
            
            response = requests.post(f"{self.base_url}/auth/register", 
                                   json=test_data, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if "user" in data and "token" in data:
                    # Verify user has dashboard tracking fields (mobile safety requirement)
                    user = data["user"]
                    has_downloads = "downloads" in user and user["downloads"] == 0
                    has_recent_views = "recentViews" in user and isinstance(user["recentViews"], list)
                    has_bookmarks = "bookmarks" in user and isinstance(user["bookmarks"], list)
                    
                    if has_downloads and has_recent_views and has_bookmarks:
                        self.auth_token = data["token"]
                        self.test_user_id = user["id"]
                        self.log_result("Mobile Safe User Registration", True, 
                                      f"User registered with dashboard fields: downloads={user['downloads']}, recentViews=[], bookmarks=[]")
                        return True
                    else:
                        self.log_result("Mobile Safe User Registration", False, 
                                      f"Missing dashboard fields - downloads: {has_downloads}, recentViews: {has_recent_views}, bookmarks: {has_bookmarks}")
                else:
                    self.log_result("Mobile Safe User Registration", False, "Missing user or token in response", response)
            else:
                self.log_result("Mobile Safe User Registration", False, f"Status code: {response.status_code}", response)
        except Exception as e:
            self.log_result("Mobile Safe User Registration", False, f"Exception: {str(e)}")
        return False

    def test_mobile_safe_user_login(self):
        """Test user login with mobile-safe token handling"""
        try:
            # First register a user for login test
            unique_id = str(uuid.uuid4())[:8]
            email = f"mobile.login.{unique_id}@sxc.edu.in"
            password = "MobileLogin123!"
            
            reg_data = {
                "email": email,
                "password": password,
                "name": f"Mobile Login Test {unique_id}",
                "department": "Mathematics",
                "year": "Second Year"
            }
            requests.post(f"{self.base_url}/auth/register", json=reg_data, headers=self.headers, timeout=15)
            
            # Now test login
            login_data = {"email": email, "password": password}
            response = requests.post(f"{self.base_url}/auth/login", 
                                   json=login_data, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if "user" in data and "token" in data:
                    # Verify token format is compatible with mobile-safe storage
                    token = data["token"]
                    if len(token) > 50 and isinstance(token, str):  # Basic token validation
                        self.log_result("Mobile Safe User Login", True, 
                                      f"Login successful with token length: {len(token)}")
                        return True
                    else:
                        self.log_result("Mobile Safe User Login", False, f"Invalid token format: {token[:20]}...")
                else:
                    self.log_result("Mobile Safe User Login", False, "Missing user or token in response", response)
            else:
                self.log_result("Mobile Safe User Login", False, f"Status code: {response.status_code}", response)
        except Exception as e:
            self.log_result("Mobile Safe User Login", False, f"Exception: {str(e)}")
        return False

    def test_token_verification_with_mobile_safety(self):
        """Test token verification with mobile safety improvements"""
        try:
            if not self.auth_token:
                self.log_result("Token Verification Mobile Safety", False, "No auth token available")
                return False
            
            auth_headers = self.headers.copy()
            auth_headers["Authorization"] = f"Bearer {self.auth_token}"
            
            # Test with mobile-appropriate timeout
            response = requests.get(f"{self.base_url}/auth/verify", headers=auth_headers, timeout=12)
            
            if response.status_code == 200:
                data = response.json()
                if "user" in data:
                    user = data["user"]
                    # Verify user data structure is compatible with mobile safety
                    required_fields = ["id", "email", "name", "role", "downloads", "recentViews", "bookmarks"]
                    missing_fields = [field for field in required_fields if field not in user]
                    
                    if not missing_fields:
                        self.log_result("Token Verification Mobile Safety", True, 
                                      f"Token verified with complete user data: {user['email']}")
                        return True
                    else:
                        self.log_result("Token Verification Mobile Safety", False, 
                                      f"Missing user fields: {missing_fields}")
                else:
                    self.log_result("Token Verification Mobile Safety", False, "Missing user in response", response)
            else:
                self.log_result("Token Verification Mobile Safety", False, f"Status code: {response.status_code}", response)
        except Exception as e:
            self.log_result("Token Verification Mobile Safety", False, f"Exception: {str(e)}")
        return False

    def test_dashboard_api_with_timeout_handling(self):
        """Test dashboard API endpoints with mobile timeout handling"""
        try:
            if not self.auth_token:
                self.log_result("Dashboard API Timeout Handling", False, "No auth token available")
                return False
            
            auth_headers = self.headers.copy()
            auth_headers["Authorization"] = f"Bearer {self.auth_token}"
            
            # Test student dashboard with mobile timeout (10 seconds as per mobile implementation)
            response = requests.get(f"{self.base_url}/dashboard/student", 
                                  headers=auth_headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["totalDownloads", "recentResources", "bookmarkedResources", "trendingResources"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    self.log_result("Dashboard API Timeout Handling", True, 
                                  f"Student dashboard API working with timeout handling: downloads={data['totalDownloads']}")
                    return True
                else:
                    self.log_result("Dashboard API Timeout Handling", False, 
                                  f"Missing dashboard fields: {missing_fields}")
            else:
                self.log_result("Dashboard API Timeout Handling", False, f"Status code: {response.status_code}", response)
        except requests.exceptions.Timeout:
            self.log_result("Dashboard API Timeout Handling", False, "Request timed out (expected for mobile timeout test)")
        except Exception as e:
            self.log_result("Dashboard API Timeout Handling", False, f"Exception: {str(e)}")
        return False

    def test_bookmark_functionality_with_mobile_error_handling(self):
        """Test bookmark functionality with mobile error handling"""
        try:
            if not self.auth_token:
                self.log_result("Bookmark Mobile Error Handling", False, "No auth token available")
                return False
            
            # First create a test resource for bookmarking
            admin_token = self.create_admin_user()
            if not admin_token:
                self.log_result("Bookmark Mobile Error Handling", False, "Could not create admin user for test resource")
                return False
            
            resource_id = self.create_test_resource(admin_token)
            if not resource_id:
                self.log_result("Bookmark Mobile Error Handling", False, "Could not create test resource")
                return False
            
            auth_headers = self.headers.copy()
            auth_headers["Authorization"] = f"Bearer {self.auth_token}"
            
            # Test bookmark with mobile timeout (8 seconds as per mobile implementation)
            response = requests.post(f"{self.base_url}/resources/{resource_id}/bookmark", 
                                   headers=auth_headers, timeout=8)
            
            if response.status_code == 200:
                data = response.json()
                if "isBookmarked" in data and "message" in data:
                    is_bookmarked = data["isBookmarked"]
                    message = data["message"]
                    
                    if is_bookmarked and "added" in message.lower():
                        self.log_result("Bookmark Mobile Error Handling", True, 
                                      f"Bookmark functionality working with mobile error handling: {message}")
                        return True
                    else:
                        self.log_result("Bookmark Mobile Error Handling", False, 
                                      f"Unexpected bookmark response: {data}")
                else:
                    self.log_result("Bookmark Mobile Error Handling", False, 
                                  "Missing bookmark response fields", response)
            else:
                self.log_result("Bookmark Mobile Error Handling", False, f"Status code: {response.status_code}", response)
        except requests.exceptions.Timeout:
            self.log_result("Bookmark Mobile Error Handling", False, "Bookmark request timed out (mobile timeout test)")
        except Exception as e:
            self.log_result("Bookmark Mobile Error Handling", False, f"Exception: {str(e)}")
        return False

    def test_resources_api_regression(self):
        """Test resources API to ensure no regressions from mobile safety changes"""
        try:
            # Test get all resources
            response = requests.get(f"{self.base_url}/resources", headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Resources API Regression", True, 
                                  f"Resources API working correctly: {len(data)} resources available")
                    return True
                else:
                    self.log_result("Resources API Regression", False, "Resources response is not a list", response)
            else:
                self.log_result("Resources API Regression", False, f"Status code: {response.status_code}", response)
        except Exception as e:
            self.log_result("Resources API Regression", False, f"Exception: {str(e)}")
        return False

    def test_search_api_regression(self):
        """Test search API to ensure no regressions from mobile safety changes"""
        try:
            # Test basic search functionality
            response = requests.get(f"{self.base_url}/search?q=computer", headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Search API Regression", True, 
                                  f"Search API working correctly: {len(data)} search results")
                    return True
                else:
                    self.log_result("Search API Regression", False, "Search response is not a list", response)
            else:
                self.log_result("Search API Regression", False, f"Status code: {response.status_code}", response)
        except Exception as e:
            self.log_result("Search API Regression", False, f"Exception: {str(e)}")
        return False

    def test_cors_headers_after_mobile_changes(self):
        """Test CORS headers are still working after mobile safety changes"""
        try:
            response = requests.get(f"{self.base_url}/", headers=self.headers, timeout=10)
            
            cors_headers = [
                'Access-Control-Allow-Origin',
                'Access-Control-Allow-Methods',
                'Access-Control-Allow-Headers'
            ]
            
            missing_headers = [header for header in cors_headers 
                             if header not in response.headers]
            
            if not missing_headers:
                self.log_result("CORS Headers After Mobile Changes", True, 
                              "All required CORS headers present after mobile safety changes")
                return True
            else:
                self.log_result("CORS Headers After Mobile Changes", False, 
                              f"Missing CORS headers: {missing_headers}")
        except Exception as e:
            self.log_result("CORS Headers After Mobile Changes", False, f"Exception: {str(e)}")
        return False

    def create_admin_user(self):
        """Helper method to create admin user for testing"""
        try:
            admin_data = {
                "email": "sahuatul2005@gmail.com",  # This email gets admin role
                "password": "AdminTest123!",
                "name": "Test Admin",
                "department": "Computer Science",
                "year": "Faculty"
            }
            
            # Try to register or login
            response = requests.post(f"{self.base_url}/auth/register", json=admin_data, headers=self.headers, timeout=15)
            if response.status_code == 200:
                return response.json().get("token")
            else:
                # Try login if user already exists
                login_response = requests.post(f"{self.base_url}/auth/login", 
                                             json={"email": admin_data["email"], "password": admin_data["password"]}, 
                                             headers=self.headers, timeout=15)
                if login_response.status_code == 200:
                    return login_response.json().get("token")
        except Exception as e:
            print(f"Admin user creation error: {e}")
        return None

    def create_test_resource(self, admin_token):
        """Helper method to create test resource for bookmark testing"""
        try:
            resource_data = {
                "title": "Mobile Safety Test Resource",
                "description": "Resource for testing mobile safety bookmark functionality",
                "department": "Computer Science",
                "year": "Third Year",
                "type": "Notes",
                "subject": "Mobile Testing",
                "fileContent": "data:text/plain;base64,VGVzdCBmaWxlIGZvciBtb2JpbGUgc2FmZXR5",  # "Test file for mobile safety" in base64
                "fileName": "mobile-test.txt",
                "fileType": "text/plain"
            }
            
            headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
            response = requests.post(f"{self.base_url}/resources", json=resource_data, headers=headers, timeout=15)
            
            if response.status_code == 200:
                return response.json().get("id")
        except Exception as e:
            print(f"Test resource creation error: {e}")
        return None

    def run_mobile_safety_tests(self):
        """Run all mobile safety backend integration tests"""
        print("📱 Starting Mobile Safety Backend Integration Tests")
        print("=" * 70)
        print("Testing that mobile safety improvements haven't broken backend APIs")
        print("=" * 70)
        
        # Test sequence focused on mobile safety integration
        test_methods = [
            self.test_api_connectivity,
            self.test_mobile_safe_user_registration,
            self.test_mobile_safe_user_login,
            self.test_token_verification_with_mobile_safety,
            self.test_dashboard_api_with_timeout_handling,
            self.test_bookmark_functionality_with_mobile_error_handling,
            self.test_resources_api_regression,
            self.test_search_api_regression,
            self.test_cors_headers_after_mobile_changes
        ]
        
        for test_method in test_methods:
            try:
                test_method()
                time.sleep(1)  # Small delay between tests
            except Exception as e:
                self.log_result(test_method.__name__, False, f"Test execution error: {str(e)}")
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 MOBILE SAFETY BACKEND INTEGRATION TEST SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {self.results['total_tests']}")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"Success Rate: {(self.results['passed']/self.results['total_tests']*100):.1f}%")
        
        if self.results['errors']:
            print("\n🔍 FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        else:
            print("\n🎉 ALL MOBILE SAFETY BACKEND INTEGRATION TESTS PASSED!")
            print("✅ Mobile safety improvements have not broken any backend functionality")
        
        return self.results

if __name__ == "__main__":
    tester = MobileSafetyBackendTester()
    results = tester.run_mobile_safety_tests()