#!/usr/bin/env python3
"""Detailed API test with actual analysis."""

import json
from pe_scanner.api import create_app

if __name__ == "__main__":
    app = create_app()
    
    with app.test_client() as client:
        print("=" * 80)
        print("PE SCANNER API v2.0 - DETAILED TEST")
        print("=" * 80)
        print()
        
        # Test 1: Full analysis with all fields
        print("1. Full Analysis with All Fields (AAPL)")
        print("-" * 80)
        response = client.get("/api/analyze/AAPL")
        if response.status_code == 200:
            data = response.json
            print(json.dumps(data, indent=2, default=str))
        else:
            print(f"Error: {response.json}")
        print()
        
        # Test 2: Analysis without anchor
        print("2. Analysis Without Anchor (AAPL, include_anchor=false)")
        print("-" * 80)
        response = client.get("/api/analyze/AAPL?include_anchor=false")
        if response.status_code == 200:
            data = response.json
            print(f"Has anchor: {'anchor' in data}")
            print(f"Has headline: {'headline' in data}")
            print(f"Has share_urls: {'share_urls' in data}")
        print()
        
        # Test 3: Analysis without headline
        print("3. Analysis Without Headline (AAPL, include_headline=false)")
        print("-" * 80)
        response = client.get("/api/analyze/AAPL?include_headline=false")
        if response.status_code == 200:
            data = response.json
            print(f"Has anchor: {'anchor' in data}")
            print(f"Has headline: {'headline' in data}")
            print(f"Has share_urls: {'share_urls' in data}")
        print()
        
        # Test 4: Minimal response (no extras)
        print("4. Minimal Response (AAPL, all extras false)")
        print("-" * 80)
        response = client.get("/api/analyze/AAPL?include_anchor=false&include_headline=false&include_share_urls=false")
        if response.status_code == 200:
            data = response.json
            print(f"Has anchor: {'anchor' in data}")
            print(f"Has headline: {'headline' in data}")
            print(f"Has share_urls: {'share_urls' in data}")
            print(f"Has metrics: {'metrics' in data}")
            print(f"Signal: {data['signal']}")
        print()
        
        # Test 5: Invalid ticker
        print("5. Invalid Ticker Error Handling")
        print("-" * 80)
        response = client.get("/api/analyze/INVALID12345")
        print(f"Status: {response.status_code}")
        if response.status_code == 404:
            print("✅ Correctly returned 404")
            print(f"Error: {response.json['error']}")
            print(f"Message: {response.json['message']}")
        print()
        
        # Test 6: Deprecated endpoint
        print("6. Deprecated Endpoint Test")
        print("-" * 80)
        response = client.get("/api/compression/AAPL")
        print(f"Status: {response.status_code}")
        print(f"X-Deprecated header: {response.headers.get('X-Deprecated')}")
        print(f"X-Sunset-Date header: {response.headers.get('X-Sunset-Date')}")
        print(f"Link header: {response.headers.get('Link')}")
        if response.status_code == 200:
            data = response.json
            print(f"Has 'warning' key: {'warning' in data}")
            print(f"Warning message: {data.get('warning', 'N/A')}")
            print(f"New endpoint: {data.get('new_endpoint', 'N/A')}")
        print()
        
        print("=" * 80)
        print("✅ ALL TESTS COMPLETE!")
        print("=" * 80)

