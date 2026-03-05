#!/usr/bin/env python3
"""
Test script to verify Mistral is working properly
"""

import requests
import json
import sys

def test_mistral_direct():
    """Test Mistral directly through Ollama"""
    print("🔍 Testing Mistral directly...")
    try:
        import ollama
        response = ollama.generate(
            model="mistral",
            prompt="Generate a simple test response"
        )
        print("✅ Mistral is working!")
        print(f"Response: {response['response'][:100]}...")
        return True
    except Exception as e:
        print(f"❌ Mistral test failed: {e}")
        return False

def test_backend():
    """Test the backend API"""
    print("\n🔍 Testing Backend API...")
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is healthy")
            print(f"   Models: {data.get('available_models')}")
            return True
        else:
            print(f"❌ Backend returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False

def test_contract_generation():
    """Test generating a contract"""
    print("\n🔍 Testing Contract Generation with Mistral...")
    
    test_data = {
        "contractType": "Software Development Agreement",
        "parties": {
            "party1": "TechCorp Inc.",
            "party2": "DevStudio LLC",
            "party1_details": {"address": "123 Tech St, SF, CA"},
            "party2_details": {"address": "456 Dev Ave, NY, NY"}
        },
        "terms": "Develop a mobile app with React Native, 3 months timeline, fixed price $50,000",
        "duration": "3 months",
        "penalty": "$5,000 per week delay",
        "language": "English",
        "jurisdiction": "California",
        "additional_clauses": "IP ownership transfers upon full payment"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/generate-contract",
            json=test_data,
            timeout=60  # Give it time to generate
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Contract generated successfully!")
                print(f"   Length: {len(data.get('contract', ''))} characters")
                print(f"   Clauses: {len(data.get('clauses', []))}")
                print(f"   Model used: {data.get('model_used')}")
                
                # Print first few lines of contract
                contract = data.get('contract', '')
                print(f"\n📄 Contract Preview:")
                print("-" * 50)
                print(contract[:500] + "...")
                print("-" * 50)
                return True
            else:
                print(f"❌ Generation failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Mistral Contract Generator\n")
    
    mistral_ok = test_mistral_direct()
    backend_ok = test_backend()
    
    if mistral_ok and backend_ok:
        test_contract_generation()
    else:
        print("\n❌ Setup incomplete. Fix the issues above.")
        sys.exit(1)