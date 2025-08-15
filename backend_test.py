#!/usr/bin/env python3
"""
Ares Club Casino - Backend API Test Suite
Tests all API endpoints and database connectivity for PostgreSQL migration
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any

class AresClubAPITester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url.rstrip('/')
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

    def run_test(self, name: str, method: str, endpoint: str, expected_status: int = 200, 
                 data: Dict[Any, Any] = None, headers: Dict[str, str] = None) -> tuple:
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                self.log_test(name, False, f"Unsupported HTTP method: {method}")
                return False, {}

            success = response.status_code == expected_status
            
            if success:
                try:
                    response_data = response.json()
                    self.log_test(name, True, f"Status: {response.status_code}")
                    return True, response_data
                except json.JSONDecodeError:
                    self.log_test(name, True, f"Status: {response.status_code} (No JSON response)")
                    return True, {"text": response.text}
            else:
                error_detail = f"Expected {expected_status}, got {response.status_code}"
                try:
                    error_data = response.json()
                    error_detail += f" - {error_data.get('detail', 'No error details')}"
                except:
                    error_detail += f" - Response: {response.text[:200]}"
                
                self.log_test(name, False, error_detail)
                return False, {}

        except requests.exceptions.ConnectionError:
            self.log_test(name, False, "Connection refused - Backend server not running")
            return False, {}
        except requests.exceptions.Timeout:
            self.log_test(name, False, "Request timeout")
            return False, {}
        except Exception as e:
            self.log_test(name, False, f"Unexpected error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test health check endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "/api/health",
            200
        )
        
        if success and response:
            if response.get("status") == "healthy" and response.get("database") == "connected":
                print("   ✅ Database connection verified")
                return True
            else:
                print(f"   ⚠️  Health check response: {response}")
                return False
        return success

    def test_root_endpoint(self):
        """Test root endpoint"""
        success, response = self.run_test(
            "Root Endpoint",
            "GET",
            "/",
            200
        )
        
        if success and response:
            if "Ares Club Casino" in response.get("message", ""):
                print("   ✅ Root endpoint working correctly")
                return True
        return success

    def test_games_endpoints(self):
        """Test games-related endpoints"""
        # Test get all games
        success, games_response = self.run_test(
            "Get All Games",
            "GET",
            "/api/games",
            200
        )
        
        if not success:
            return False
            
        games_data = games_response.get("data", [])
        if not games_data:
            print("   ⚠️  No games data returned")
            return False
            
        print(f"   ✅ Found {len(games_data)} games")
        
        # Test get specific game
        first_game_id = games_data[0].get("id") if games_data else 1
        success, game_response = self.run_test(
            f"Get Game {first_game_id}",
            "GET",
            f"/api/games/{first_game_id}",
            200
        )
        
        if success:
            print(f"   ✅ Game details retrieved for ID {first_game_id}")
        
        # Test game interaction
        success, interaction_response = self.run_test(
            f"Game {first_game_id} Interaction",
            "POST",
            f"/api/games/{first_game_id}/interact",
            200
        )
        
        if success and interaction_response:
            if "whatsapp_url" in interaction_response:
                print("   ✅ Game interaction recorded with WhatsApp URL")
                return True
        
        return success

    def test_promotions_endpoints(self):
        """Test promotions endpoints"""
        # Test get promotions
        success, promos_response = self.run_test(
            "Get Promotions",
            "GET",
            "/api/promotions",
            200
        )
        
        if not success:
            return False
            
        promos_data = promos_response.get("data", [])
        print(f"   ✅ Found {len(promos_data)} promotions")
        
        # Test promotion interaction
        if promos_data:
            first_promo_id = promos_data[0].get("id")
            success, interaction_response = self.run_test(
                f"Promotion {first_promo_id} Interaction",
                "POST",
                f"/api/promotions/{first_promo_id}/interact",
                200
            )
            
            if success and interaction_response:
                if "whatsapp_url" in interaction_response:
                    print("   ✅ Promotion interaction recorded")
                    return True
        
        return success

    def test_payment_methods(self):
        """Test payment methods endpoint"""
        success, response = self.run_test(
            "Get Payment Methods",
            "GET",
            "/api/payment-methods",
            200
        )
        
        if success and response:
            methods_data = response.get("data", [])
            print(f"   ✅ Found {len(methods_data)} payment methods")
            return True
        
        return success

    def test_faq_endpoint(self):
        """Test FAQ endpoint"""
        success, response = self.run_test(
            "Get FAQ",
            "GET",
            "/api/faq",
            200
        )
        
        if success and response:
            faq_data = response.get("data", [])
            print(f"   ✅ Found {len(faq_data)} FAQ items")
            return True
        
        return success

    def test_contact_endpoint(self):
        """Test contact form endpoint"""
        test_contact_data = {
            "name": "Test User",
            "phone": "+5491178419956",
            "email": "test@example.com",
            "message": "Test contact from API test",
            "source": "api_test"
        }
        
        success, response = self.run_test(
            "Contact Form Submission",
            "POST",
            "/api/contact",
            200,
            data=test_contact_data
        )
        
        if success and response:
            if "whatsapp_url" in response:
                print("   ✅ Contact form processed successfully")
                return True
        
        return success

    def test_stats_endpoint(self):
        """Test statistics endpoint"""
        success, response = self.run_test(
            "Get Statistics",
            "GET",
            "/api/stats",
            200
        )
        
        if success and response:
            stats_data = response.get("data", {})
            if "total_contacts" in stats_data and "total_game_interactions" in stats_data:
                print(f"   ✅ Stats: {stats_data.get('total_contacts')} contacts, "
                      f"{stats_data.get('total_game_interactions')} game interactions")
                return True
        
        return success

    def test_invalid_endpoints(self):
        """Test error handling for invalid endpoints"""
        # Test non-existent game
        success, response = self.run_test(
            "Non-existent Game",
            "GET",
            "/api/games/999",
            404
        )
        
        if success:
            print("   ✅ Proper 404 handling for non-existent game")
        
        # Test non-existent promotion interaction
        success2, response2 = self.run_test(
            "Non-existent Promotion Interaction",
            "POST",
            "/api/promotions/999/interact",
            404
        )
        
        if success2:
            print("   ✅ Proper 404 handling for non-existent promotion")
        
        return success and success2

    def run_all_tests(self):
        """Run all backend API tests"""
        print("🚀 Starting Ares Club Casino Backend API Tests")
        print("=" * 60)
        
        # Core functionality tests
        self.test_root_endpoint()
        self.test_health_check()
        
        # API endpoint tests
        self.test_games_endpoints()
        self.test_promotions_endpoints()
        self.test_payment_methods()
        self.test_faq_endpoint()
        self.test_contact_endpoint()
        self.test_stats_endpoint()
        
        # Error handling tests
        self.test_invalid_endpoints()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("\n🎉 ALL TESTS PASSED! Backend API is working correctly.")
            return 0
        else:
            print(f"\n⚠️  {self.tests_run - self.tests_passed} tests failed. Check the details above.")
            
            # Print failed tests
            failed_tests = [t for t in self.test_results if not t["success"]]
            if failed_tests:
                print("\n❌ FAILED TESTS:")
                for test in failed_tests:
                    print(f"   - {test['test']}: {test['details']}")
            
            return 1

def main():
    """Main test execution"""
    print("Ares Club Casino - Backend API Test Suite")
    print("Testing PostgreSQL migration and API functionality")
    print("-" * 60)
    
    # Initialize tester
    tester = AresClubAPITester()
    
    # Run all tests
    exit_code = tester.run_all_tests()
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())