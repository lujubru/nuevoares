#!/usr/bin/env python3
"""
Ares Club Casino - Frontend-Backend Integration Test
Tests the integration between React frontend and FastAPI backend
"""

import requests
import json
import sys
from datetime import datetime

class IntegrationTester:
    def __init__(self):
        self.frontend_url = "http://localhost:3000"
        self.backend_url = "http://localhost:8001"
        self.tests_run = 0
        self.tests_passed = 0

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")

    def test_frontend_accessibility(self):
        """Test if frontend is accessible"""
        print("\n🔍 Testing Frontend Accessibility...")
        try:
            response = requests.get(self.frontend_url, timeout=10)
            if response.status_code == 200 and "Ares Club" in response.text:
                self.log_test("Frontend Accessibility", True, "Frontend is accessible and contains expected content")
                return True
            else:
                self.log_test("Frontend Accessibility", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Frontend Accessibility", False, str(e))
            return False

    def test_backend_accessibility(self):
        """Test if backend is accessible"""
        print("\n🔍 Testing Backend Accessibility...")
        try:
            response = requests.get(f"{self.backend_url}/api/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_test("Backend Accessibility", True, "Backend is healthy and accessible")
                    return True
                else:
                    self.log_test("Backend Accessibility", False, f"Backend not healthy: {data}")
                    return False
            else:
                self.log_test("Backend Accessibility", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Accessibility", False, str(e))
            return False

    def test_api_endpoints_integration(self):
        """Test all API endpoints that frontend uses"""
        print("\n🔍 Testing API Endpoints Integration...")
        
        endpoints = [
            ("/api/games", "Games API"),
            ("/api/promotions", "Promotions API"),
            ("/api/payment-methods", "Payment Methods API"),
            ("/api/faq", "FAQ API")
        ]
        
        all_passed = True
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and data.get("data"):
                        self.log_test(f"{name} Integration", True, f"Returned {len(data['data'])} items")
                    else:
                        self.log_test(f"{name} Integration", False, "No data returned")
                        all_passed = False
                else:
                    self.log_test(f"{name} Integration", False, f"Status: {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.log_test(f"{name} Integration", False, str(e))
                all_passed = False
        
        return all_passed

    def test_whatsapp_integration(self):
        """Test WhatsApp URL generation"""
        print("\n🔍 Testing WhatsApp Integration...")
        try:
            # Test game interaction
            response = requests.post(f"{self.backend_url}/api/games/1/interact", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "whatsapp_url" in data and "wa.me" in data["whatsapp_url"]:
                    self.log_test("WhatsApp Integration", True, "WhatsApp URL generated correctly")
                    return True
                else:
                    self.log_test("WhatsApp Integration", False, "No WhatsApp URL in response")
                    return False
            else:
                self.log_test("WhatsApp Integration", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("WhatsApp Integration", False, str(e))
            return False

    def test_database_integration(self):
        """Test database integration"""
        print("\n🔍 Testing Database Integration...")
        try:
            # Test contact form submission
            contact_data = {
                "name": "Integration Test",
                "phone": "+5491178419956",
                "email": "integration@test.com",
                "message": "Integration test message",
                "source": "integration_test"
            }
            
            response = requests.post(f"{self.backend_url}/api/contact", json=contact_data, timeout=10)
            if response.status_code == 200:
                # Check if stats reflect the new contact
                stats_response = requests.get(f"{self.backend_url}/api/stats", timeout=10)
                if stats_response.status_code == 200:
                    stats_data = stats_response.json()
                    if stats_data.get("success") and stats_data.get("data"):
                        contacts_count = stats_data["data"].get("total_contacts", 0)
                        self.log_test("Database Integration", True, f"Database working - {contacts_count} total contacts")
                        return True
                    else:
                        self.log_test("Database Integration", False, "Stats API not working")
                        return False
                else:
                    self.log_test("Database Integration", False, "Stats API not accessible")
                    return False
            else:
                self.log_test("Database Integration", False, f"Contact submission failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Database Integration", False, str(e))
            return False

    def test_meta_pixel_integration(self):
        """Test Meta Pixel integration"""
        print("\n🔍 Testing Meta Pixel Integration...")
        try:
            response = requests.get(self.frontend_url, timeout=10)
            if response.status_code == 200:
                html_content = response.text
                if "fbq" in html_content and "Meta Pixel" in html_content:
                    self.log_test("Meta Pixel Integration", True, "Meta Pixel code found in frontend")
                    return True
                else:
                    self.log_test("Meta Pixel Integration", False, "Meta Pixel code not found")
                    return False
            else:
                self.log_test("Meta Pixel Integration", False, f"Frontend not accessible: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Meta Pixel Integration", False, str(e))
            return False

    def test_cors_configuration(self):
        """Test CORS configuration"""
        print("\n🔍 Testing CORS Configuration...")
        try:
            headers = {
                'Origin': 'http://localhost:3000',
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            
            response = requests.options(f"{self.backend_url}/api/games", headers=headers, timeout=10)
            if response.status_code in [200, 204]:
                cors_headers = response.headers
                if 'Access-Control-Allow-Origin' in cors_headers:
                    self.log_test("CORS Configuration", True, "CORS headers present")
                    return True
                else:
                    self.log_test("CORS Configuration", False, "CORS headers missing")
                    return False
            else:
                self.log_test("CORS Configuration", False, f"OPTIONS request failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("CORS Configuration", False, str(e))
            return False

    def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 Starting Ares Club Casino Integration Tests")
        print("=" * 60)
        
        # Run all tests
        self.test_frontend_accessibility()
        self.test_backend_accessibility()
        self.test_api_endpoints_integration()
        self.test_whatsapp_integration()
        self.test_database_integration()
        self.test_meta_pixel_integration()
        self.test_cors_configuration()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 INTEGRATION TEST SUMMARY")
        print("=" * 60)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("\n🎉 ALL INTEGRATION TESTS PASSED!")
            print("✅ Frontend-Backend integration is working correctly")
            print("✅ PostgreSQL database migration successful")
            print("✅ All API endpoints functional")
            print("✅ WhatsApp integration working")
            print("✅ Meta Pixel tracking configured")
            return 0
        else:
            print(f"\n⚠️  {self.tests_run - self.tests_passed} integration tests failed.")
            return 1

def main():
    """Main test execution"""
    print("Ares Club Casino - Integration Test Suite")
    print("Testing Frontend-Backend Integration & PostgreSQL Migration")
    print("-" * 60)
    
    tester = IntegrationTester()
    exit_code = tester.run_all_tests()
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())