#!/usr/bin/env python3
"""
Test admin login and functionality
"""

import requests
import json

BASE_URL = "http://localhost:3000/api"
HEADERS = {"Content-Type": "application/json"}

def test_admin_login():
    print("🔐 Testing Admin Login and Functionality")
    print("-" * 50)
    
    # Try to login with admin credentials
    login_data = {
        "email": "sahuatul2005@gmail.com",
        "password": "AdminTest123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            user_role = data.get('user', {}).get('role')
            admin_token = data.get('token')
            
            print(f"✅ Admin Login: PASSED - Role: {user_role}")
            
            if user_role == 'admin' and admin_token:
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
                    print("✅ Admin Resource Upload: PASSED")
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
            print(f"❌ Admin Login: FAILED - Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
            # Try to register new admin user with different password
            admin_data = {
                "email": "sahuatul2005@gmail.com",
                "password": "NewAdminPass123",
                "name": "Admin User",
                "department": "Computer Science",
                "year": "Faculty"
            }
            
            reg_response = requests.post(f"{BASE_URL}/auth/register", json=admin_data, headers=HEADERS)
            if reg_response.status_code == 200:
                data = reg_response.json()
                user_role = data.get('user', {}).get('role')
                print(f"✅ Admin Registration: PASSED - Role: {user_role}")
            else:
                print(f"❌ Admin Registration: FAILED - Status: {reg_response.status_code}")
                print(f"   Response: {reg_response.text}")
                
    except Exception as e:
        print(f"❌ Admin Test: FAILED - Exception: {str(e)}")

if __name__ == "__main__":
    test_admin_login()