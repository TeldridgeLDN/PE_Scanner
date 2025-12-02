#!/usr/bin/env python3
"""Quick API test script."""

from pe_scanner.api import create_app

if __name__ == "__main__":
    app = create_app()
    
    # Test with test client
    with app.test_client() as client:
        # Test root endpoint
        print("Testing / ...")
        response = client.get("/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json}")
        print()
        
        # Test health endpoint
        print("Testing /health ...")
        response = client.get("/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json}")
        print()
        
        # Test analyze endpoint with HOOD
        print("Testing /api/analyze/HOOD ...")
        response = client.get("/api/analyze/HOOD")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json
            print(f"Ticker: {data['ticker']}")
            print(f"Analysis Mode: {data['analysis_mode']}")
            print(f"Signal: {data['signal']}")
            print(f"Confidence: {data['confidence']}")
            if 'anchor' in data:
                print(f"Anchor: {data['anchor'][:80]}...")
            if 'headline' in data:
                print(f"Headline: {data['headline'][:80]}...")
        else:
            print(f"Error: {response.json}")
        print()
        
        # Test deprecated endpoint
        print("Testing /api/compression/HOOD (deprecated) ...")
        response = client.get("/api/compression/HOOD")
        print(f"Status: {response.status_code}")
        print(f"Has deprecation warning: {'warning' in response.json}")
        print(f"Headers: X-Deprecated={response.headers.get('X-Deprecated')}")
        print()
        
        print("✅ API tests complete!")

