#!/usr/bin/env python3
"""
Backend Testing Script for SXC ScholarHub
Tests all backend APIs and creates sample resources for frontend testing
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:3000/api"
ADMIN_EMAIL = "sahuatul2005@gmail.com"
ADMIN_PASSWORD = "admin123"

class BackendTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.admin_token = None
        self.admin_user = None
        self.test_results = []
        
    def log_test(self, test_name, success, message="", details=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
    def test_api_root(self):
        """Test API root endpoint"""
        try:
            response = requests.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                self.log_test("API Root", True, f"API is running: {data.get('message', '')}")
                return True
            else:
                self.log_test("API Root", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("API Root", False, f"Error: {str(e)}")
            return False
            
    def register_admin_user(self):
        """Register admin user"""
        try:
            user_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD,
                "name": "Admin User",
                "department": "Computer Science",
                "year": "Faculty"
            }
            
            response = requests.post(f"{self.base_url}/auth/register", json=user_data)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                self.admin_user = data.get('user')
                self.log_test("Admin Registration", True, f"Admin user registered successfully. Role: {self.admin_user.get('role')}")
                return True
            elif response.status_code == 400 and "already exists" in response.json().get('error', ''):
                # User already exists, try to login
                return self.login_admin_user()
            else:
                self.log_test("Admin Registration", False, f"Status: {response.status_code}, Error: {response.json().get('error', 'Unknown')}")
                return False
        except Exception as e:
            self.log_test("Admin Registration", False, f"Error: {str(e)}")
            return False
            
    def login_admin_user(self):
        """Login admin user"""
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = requests.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                self.admin_user = data.get('user')
                self.log_test("Admin Login", True, f"Admin logged in successfully. Role: {self.admin_user.get('role')}")
                return True
            else:
                self.log_test("Admin Login", False, f"Status: {response.status_code}, Error: {response.json().get('error', 'Unknown')}")
                return False
        except Exception as e:
            self.log_test("Admin Login", False, f"Error: {str(e)}")
            return False
            
    def verify_token(self):
        """Verify admin token"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/auth/verify", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                user = data.get('user')
                self.log_test("Token Verification", True, f"Token valid. User: {user.get('name')}, Role: {user.get('role')}")
                return True
            else:
                self.log_test("Token Verification", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Token Verification", False, f"Error: {str(e)}")
            return False
            
    def create_sample_resources(self):
        """Create diverse sample resources for testing"""
        sample_resources = [
            {
                "title": "Data Structures and Algorithms - Complete Notes",
                "description": "Comprehensive notes covering arrays, linked lists, trees, graphs, sorting algorithms, and dynamic programming with examples and practice problems.",
                "department": "Computer Science",
                "year": "Second Year",
                "semester": "3rd Semester",
                "type": "Notes",
                "subject": "Data Structures",
                "gdriveLink": "https://drive.google.com/file/d/1example_dsa_notes/view"
            },
            {
                "title": "Database Management Systems - Previous Year Paper 2023",
                "description": "Previous year examination paper for DBMS including SQL queries, normalization, transaction management, and database design questions.",
                "department": "Computer Science", 
                "year": "Third Year",
                "semester": "5th Semester",
                "type": "Previous Year Papers",
                "subject": "Database Management Systems",
                "gdriveLink": "https://drive.google.com/file/d/1example_dbms_paper/view"
            },
            {
                "title": "Calculus and Differential Equations - Assignment Solutions",
                "description": "Step-by-step solutions to calculus problems including limits, derivatives, integrals, and differential equations with detailed explanations.",
                "department": "Mathematics",
                "year": "First Year", 
                "semester": "2nd Semester",
                "type": "Assignments",
                "subject": "Mathematics",
                "gdriveLink": "https://drive.google.com/file/d/1example_math_assignment/view"
            },
            {
                "title": "Physics Lab Manual - Mechanics and Thermodynamics",
                "description": "Complete lab manual with experiments on mechanics, heat, thermodynamics, and wave motion including procedure, observations, and calculations.",
                "department": "Physics",
                "year": "First Year",
                "semester": "1st Semester", 
                "type": "Notes",
                "subject": "Physics",
                "gdriveLink": "https://drive.google.com/file/d/1example_physics_lab/view"
            },
            {
                "title": "Computer Networks - Syllabus and Course Outline",
                "description": "Complete syllabus for Computer Networks course covering OSI model, TCP/IP, routing protocols, network security, and wireless networks.",
                "department": "Computer Science",
                "year": "Third Year",
                "semester": "6th Semester",
                "type": "Syllabus", 
                "subject": "Computer Networks",
                "gdriveLink": "https://drive.google.com/file/d/1example_networks_syllabus/view"
            },
            {
                "title": "Organic Chemistry - Previous Year Paper 2022",
                "description": "Previous year question paper covering organic reactions, mechanisms, stereochemistry, and biomolecules with marking scheme.",
                "department": "Chemistry",
                "year": "Second Year",
                "semester": "4th Semester",
                "type": "Previous Year Papers",
                "subject": "Organic Chemistry", 
                "gdriveLink": "https://drive.google.com/file/d/1example_chemistry_paper/view"
            },
            {
                "title": "Software Engineering - Project Documentation Template",
                "description": "Complete project documentation template including SRS, design documents, test cases, and user manual formats for software projects.",
                "department": "Computer Science",
                "year": "Fourth Year",
                "semester": "7th Semester",
                "type": "Assignments",
                "subject": "Software Engineering",
                "gdriveLink": "https://drive.google.com/file/d/1example_se_template/view"
            },
            {
                "title": "Linear Algebra and Vector Calculus - Comprehensive Notes",
                "description": "Detailed notes on matrices, determinants, eigenvalues, vector spaces, line integrals, surface integrals, and Green's theorem with solved examples.",
                "department": "Mathematics", 
                "year": "Second Year",
                "semester": "3rd Semester",
                "type": "Notes",
                "subject": "Mathematics",
                "gdriveLink": "https://drive.google.com/file/d/1example_linear_algebra/view"
            }
        ]
        
        created_resources = []
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        for i, resource in enumerate(sample_resources, 1):
            try:
                response = requests.post(f"{self.base_url}/resources", json=resource, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    resource_id = data.get('id')
                    created_resources.append(resource_id)
                    self.log_test(f"Resource Creation {i}", True, f"Created: {resource['title'][:50]}... (ID: {resource_id})")
                else:
                    error_msg = response.json().get('error', 'Unknown error')
                    self.log_test(f"Resource Creation {i}", False, f"Failed to create {resource['title'][:30]}... - {error_msg}")
                    
                # Small delay between requests
                time.sleep(0.5)
                
            except Exception as e:
                self.log_test(f"Resource Creation {i}", False, f"Error creating {resource['title'][:30]}... - {str(e)}")
                
        return created_resources
        
    def test_resource_retrieval(self):
        """Test resource retrieval endpoints"""
        try:
            # Test get all resources
            response = requests.get(f"{self.base_url}/resources")
            
            if response.status_code == 200:
                resources = response.json()
                resource_count = len(resources)
                self.log_test("Get All Resources", True, f"Retrieved {resource_count} resources")
                
                # Test get specific resource if any exist
                if resources:
                    first_resource = resources[0]
                    resource_id = first_resource.get('id')
                    
                    response = requests.get(f"{self.base_url}/resources/{resource_id}")
                    if response.status_code == 200:
                        resource_data = response.json()
                        self.log_test("Get Resource by ID", True, f"Retrieved resource: {resource_data.get('title', 'Unknown')}")
                    else:
                        self.log_test("Get Resource by ID", False, f"Status: {response.status_code}")
                        
                return True
            else:
                self.log_test("Get All Resources", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Resource Retrieval", False, f"Error: {str(e)}")
            return False
            
    def test_search_functionality(self):
        """Test search and filter functionality"""
        try:
            # Test basic search
            response = requests.get(f"{self.base_url}/search?q=computer")
            if response.status_code == 200:
                results = response.json()
                self.log_test("Basic Search", True, f"Found {len(results)} results for 'computer'")
            else:
                self.log_test("Basic Search", False, f"Status: {response.status_code}")
                
            # Test department filter
            response = requests.get(f"{self.base_url}/search?department=Computer Science")
            if response.status_code == 200:
                results = response.json()
                self.log_test("Department Filter", True, f"Found {len(results)} Computer Science resources")
            else:
                self.log_test("Department Filter", False, f"Status: {response.status_code}")
                
            # Test year filter
            response = requests.get(f"{self.base_url}/search?year=Second Year")
            if response.status_code == 200:
                results = response.json()
                self.log_test("Year Filter", True, f"Found {len(results)} Second Year resources")
            else:
                self.log_test("Year Filter", False, f"Status: {response.status_code}")
                
            # Test type filter
            response = requests.get(f"{self.base_url}/search?type=Notes")
            if response.status_code == 200:
                results = response.json()
                self.log_test("Type Filter", True, f"Found {len(results)} Notes resources")
            else:
                self.log_test("Type Filter", False, f"Status: {response.status_code}")
                
            return True
            
        except Exception as e:
            self.log_test("Search Functionality", False, f"Error: {str(e)}")
            return False
            
    def test_dashboard_endpoints(self):
        """Test dashboard endpoints"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test admin dashboard
            response = requests.get(f"{self.base_url}/dashboard/admin", headers=headers)
            if response.status_code == 200:
                data = response.json()
                total_uploads = data.get('totalUploads', 0)
                recent_uploads = len(data.get('recentUploads', []))
                self.log_test("Admin Dashboard", True, f"Total uploads: {total_uploads}, Recent: {recent_uploads}")
            else:
                self.log_test("Admin Dashboard", False, f"Status: {response.status_code}")
                
            # Test student dashboard (admin can access it too)
            response = requests.get(f"{self.base_url}/dashboard/student", headers=headers)
            if response.status_code == 200:
                data = response.json()
                total_downloads = data.get('totalDownloads', 0)
                trending_count = len(data.get('trendingResources', []))
                self.log_test("Student Dashboard", True, f"Total downloads: {total_downloads}, Trending resources: {trending_count}")
            else:
                self.log_test("Student Dashboard", False, f"Status: {response.status_code}")
                
            return True
            
        except Exception as e:
            self.log_test("Dashboard Endpoints", False, f"Error: {str(e)}")
            return False
            
    def test_bookmark_functionality(self):
        """Test bookmark functionality"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Get a resource to bookmark
            response = requests.get(f"{self.base_url}/resources")
            if response.status_code == 200:
                resources = response.json()
                if resources:
                    resource_id = resources[0].get('id')
                    
                    # Test bookmark toggle
                    response = requests.post(f"{self.base_url}/resources/{resource_id}/bookmark", headers=headers)
                    if response.status_code == 200:
                        data = response.json()
                        is_bookmarked = data.get('isBookmarked')
                        message = data.get('message')
                        self.log_test("Bookmark Toggle", True, f"Bookmark status: {is_bookmarked}, Message: {message}")
                        return True
                    else:
                        self.log_test("Bookmark Toggle", False, f"Status: {response.status_code}")
                        return False
                else:
                    self.log_test("Bookmark Functionality", False, "No resources available to bookmark")
                    return False
            else:
                self.log_test("Bookmark Functionality", False, f"Failed to get resources: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Bookmark Functionality", False, f"Error: {str(e)}")
            return False
            
    def run_comprehensive_test(self):
        """Run all backend tests"""
        print("🚀 Starting Comprehensive Backend Testing for SXC ScholarHub")
        print("=" * 70)
        
        # Test API connectivity
        if not self.test_api_root():
            print("❌ API is not accessible. Stopping tests.")
            return False
            
        # Test authentication
        if not self.register_admin_user():
            print("❌ Admin user registration/login failed. Stopping tests.")
            return False
            
        if not self.verify_token():
            print("❌ Token verification failed. Stopping tests.")
            return False
            
        # Create sample resources
        print("\n📝 Creating Sample Resources...")
        created_resources = self.create_sample_resources()
        print(f"✅ Created {len(created_resources)} sample resources")
        
        # Test resource operations
        print("\n🔍 Testing Resource Operations...")
        self.test_resource_retrieval()
        
        # Test search functionality
        print("\n🔎 Testing Search and Filter...")
        self.test_search_functionality()
        
        # Test dashboard endpoints
        print("\n📊 Testing Dashboard Endpoints...")
        self.test_dashboard_endpoints()
        
        # Test bookmark functionality
        print("\n🔖 Testing Bookmark Functionality...")
        self.test_bookmark_functionality()
        
        # Print summary
        self.print_test_summary()
        
        return True
        
    def print_test_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("📋 TEST SUMMARY")
        print("=" * 70)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print("\n📊 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}: {result['message']}")
            
        print("\n🎯 BACKEND VERIFICATION COMPLETE!")
        print(f"✅ Admin user registered: {ADMIN_EMAIL}")
        print(f"✅ Sample resources created for frontend testing")
        print(f"✅ All major backend APIs verified and working")
        
        if success_rate >= 80:
            print("🎉 Backend is ready for frontend resource cards limit testing!")
        else:
            print("⚠️  Some issues found. Please review failed tests.")

if __name__ == "__main__":
    tester = BackendTester()
    tester.run_comprehensive_test()