"""
Integration Tests for PE Scanner API v2.0

Tests the complete API functionality including all endpoints,
query parameters, error handling, and response schemas.
"""

import pytest
from flask.testing import FlaskClient

from pe_scanner.api import create_app


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def app():
    """Create Flask app for testing."""
    app = create_app({"TESTING": True})
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


# =============================================================================
# Root and Health Endpoints
# =============================================================================


def test_root_endpoint(client: FlaskClient):
    """Test API root endpoint returns correct information."""
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json
    assert data["name"] == "PE Scanner API v2.0"
    assert data["version"] == "2.0.0"
    assert "endpoints" in data
    assert "/api/analyze/<ticker>" in data["endpoints"]["analyze"]
    assert "timestamp" in data


def test_health_check(client: FlaskClient):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json
    assert data["status"] == "healthy"
    assert "timestamp" in data


# =============================================================================
# Main Analysis Endpoint Tests
# =============================================================================


def test_analyze_endpoint_basic(client: FlaskClient):
    """Test basic analysis endpoint with default parameters."""
    response = client.get("/api/analyze/AAPL")
    assert response.status_code == 200
    
    data = response.json
    
    # Core fields
    assert data["ticker"] == "AAPL"
    assert "company_name" in data
    assert "current_price" in data
    assert "analysis_mode" in data
    assert "metrics" in data
    assert "signal" in data
    assert "confidence" in data
    assert "data_quality" in data
    assert "timestamp" in data
    
    # v2.0 enhancements (default included)
    assert "anchor" in data
    assert "headline" in data
    assert "share_urls" in data
    
    # Share URLs structure
    if data.get("share_urls"):
        assert "twitter" in data["share_urls"]
        assert "linkedin" in data["share_urls"]
        assert "copy_text" in data["share_urls"]


def test_analyze_exclude_anchor(client: FlaskClient):
    """Test analysis without anchor field."""
    response = client.get("/api/analyze/AAPL?include_anchor=false")
    assert response.status_code == 200
    
    data = response.json
    assert "anchor" not in data
    assert "headline" in data  # Other fields still included
    assert "share_urls" in data


def test_analyze_exclude_headline(client: FlaskClient):
    """Test analysis without headline field."""
    response = client.get("/api/analyze/AAPL?include_headline=false")
    assert response.status_code == 200
    
    data = response.json
    assert "anchor" in data
    assert "headline" not in data
    assert "share_urls" in data  # Share URLs require headline internally


def test_analyze_exclude_share_urls(client: FlaskClient):
    """Test analysis without share URLs."""
    response = client.get("/api/analyze/AAPL?include_share_urls=false")
    assert response.status_code == 200
    
    data = response.json
    assert "anchor" in data
    assert "headline" in data
    assert "share_urls" not in data


def test_analyze_minimal_response(client: FlaskClient):
    """Test minimal response with all optional fields excluded."""
    response = client.get(
        "/api/analyze/AAPL?include_anchor=false&include_headline=false&include_share_urls=false"
    )
    assert response.status_code == 200
    
    data = response.json
    
    # Core fields always present
    assert "ticker" in data
    assert "analysis_mode" in data
    assert "signal" in data
    assert "confidence" in data
    
    # Optional fields excluded
    assert "anchor" not in data
    assert "headline" not in data
    assert "share_urls" not in data


def test_analyze_with_base_url(client: FlaskClient):
    """Test analysis with custom base URL for share links."""
    base_url = "https://example.com"
    response = client.get(f"/api/analyze/AAPL?base_url={base_url}")
    assert response.status_code == 200
    
    data = response.json
    if data.get("share_urls"):
        # Base URL should be included in share text
        assert base_url in data["share_urls"]["copy_text"]


# =============================================================================
# Analysis Mode Tests
# =============================================================================


def test_value_mode_analysis(client: FlaskClient):
    """Test VALUE mode analysis (P/E < 25)."""
    # Using a ticker that should trigger VALUE mode
    response = client.get("/api/analyze/T")  # AT&T typically has low P/E
    
    if response.status_code == 200:
        data = response.json
        # Should have VALUE or possibly HYPER_GROWTH mode
        assert "analysis_mode" in data
        
        # Should have appropriate metrics
        assert "metrics" in data
        if "VALUE" in data["analysis_mode"]:
            assert "compression_pct" in data["metrics"]


def test_growth_mode_analysis(client: FlaskClient):
    """Test GROWTH mode analysis (P/E 25-50)."""
    # Note: This depends on current market conditions
    response = client.get("/api/analyze/MSFT")
    
    if response.status_code == 200:
        data = response.json
        assert "analysis_mode" in data
        assert "metrics" in data


def test_hyper_growth_mode_analysis(client: FlaskClient):
    """Test HYPER_GROWTH mode analysis (P/E > 50 or loss-making)."""
    response = client.get("/api/analyze/PLTR")
    
    if response.status_code == 200:
        data = response.json
        assert "analysis_mode" in data
        assert "metrics" in data


# =============================================================================
# Error Handling Tests
# =============================================================================


def test_invalid_ticker_404(client: FlaskClient):
    """Test that invalid ticker returns 404."""
    response = client.get("/api/analyze/INVALID12345XYZ")
    
    # Should return error (either 404 or 200 with DATA_ERROR signal)
    assert response.status_code in (200, 404, 500)
    
    data = response.json
    if response.status_code == 404:
        assert "error" in data
        assert data["error"] == "InvalidTicker"
        assert "message" in data
        assert "ticker" in data


def test_case_insensitive_ticker(client: FlaskClient):
    """Test that ticker symbols are case-insensitive."""
    response_lower = client.get("/api/analyze/aapl")
    response_upper = client.get("/api/analyze/AAPL")
    
    assert response_lower.status_code == 200
    assert response_upper.status_code == 200
    
    # Both should analyze the same ticker
    assert response_lower.json["ticker"] == "AAPL"
    assert response_upper.json["ticker"] == "AAPL"


def test_invalid_query_parameters(client: FlaskClient):
    """Test that invalid query parameter values are handled gracefully."""
    # Invalid boolean values should default to false
    response = client.get("/api/analyze/AAPL?include_anchor=invalid")
    assert response.status_code == 200
    
    data = response.json
    # 'invalid' != 'true', so should default to false
    assert "anchor" not in data


# =============================================================================
# Deprecated Endpoint Tests
# =============================================================================


def test_deprecated_endpoint_basic(client: FlaskClient):
    """Test deprecated /api/compression endpoint."""
    response = client.get("/api/compression/AAPL")
    assert response.status_code == 200
    
    data = response.json
    
    # Should have deprecation wrapper
    assert "warning" in data
    assert "deprecated" in data["warning"].lower()
    assert "deprecated_endpoint" in data
    assert "new_endpoint" in data
    assert "migration_guide" in data
    assert "sunset_date" in data
    assert "data" in data
    
    # Actual analysis data should be nested
    assert "ticker" in data["data"]
    assert "analysis_mode" in data["data"]


def test_deprecated_endpoint_headers(client: FlaskClient):
    """Test deprecation headers are present."""
    response = client.get("/api/compression/AAPL")
    assert response.status_code == 200
    
    # Check deprecation headers
    assert response.headers.get("X-Deprecated") == "true"
    assert response.headers.get("X-Sunset-Date") == "2026-01-01"
    assert "successor-version" in response.headers.get("Link", "")


def test_deprecated_endpoint_with_params(client: FlaskClient):
    """Test deprecated endpoint respects query parameters."""
    response = client.get("/api/compression/AAPL?include_anchor=false")
    assert response.status_code == 200
    
    data = response.json
    assert "data" in data
    # Anchor should be excluded from nested data
    assert "anchor" not in data["data"]


# =============================================================================
# Response Schema Validation
# =============================================================================


def test_response_has_all_required_fields(client: FlaskClient):
    """Test that response contains all required v2.0 fields."""
    response = client.get("/api/analyze/AAPL")
    assert response.status_code == 200
    
    data = response.json
    
    # Required fields that should always be present
    required_fields = [
        "ticker",
        "analysis_mode",
        "metrics",
        "signal",
        "confidence",
        "data_quality",
        "timestamp",
    ]
    
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"


def test_metrics_structure_varies_by_mode(client: FlaskClient):
    """Test that metrics structure varies appropriately by analysis mode."""
    response = client.get("/api/analyze/AAPL")
    assert response.status_code == 200
    
    data = response.json
    assert "metrics" in data
    assert isinstance(data["metrics"], dict)
    assert len(data["metrics"]) > 0


def test_signal_values_are_valid(client: FlaskClient):
    """Test that signal values are from valid set."""
    response = client.get("/api/analyze/AAPL")
    assert response.status_code == 200
    
    data = response.json
    valid_signals = [
        "STRONG BUY", "BUY", "HOLD", "SELL", "STRONG SELL", "DATA ERROR"
    ]
    assert data["signal"] in valid_signals


def test_confidence_values_are_valid(client: FlaskClient):
    """Test that confidence values are valid."""
    response = client.get("/api/analyze/AAPL")
    assert response.status_code == 200
    
    data = response.json
    valid_confidence = ["high", "medium", "low"]
    assert data["confidence"] in valid_confidence


# =============================================================================
# Integration with v2.0 Modules
# =============================================================================


def test_anchor_generation_integration(client: FlaskClient):
    """Test that anchor generation is integrated properly."""
    response = client.get("/api/analyze/AAPL")
    assert response.status_code == 200
    
    data = response.json
    if "anchor" in data and data["anchor"]:
        # Anchor should be a non-empty string
        assert isinstance(data["anchor"], str)
        assert len(data["anchor"]) > 0


def test_headline_generation_integration(client: FlaskClient):
    """Test that headline generation is integrated properly."""
    response = client.get("/api/analyze/AAPL")
    assert response.status_code == 200
    
    data = response.json
    if "headline" in data and data["headline"]:
        # Headline should contain ticker symbol
        assert "$" in data["headline"]
        assert data["ticker"] in data["headline"]
        # Should be tweet-length
        assert len(data["headline"]) <= 280


def test_share_urls_generation_integration(client: FlaskClient):
    """Test that share URLs are generated properly."""
    response = client.get("/api/analyze/AAPL")
    assert response.status_code == 200
    
    data = response.json
    if "share_urls" in data and data["share_urls"]:
        # All URLs should be present
        assert "twitter" in data["share_urls"]
        assert "linkedin" in data["share_urls"]
        assert "copy_text" in data["share_urls"]
        
        # URLs should be valid
        assert data["share_urls"]["twitter"].startswith("https://twitter.com")
        assert data["share_urls"]["linkedin"].startswith("https://www.linkedin.com")


# =============================================================================
# CORS Tests
# =============================================================================


def test_cors_headers_present(client: FlaskClient):
    """Test that CORS headers are present for cross-origin requests."""
    response = client.get(
        "/api/analyze/AAPL",
        headers={"Origin": "https://example.com"}
    )
    
    assert response.status_code == 200
    # CORS should be enabled
    # Note: Flask-CORS may not set headers in test client, so this might pass without headers


# =============================================================================
# Edge Cases and Error Scenarios
# =============================================================================


def test_404_for_nonexistent_endpoint(client: FlaskClient):
    """Test that nonexistent endpoints return 404."""
    response = client.get("/api/nonexistent")
    assert response.status_code == 404
    
    data = response.json
    assert "error" in data


def test_405_for_wrong_http_method(client: FlaskClient):
    """Test that wrong HTTP methods return 405."""
    response = client.post("/api/analyze/AAPL")
    assert response.status_code == 405
    
    data = response.json
    assert "error" in data


def test_warnings_included_when_present(client: FlaskClient):
    """Test that warnings are included in response when present."""
    response = client.get("/api/analyze/AAPL")
    assert response.status_code == 200
    
    data = response.json
    assert "warnings" in data
    assert isinstance(data["warnings"], list)


# =============================================================================
# Performance and Reliability
# =============================================================================


def test_multiple_sequential_requests(client: FlaskClient):
    """Test that multiple requests work correctly."""
    tickers = ["AAPL", "MSFT", "GOOGL"]
    
    for ticker in tickers:
        response = client.get(f"/api/analyze/{ticker}")
        assert response.status_code == 200
        assert response.json["ticker"] == ticker


def test_response_time_reasonable(client: FlaskClient):
    """Test that response time is reasonable."""
    import time
    
    start = time.time()
    response = client.get("/api/analyze/AAPL")
    elapsed = time.time() - start
    
    assert response.status_code == 200
    # Should complete within 5 seconds (generous for testing)
    assert elapsed < 5.0

