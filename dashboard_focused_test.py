#!/usr/bin/env python3
"""
Focused Smart Academic Dashboard Testing
Tests only the new dashboard features that are implemented
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

    def test_comprehensive_dashboard_features(self):
        """
        Comprehensive test of all Smart Academic Dashboard features
        """
        print("🚀 SMART ACADEMIC DASHBOARD COMPREHENSIVE TESTING")
        print("=" * 60)
        
        # Create test users
        admin_user = {
            "email": "sahuatul2005@gmail.com",  # This email gets admin role
            "password": "AdminTest123",
            "name": "Dr. Admin Test",
            "department": "Computer Science",
            "year": "Faculty"
        }
        
        student_user = {
            "email": f"student.test.{str(uuid.uuid4())[:8]}@sxc.edu.in",
            "password": "StudentTest123",
            "name": "Test Student Dashboard",
            "department": "Mathematics",
            "year": "2024"
        }
        
        admin_token = None
        student_token = None
        test_resource_id = None
        
        # 1. Test User Registration with New Schema Fields
        try:
            response = requests.post(f"{self.base_url}/auth/register", json=student_user)
            if response.status_code == 200:
                data = response.json()
                student_token = data.get('token')
                user_data = data.get('user', {})
                
                # Verify new schema fields
                has_downloads = 'downloads' in user_data and user_data['downloads'] == 0
                has_recent_views = 'recentViews' in user_data and isinstance(user_data['recentViews'], list) and len(user_data['recentViews']) == 0
                has_bookmarks = 'bookmarks' in user_data and isinstance(user_data['bookmarks'], list) and len(user_data['bookmarks']) == 0
                
                if has_downloads and has_recent_views and has_bookmarks:
                    self.log_result("User Registration Schema Enhancement", True, 
                                  f"New user created with downloads: {user_data['downloads']}, recentViews: {user_data['recentViews']}, bookmarks: {user_data['bookmarks']}")
                else:
                    self.log_result("User Registration Schema Enhancement", False, 
                                  f"Schema validation failed - downloads: {has_downloads}, recentViews: {has_recent_views}, bookmarks: {has_bookmarks}")
            else:
                self.log_result("User Registration Schema Enhancement", False, f"Registration failed: {response.status_code}")
        except Exception as e:
            self.log_result("User Registration Schema Enhancement", False, f"Exception: {str(e)}")
        
        # Setup admin user (try login first, then register if needed)
        try:
            login_response = requests.post(f"{self.base_url}/auth/login", 
                                         json={"email": admin_user["email"], "password": admin_user["password"]})
            if login_response.status_code == 200:
                admin_token = login_response.json().get('token')
            else:
                # Try registration
                reg_response = requests.post(f"{self.base_url}/auth/register", json=admin_user)
                if reg_response.status_code == 200:
                    admin_token = reg_response.json().get('token')
        except Exception as e:
            print(f"Admin setup: {e}")
        
        # 2. Test Resource Creation with downloadCount: 0
        if admin_token:
            try:
                resource_data = {
                    "title": "Dashboard Test Resource",
                    "description": "Resource for comprehensive dashboard testing",
                    "department": "Computer Science",
                    "year": "2024",
                    "type": "notes",
                    "subject": "Dashboard Testing",
                    "fileContent": "data:text/plain;base64,VGVzdCBmaWxlIGZvciBkYXNoYm9hcmQgdGVzdGluZw==",  # "Test file for dashboard testing"
                    "fileName": "dashboard-test.txt",
                    "fileType": "text/plain"
                }
                
                headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
                response = requests.post(f"{self.base_url}/resources", json=resource_data, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    test_resource_id = data.get('id')
                    
                    # Verify resource has downloadCount: 0
                    resource_response = requests.get(f"{self.base_url}/resources/{test_resource_id}")
                    if resource_response.status_code == 200:
                        resource = resource_response.json()
                        download_count = resource.get('downloadCount', -1)
                        if download_count == 0:
                            self.log_result("Resource Creation with downloadCount", True, 
                                          f"Resource created with downloadCount: {download_count}")
                        else:
                            self.log_result("Resource Creation with downloadCount", False, 
                                          f"Expected downloadCount: 0, got: {download_count}")
                    else:
                        self.log_result("Resource Creation with downloadCount", False, "Could not verify resource")
                else:
                    self.log_result("Resource Creation with downloadCount", False, f"Resource creation failed: {response.status_code}")
            except Exception as e:
                self.log_result("Resource Creation with downloadCount", False, f"Exception: {str(e)}")
        
        # 3. Test Download Tracking Enhancement
        if student_token and test_resource_id:
            try:
                headers = {"Authorization": f"Bearer {student_token}"}
                
                # Download the resource
                download_response = requests.get(f"{self.base_url}/resources/{test_resource_id}/download", headers=headers)
                
                if download_response.status_code == 200:
                    # Verify user stats updated
                    verify_response = requests.get(f"{self.base_url}/auth/verify", headers=headers)
                    if verify_response.status_code == 200:
                        user_data = verify_response.json().get('user', {})
                        user_downloads = user_data.get('downloads', 0)
                        recent_views = user_data.get('recentViews', [])
                        
                        # Verify resource download count updated
                        resource_response = requests.get(f"{self.base_url}/resources/{test_resource_id}")
                        if resource_response.status_code == 200:
                            resource = resource_response.json()
                            resource_downloads = resource.get('downloadCount', 0)
                            
                            # Check all tracking features
                            user_tracking_ok = user_downloads >= 1
                            recent_views_ok = test_resource_id in recent_views
                            resource_tracking_ok = resource_downloads >= 1
                            
                            if user_tracking_ok and recent_views_ok and resource_tracking_ok:
                                self.log_result("Download Tracking Enhancement", True, 
                                              f"All tracking working: user downloads={user_downloads}, resource downloads={resource_downloads}, in recent views={recent_views_ok}")
                            else:
                                self.log_result("Download Tracking Enhancement", False, 
                                              f"Tracking issues: user downloads={user_downloads}, resource downloads={resource_downloads}, in recent views={recent_views_ok}")
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
                        # Test remove bookmark
                        remove_response = requests.post(f"{self.base_url}/resources/{test_resource_id}/bookmark", headers=headers)
                        if remove_response.status_code == 200:
                            remove_data = remove_response.json()
                            is_removed = not remove_data.get('isBookmarked')
                            remove_message = remove_data.get('message', '')
                            
                            if is_removed and 'removed' in remove_message.lower():
                                self.log_result("Bookmark Add/Remove Functionality", True, 
                                              f"Bookmark toggle working: add={is_bookmarked}, remove={is_removed}")
                            else:
                                self.log_result("Bookmark Add/Remove Functionality", False, 
                                              f"Remove failed: {remove_data}")
                        else:
                            self.log_result("Bookmark Add/Remove Functionality", False, 
                                          f"Remove request failed: {remove_response.status_code}")
                    else:
                        self.log_result("Bookmark Add/Remove Functionality", False, 
                                      f"Add failed: {bookmark_data}")
                else:
                    self.log_result("Bookmark Add/Remove Functionality", False, 
                                  f"Bookmark request failed: {bookmark_response.status_code}")
            except Exception as e:
                self.log_result("Bookmark Add/Remove Functionality", False, f"Exception: {str(e)}")
        
        # 5. Test Student Dashboard Endpoint
        if student_token:
            try:
                headers = {"Authorization": f"Bearer {student_token}"}
                response = requests.get(f"{self.base_url}/dashboard/student", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check all required fields
                    required_fields = ['totalDownloads', 'recentResources', 'bookmarkedResources', 'trendingResources']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        total_downloads = data.get('totalDownloads', 0)
                        recent_resources = data.get('recentResources', [])
                        bookmarked_resources = data.get('bookmarkedResources', [])
                        trending_resources = data.get('trendingResources', [])
                        
                        # Validate data types and structure
                        valid_structure = (
                            isinstance(total_downloads, int) and
                            isinstance(recent_resources, list) and
                            isinstance(bookmarked_resources, list) and
                            isinstance(trending_resources, list)
                        )
                        
                        if valid_structure:
                            self.log_result("Student Dashboard Endpoint", True, 
                                          f"Dashboard data: downloads={total_downloads}, recent={len(recent_resources)}, bookmarked={len(bookmarked_resources)}, trending={len(trending_resources)}")
                        else:
                            self.log_result("Student Dashboard Endpoint", False, "Invalid data structure in response")
                    else:
                        self.log_result("Student Dashboard Endpoint", False, f"Missing required fields: {missing_fields}")
                else:
                    self.log_result("Student Dashboard Endpoint", False, f"Request failed: {response.status_code}")
            except Exception as e:
                self.log_result("Student Dashboard Endpoint", False, f"Exception: {str(e)}")
        
        # 6. Test Admin Dashboard Endpoint
        if admin_token:
            try:
                headers = {"Authorization": f"Bearer {admin_token}"}
                response = requests.get(f"{self.base_url}/dashboard/admin", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check all required fields
                    required_fields = ['totalUploads', 'recentUploads', 'pendingRequests']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        total_uploads = data.get('totalUploads', 0)
                        recent_uploads = data.get('recentUploads', [])
                        pending_requests = data.get('pendingRequests', [])
                        
                        # Validate data types and structure
                        valid_structure = (
                            isinstance(total_uploads, int) and
                            isinstance(recent_uploads, list) and
                            isinstance(pending_requests, list)
                        )
                        
                        if valid_structure:
                            self.log_result("Admin Dashboard Endpoint", True, 
                                          f"Admin dashboard: uploads={total_uploads}, recent={len(recent_uploads)}, pending={len(pending_requests)}")
                        else:
                            self.log_result("Admin Dashboard Endpoint", False, "Invalid data structure in response")
                    else:
                        self.log_result("Admin Dashboard Endpoint", False, f"Missing required fields: {missing_fields}")
                else:
                    self.log_result("Admin Dashboard Endpoint", False, f"Request failed: {response.status_code}")
            except Exception as e:
                self.log_result("Admin Dashboard Endpoint", False, f"Exception: {str(e)}")
        
        # 7. Test Authentication Requirements
        try:
            # Test student dashboard without token
            response = requests.get(f"{self.base_url}/dashboard/student")
            student_auth_ok = response.status_code == 401
            
            # Test admin dashboard without token
            response = requests.get(f"{self.base_url}/dashboard/admin")
            admin_auth_ok = response.status_code == 401
            
            if student_auth_ok and admin_auth_ok:
                self.log_result("Dashboard Authentication Requirements", True, 
                              "Both dashboards correctly require authentication")
            else:
                self.log_result("Dashboard Authentication Requirements", False, 
                              f"Auth check failed: student={student_auth_ok}, admin={admin_auth_ok}")
        except Exception as e:
            self.log_result("Dashboard Authentication Requirements", False, f"Exception: {str(e)}")
        
        # 8. Test Access Control (Student accessing Admin Dashboard)
        if student_token:
            try:
                headers = {"Authorization": f"Bearer {student_token}"}
                response = requests.get(f"{self.base_url}/dashboard/admin", headers=headers)
                
                if response.status_code == 403:
                    error_message = response.json().get('error', '')
                    if 'admin' in error_message.lower():
                        self.log_result("Admin Dashboard Access Control", True, 
                                      "Student correctly blocked from admin dashboard")
                    else:
                        self.log_result("Admin Dashboard Access Control", False, 
                                      f"Wrong error message: {error_message}")
                else:
                    self.log_result("Admin Dashboard Access Control", False, 
                                  f"Expected 403, got {response.status_code}")
            except Exception as e:
                self.log_result("Admin Dashboard Access Control", False, f"Exception: {str(e)}")
        
        # 9. Test Bookmark Authentication
        if test_resource_id:
            try:
                # Test bookmark without token
                response = requests.post(f"{self.base_url}/resources/{test_resource_id}/bookmark")
                if response.status_code == 401:
                    self.log_result("Bookmark Authentication Requirement", True, 
                                  "Bookmark endpoint correctly requires authentication")
                else:
                    self.log_result("Bookmark Authentication Requirement", False, 
                                  f"Expected 401, got {response.status_code}")
            except Exception as e:
                self.log_result("Bookmark Authentication Requirement", False, f"Exception: {str(e)}")
        
        # 10. Test Error Handling - Non-existent Resource Bookmark
        if student_token:
            try:
                fake_resource_id = str(uuid.uuid4())
                headers = {"Authorization": f"Bearer {student_token}"}
                response = requests.post(f"{self.base_url}/resources/{fake_resource_id}/bookmark", headers=headers)
                
                if response.status_code == 404:
                    error_message = response.json().get('error', '')
                    if 'not found' in error_message.lower():
                        self.log_result("Bookmark Error Handling", True, 
                                      "Correctly handles non-existent resource")
                    else:
                        self.log_result("Bookmark Error Handling", False, 
                                      f"Wrong error message: {error_message}")
                else:
                    self.log_result("Bookmark Error Handling", False, 
                                  f"Expected 404, got {response.status_code}")
            except Exception as e:
                self.log_result("Bookmark Error Handling", False, f"Exception: {str(e)}")

    def run_tests(self):
        """Run all dashboard tests"""
        self.test_comprehensive_dashboard_features()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 SMART DASHBOARD TEST SUMMARY")
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
    results = tester.run_tests()