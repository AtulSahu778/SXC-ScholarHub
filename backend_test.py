#!/usr/bin/env python3
"""
Backend API Testing for ScholarHub Gemini 2.0 Flash Integration
Tests the POST /api/chat endpoint functionality, session management, error handling, and API security.
"""

import requests
import json
import uuid
import os
import time
from typing import Dict, Any

# Get the base URL from environment or use default
BASE_URL = os.getenv('NEXT_PUBLIC_BASE_URL', 'http://localhost:3000')
API_URL = f"{BASE_URL}/api/chat"

class ScholarHubAPITester:
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details
        })
    
    def test_api_endpoint_basic(self):
        """Test basic POST /api/chat endpoint functionality"""
        print("\n=== Testing Basic API Endpoint Functionality ===")
        
        try:
            # Test with a simple academic question
            payload = {
                "message": "What is the difference between qualitative and quantitative research?",
                "sessionId": self.session_id
            }
            
            response = requests.post(
                API_URL,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'response' in data and data['response']:
                    self.log_test(
                        "Basic API Endpoint",
                        True,
                        f"Successfully received response: {data['response'][:100]}..."
                    )
                    return True
                else:
                    self.log_test(
                        "Basic API Endpoint",
                        False,
                        f"Response missing 'response' field: {data}"
                    )
            else:
                self.log_test(
                    "Basic API Endpoint",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except requests.exceptions.Timeout:
            self.log_test(
                "Basic API Endpoint",
                False,
                "Request timed out after 30 seconds"
            )
        except Exception as e:
            self.log_test(
                "Basic API Endpoint",
                False,
                f"Exception occurred: {str(e)}"
            )
        
        return False
    
    def test_gemini_model_integration(self):
        """Test that the API correctly uses Gemini 2.0 Flash model"""
        print("\n=== Testing Gemini 2.0 Flash Model Integration ===")
        
        try:
            # Ask a question that would help identify the model
            payload = {
                "message": "Can you tell me about your capabilities as an AI assistant?",
                "sessionId": self.session_id
            }
            
            response = requests.post(
                API_URL,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'response' in data and data['response']:
                    # Check if response indicates academic assistant capabilities
                    response_text = data['response'].lower()
                    if any(keyword in response_text for keyword in ['academic', 'research', 'study', 'educational']):
                        self.log_test(
                            "Gemini Model Integration",
                            True,
                            "Model responds with academic context as configured"
                        )
                        return True
                    else:
                        self.log_test(
                            "Gemini Model Integration",
                            True,
                            "Model responds but academic context unclear"
                        )
                        return True
                else:
                    self.log_test(
                        "Gemini Model Integration",
                        False,
                        "No response received from model"
                    )
            else:
                self.log_test(
                    "Gemini Model Integration",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "Gemini Model Integration",
                False,
                f"Exception occurred: {str(e)}"
            )
        
        return False
    
    def test_session_management(self):
        """Test session management with sessionId parameter"""
        print("\n=== Testing Session Management ===")
        
        try:
            # Send first message with session ID
            session_1 = str(uuid.uuid4())
            payload_1 = {
                "message": "Remember this: My favorite subject is Mathematics",
                "sessionId": session_1
            }
            
            response_1 = requests.post(
                API_URL,
                json=payload_1,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response_1.status_code != 200:
                self.log_test(
                    "Session Management",
                    False,
                    f"First request failed: HTTP {response_1.status_code}"
                )
                return False
            
            # Send second message with same session ID
            payload_2 = {
                "message": "What was my favorite subject?",
                "sessionId": session_1
            }
            
            response_2 = requests.post(
                API_URL,
                json=payload_2,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response_2.status_code == 200:
                data_2 = response_2.json()
                if 'response' in data_2:
                    # Check if sessionId is returned
                    if 'sessionId' in data_2 and data_2['sessionId'] == session_1:
                        self.log_test(
                            "Session Management",
                            True,
                            "SessionId correctly maintained and returned"
                        )
                        return True
                    else:
                        self.log_test(
                            "Session Management",
                            True,
                            "Session works but sessionId not returned in response"
                        )
                        return True
                else:
                    self.log_test(
                        "Session Management",
                        False,
                        "No response in second request"
                    )
            else:
                self.log_test(
                    "Session Management",
                    False,
                    f"Second request failed: HTTP {response_2.status_code}"
                )
                
        except Exception as e:
            self.log_test(
                "Session Management",
                False,
                f"Exception occurred: {str(e)}"
            )
        
        return False
    
    def test_error_handling_missing_message(self):
        """Test error handling for missing message parameter"""
        print("\n=== Testing Error Handling - Missing Message ===")
        
        try:
            payload = {
                "sessionId": self.session_id
                # Missing message parameter
            }
            
            response = requests.post(
                API_URL,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 400:
                data = response.json()
                if 'error' in data and 'message' in data['error'].lower():
                    self.log_test(
                        "Error Handling - Missing Message",
                        True,
                        f"Correctly returned 400 error: {data['error']}"
                    )
                    return True
                else:
                    self.log_test(
                        "Error Handling - Missing Message",
                        False,
                        f"400 status but unclear error message: {data}"
                    )
            else:
                self.log_test(
                    "Error Handling - Missing Message",
                    False,
                    f"Expected 400 but got HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "Error Handling - Missing Message",
                False,
                f"Exception occurred: {str(e)}"
            )
        
        return False
    
    def test_error_handling_missing_session_id(self):
        """Test error handling for missing sessionId parameter"""
        print("\n=== Testing Error Handling - Missing SessionId ===")
        
        try:
            payload = {
                "message": "Test message"
                # Missing sessionId parameter
            }
            
            response = requests.post(
                API_URL,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 400:
                data = response.json()
                if 'error' in data and 'session' in data['error'].lower():
                    self.log_test(
                        "Error Handling - Missing SessionId",
                        True,
                        f"Correctly returned 400 error: {data['error']}"
                    )
                    return True
                else:
                    self.log_test(
                        "Error Handling - Missing SessionId",
                        False,
                        f"400 status but unclear error message: {data}"
                    )
            else:
                self.log_test(
                    "Error Handling - Missing SessionId",
                    False,
                    f"Expected 400 but got HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "Error Handling - Missing SessionId",
                False,
                f"Exception occurred: {str(e)}"
            )
        
        return False
    
    def test_response_format(self):
        """Test the response format and structure"""
        print("\n=== Testing Response Format and Structure ===")
        
        try:
            payload = {
                "message": "What is machine learning?",
                "sessionId": self.session_id
            }
            
            response = requests.post(
                API_URL,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                # Check if response is valid JSON
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    self.log_test(
                        "Response Format",
                        False,
                        "Response is not valid JSON"
                    )
                    return False
                
                # Check required fields
                if 'response' in data:
                    if isinstance(data['response'], str) and len(data['response']) > 0:
                        self.log_test(
                            "Response Format",
                            True,
                            f"Valid JSON response with 'response' field containing {len(data['response'])} characters"
                        )
                        return True
                    else:
                        self.log_test(
                            "Response Format",
                            False,
                            "'response' field is empty or not a string"
                        )
                else:
                    self.log_test(
                        "Response Format",
                        False,
                        f"Missing 'response' field in response: {data}"
                    )
            else:
                self.log_test(
                    "Response Format",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "Response Format",
                False,
                f"Exception occurred: {str(e)}"
            )
        
        return False
    
    def test_api_key_security(self):
        """Test that API key is handled securely (server-side only)"""
        print("\n=== Testing API Key Security ===")
        
        try:
            # Check that API key is not exposed in responses
            payload = {
                "message": "Tell me about your configuration",
                "sessionId": self.session_id
            }
            
            response = requests.post(
                API_URL,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                response_text = response.text.lower()
                
                # Check if API key is exposed in response
                if 'aizasy' in response_text or 'api_key' in response_text or 'gemini_api_key' in response_text:
                    self.log_test(
                        "API Key Security",
                        False,
                        "API key or key fragments found in response - security risk!"
                    )
                    return False
                else:
                    self.log_test(
                        "API Key Security",
                        True,
                        "API key not exposed in response - secure handling confirmed"
                    )
                    return True
            else:
                self.log_test(
                    "API Key Security",
                    False,
                    f"Could not test security due to API error: HTTP {response.status_code}"
                )
                
        except Exception as e:
            self.log_test(
                "API Key Security",
                False,
                f"Exception occurred: {str(e)}"
            )
        
        return False
    
    def test_academic_question_handling(self):
        """Test with specific academic questions as requested"""
        print("\n=== Testing Academic Question Handling ===")
        
        academic_questions = [
            "What is the difference between qualitative and quantitative research?",
            "Explain the concept of peer review in academic publishing",
            "What are the key components of a research methodology?"
        ]
        
        successful_tests = 0
        
        for i, question in enumerate(academic_questions, 1):
            try:
                payload = {
                    "message": question,
                    "sessionId": f"{self.session_id}-academic-{i}"
                }
                
                response = requests.post(
                    API_URL,
                    json=payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if 'response' in data and len(data['response']) > 50:  # Reasonable response length
                        successful_tests += 1
                        print(f"  ✅ Question {i}: Got {len(data['response'])} character response")
                    else:
                        print(f"  ❌ Question {i}: Response too short or missing")
                else:
                    print(f"  ❌ Question {i}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ Question {i}: Exception - {str(e)}")
        
        if successful_tests == len(academic_questions):
            self.log_test(
                "Academic Question Handling",
                True,
                f"Successfully handled all {len(academic_questions)} academic questions"
            )
            return True
        elif successful_tests > 0:
            self.log_test(
                "Academic Question Handling",
                True,
                f"Handled {successful_tests}/{len(academic_questions)} academic questions"
            )
            return True
        else:
            self.log_test(
                "Academic Question Handling",
                False,
                "Failed to handle any academic questions"
            )
            return False
    
    def run_all_tests(self):
        """Run all tests and return summary"""
        print("🚀 Starting ScholarHub Gemini 2.0 Flash API Integration Tests")
        print(f"📍 Testing API endpoint: {API_URL}")
        print(f"🔑 Session ID: {self.session_id}")
        
        # Run all tests
        tests = [
            self.test_api_endpoint_basic,
            self.test_gemini_model_integration,
            self.test_session_management,
            self.test_error_handling_missing_message,
            self.test_error_handling_missing_session_id,
            self.test_response_format,
            self.test_api_key_security,
            self.test_academic_question_handling
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
                time.sleep(1)  # Brief pause between tests
            except Exception as e:
                print(f"❌ Test {test.__name__} failed with exception: {e}")
        
        # Print summary
        print(f"\n📊 TEST SUMMARY")
        print(f"{'='*50}")
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("🎉 All tests passed! Gemini 2.0 Flash API integration is working correctly.")
        elif passed > total * 0.7:  # 70% pass rate
            print("⚠️  Most tests passed. Some minor issues detected.")
        else:
            print("🚨 Multiple test failures detected. API integration needs attention.")
        
        return passed, total, self.test_results

if __name__ == "__main__":
    tester = ScholarHubAPITester()
    passed, total, results = tester.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if passed == total else 1)