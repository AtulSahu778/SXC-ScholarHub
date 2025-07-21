#!/usr/bin/env python3
"""
Quick admin functionality test with the correct admin email
"""

import requests
import json

BASE_URL = "http://localhost:3000/api"
HEADERS = {"Content-Type": "application/json"}

def test_admin_functionality():
    print("🔐 Testing Admin Functionality with Correct Email")
    print("-" * 50)
    
    # Admin user data with the correct email
    admin_data = {
        "email": "sahuatul2005@gmail.com",
        "password": "AdminTest123",
        "name": "Admin User",
        "department": "Computer Science",
        "year": "Faculty"
    }
    
    # Test admin registration
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=admin_data, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            user_role = data.get('user', {}).get('role')
            admin_token = data.get('token')
            
            if user_role == 'admin':
                print("✅ Admin Registration: PASSED - Admin role assigned correctly")
                
                # Test admin resource upload
                resource_data = {
                    "title": "Admin Test Resource",
                    "description": "Test resource uploaded by admin",
                    "subject": "Testing",
                    "department": "Computer Science",
                    "year": "2024",
                    "type": "notes",
                    "gdriveLink": "https://drive.google.com/file/d/test123/view"
                }
                
                auth_headers = HEADERS.copy()
                auth_headers["Authorization"] = f"Bearer {admin_token}"
                
                upload_response = requests.post(f"{BASE_URL}/resources", json=resource_data, headers=auth_headers)
                if upload_response.status_code == 200:
                    print("✅ Admin Resource Upload: PASSED - Admin can upload resources")
                else:
                    print(f"❌ Admin Resource Upload: FAILED - Status: {upload_response.status_code}")
                    print(f"   Response: {upload_response.text}")
                
                # Test admin get users
                users_response = requests.get(f"{BASE_URL}/users", headers=auth_headers)
                if users_response.status_code == 200:
                    users = users_response.json()
                    print(f"✅ Admin Get Users: PASSED - Retrieved {len(users)} users")
                else:
                    print(f"❌ Admin Get Users: FAILED - Status: {users_response.status_code}")
                
            else:
                print(f"❌ Admin Registration: FAILED - Expected admin role, got: {user_role}")
        else:
            print(f"❌ Admin Registration: FAILED - Status: {response.status_code}")
            if response.status_code == 400:
                # User might already exist, try login instead
                login_response = requests.post(f"{BASE_URL}/auth/login", 
                                             json={"email": admin_data["email"], "password": admin_data["password"]}, 
                                             headers=HEADERS)
                if login_response.status_code == 200:
                    data = login_response.json()
                    user_role = data.get('user', {}).get('role')
                    if user_role == 'admin':
                        print("✅ Admin Login: PASSED - Admin role verified")
                    else:
                        print(f"❌ Admin Login: FAILED - Expected admin role, got: {user_role}")
                        
    except Exception as e:
        print(f"❌ Admin Test: FAILED - Exception: {str(e)}")

if __name__ == "__main__":
    test_admin_functionality()