#!/usr/bin/env python3
"""
Test script for Asset Library API
Run this to test your API endpoints locally
"""

import requests
import json

# Configuration
API_BASE_URL = "http://localhost:8000"  # Change to your deployed URL when testing live

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_test(name, status, response=None):
    """Pretty print test results"""
    symbol = f"{GREEN}✓{RESET}" if status else f"{RED}✗{RESET}"
    print(f"{symbol} {name}")
    if response:
        print(f"  Response: {json.dumps(response, indent=2)}")
    print()


def test_health_check():
    """Test 1: Health check endpoint"""
    print(f"{BLUE}Test 1: Health Check{RESET}")
    try:
        response = requests.get(f"{API_BASE_URL}/")
        success = response.status_code == 200
        print_test("GET /", success, response.json() if success else None)
        return success
    except Exception as e:
        print_test("GET /", False)
        print(f"  Error: {str(e)}\n")
        return False


def test_login(email, password):
    """Test 2: Login endpoint"""
    print(f"{BLUE}Test 2: Login{RESET}")
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/auth/login",
            json={"email": email, "password": password}
        )
        success = response.status_code == 200
        data = response.json() if success else None
        print_test("POST /api/auth/login", success, data)
        
        if success:
            return data.get("token")
        return None
    except Exception as e:
        print_test("POST /api/auth/login", False)
        print(f"  Error: {str(e)}\n")
        return None


def test_get_assets(token, category=None):
    """Test 3: Get assets endpoint"""
    print(f"{BLUE}Test 3: Get Assets{RESET}")
    try:
        params = {"category": category} if category else {}
        response = requests.get(
            f"{API_BASE_URL}/api/assets",
            params=params,
            headers={"Authorization": f"Bearer {token}"}
        )
        success = response.status_code == 200
        data = response.json() if success else None
        
        if success and data:
            print_test(
                f"GET /api/assets (found {len(data)} assets)",
                success,
                data[:2]  # Show first 2 assets
            )
        else:
            print_test("GET /api/assets", success, data)
        
        return data if success else None
    except Exception as e:
        print_test("GET /api/assets", False)
        print(f"  Error: {str(e)}\n")
        return None


def test_get_download_url(token, asset_id):
    """Test 4: Get download URL endpoint"""
    print(f"{BLUE}Test 4: Get Download URL{RESET}")
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/assets/{asset_id}/download",
            headers={"Authorization": f"Bearer {token}"}
        )
        success = response.status_code == 200
        data = response.json() if success else None
        print_test(f"GET /api/assets/{asset_id}/download", success, data)
        return data if success else None
    except Exception as e:
        print_test(f"GET /api/assets/{asset_id}/download", False)
        print(f"  Error: {str(e)}\n")
        return None


def test_get_profile(token):
    """Test 5: Get user profile endpoint"""
    print(f"{BLUE}Test 5: Get User Profile{RESET}")
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/user/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        success = response.status_code == 200
        data = response.json() if success else None
        print_test("GET /api/user/profile", success, data)
        return data if success else None
    except Exception as e:
        print_test("GET /api/user/profile", False)
        print(f"  Error: {str(e)}\n")
        return None


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print(f"{BLUE}Asset Library API Test Suite{RESET}")
    print("="*60 + "\n")
    
    # Test 1: Health check
    if not test_health_check():
        print(f"{RED}API is not running! Start with: python main.py{RESET}\n")
        return
    
    # Get credentials
    print(f"{BLUE}Enter your test credentials:{RESET}")
    email = input("Email: ").strip()
    password = input("Password: ").strip()
    print()
    
    # Test 2: Login
    token = test_login(email, password)
    if not token:
        print(f"{RED}Login failed! Check your credentials and Outseta configuration.{RESET}\n")
        return
    
    # Test 3: Get assets
    assets = test_get_assets(token)
    if not assets:
        print(f"{RED}No assets found! Check your LemonSqueezy configuration.{RESET}\n")
        print("Make sure you have:")
        print("1. Uploaded files to LemonSqueezy")
        print("2. Added custom metadata to products")
        print("3. Set LEMONSQUEEZY_API_KEY correctly\n")
        return
    
    # Test 4: Get download URL (if assets exist)
    if assets and len(assets) > 0:
        first_asset = assets[0]
        test_get_download_url(token, first_asset.get("id"))
    
    # Test 5: Get profile
    test_get_profile(token)
    
    # Summary
    print("="*60)
    print(f"{GREEN}All tests completed!{RESET}")
    print("="*60)
    print(f"\nYour API is ready to use!")
    print(f"API URL: {API_BASE_URL}")
    print(f"Update your Blender addon with this URL.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{RED}Tests cancelled by user{RESET}\n")
    except Exception as e:
        print(f"\n{RED}Unexpected error: {str(e)}{RESET}\n")
