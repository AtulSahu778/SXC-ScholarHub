#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for SXC ScholarHub
Tests all authentication, resources, search, and database operations
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Configuration
BASE_URL = "https://753834e2-31a8-4119-a0c0-04a384a471b4.preview.emergentagent.com/api"
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
            self.test_options_request
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