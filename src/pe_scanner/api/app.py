"""
Flask API Application for PE Scanner v2.0

Provides RESTful API endpoints for stock analysis with tiered modes,
anchors, headlines, and share URLs.
"""

import logging
from datetime import datetime
from typing import Optional

from flask import Flask, jsonify, request, redirect, url_for
from flask_cors import CORS

from pe_scanner.api.schema import (
    AnalysisResponse,
    ErrorResponse,
    DeprecatedEndpointResponse,
    RateLimitErrorResponse,
    ShareURLs,
)
from pe_scanner.api.service import AnalysisService
from pe_scanner.api.rate_limit import rate_limit_check, RedisClient
from pe_scanner.data.fetcher import fetch_market_data

logger = logging.getLogger(__name__)


# =============================================================================
# Flask App Factory
# =============================================================================


def create_app(config: Optional[dict] = None) -> Flask:
    """
    Create and configure the Flask application.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Configured Flask app instance
    """
    app = Flask(__name__)
    
    # Default configuration
    app.config.update({
        "JSON_SORT_KEYS": False,
        "JSONIFY_PRETTYPRINT_REGULAR": True,
        "MAX_CONTENT_LENGTH": 16 * 1024,  # 16KB max request size
    })
    
    # Apply custom config if provided
    if config:
        app.config.update(config)
    
    # Enable CORS with specific configuration
    # Allow Vercel domains in production, localhost in development
    cors_origins = [
        "https://pe-scanner.com",
        "https://www.pe-scanner.com",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    
    CORS(
        app,
        origins=cors_origins,
        expose_headers=[
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining", 
            "X-RateLimit-Reset",
            "Retry-After"
        ],
        supports_credentials=False,
    )
    
    # Initialize Redis connection on startup
    if RedisClient.is_available():
        logger.info("Redis connection available for rate limiting")
    else:
        logger.warning("Redis unavailable - rate limiting will be disabled")
    
    # Initialize service
    analysis_service = AnalysisService()
    
    # Register routes
    register_routes(app, analysis_service)
    register_error_handlers(app)
    
    return app


# =============================================================================
# Route Registration
# =============================================================================


def register_routes(app: Flask, service: AnalysisService) -> None:
    """Register API routes."""
    
    @app.route("/")
    def index():
        """API root endpoint with welcome message and documentation links."""
        return jsonify({
            "name": "PE Scanner API v2.0",
            "version": "2.0.0",
            "description": "Stock analysis API with tiered modes, anchors, and headlines",
            "endpoints": {
                "analyze": "/api/analyze/<ticker>",
                "deprecated_compression": "/api/compression/<ticker> (redirects to /api/analyze)"
            },
            "documentation": "https://github.com/yourusername/PE_Scanner",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
    
    @app.route("/health")
    def health_check():
        """
        Health check endpoint for Railway monitoring.
        
        Returns service status, Redis connectivity, and basic stats.
        """
        health_data = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "version": "2.0",
            "services": {
                "api": "operational",
                "redis": "unavailable",
            }
        }
        
        # Check Redis connectivity
        try:
            if RedisClient.is_available():
                health_data["services"]["redis"] = "operational"
        except Exception as e:
            logger.warning(f"Redis health check failed: {e}")
            health_data["services"]["redis"] = "error"
        
        # Overall status based on critical services
        # API can run without Redis (graceful degradation)
        # So we keep status "healthy" even if Redis is down
        
        return jsonify(health_data)
    
    @app.route("/api/analyze/<ticker>", methods=["GET"])
    @rate_limit_check
    def analyze_stock(ticker: str):
        """
        Analyze a stock with v2.0 tiered analysis.
        
        Query Parameters:
            include_anchor (bool): Include anchor statement (default: true)
            include_headline (bool): Include headline (default: true)
            include_share_urls (bool): Include share URLs (default: true)
            base_url (str): Base URL for share URLs (optional)
            
        Returns:
            JSON response with complete analysis
        """
        try:
            # Parse query parameters
            include_anchor = request.args.get("include_anchor", "true").lower() == "true"
            include_headline = request.args.get("include_headline", "true").lower() == "true"
            include_share_urls = request.args.get("include_share_urls", "true").lower() == "true"
            base_url = request.args.get("base_url", "")
            
            # Perform analysis
            response = service.analyze(
                ticker=ticker.upper(),
                include_anchor=include_anchor,
                include_headline=include_headline,
                include_share_urls=include_share_urls,
                base_url=base_url,
            )
            
            # Convert to dict for JSON response
            return jsonify(response.model_dump(mode="json", exclude_none=True))
            
        except ValueError as e:
            # Invalid ticker or data not found
            error = ErrorResponse(
                error="InvalidTicker",
                message=str(e),
                ticker=ticker.upper(),
            )
            return jsonify(error.model_dump(mode="json")), 404
            
        except Exception as e:
            # Unexpected error
            logger.error(f"Error analyzing {ticker}: {e}", exc_info=True)
            error = ErrorResponse(
                error="AnalysisError",
                message=f"Failed to analyze {ticker}: {str(e)}",
                ticker=ticker.upper(),
            )
            return jsonify(error.model_dump(mode="json")), 500
    
    @app.route("/api/compression/<ticker>", methods=["GET"])
    def deprecated_compression(ticker: str):
        """
        DEPRECATED: Old P/E compression endpoint.
        
        Redirects to new /api/analyze endpoint with deprecation warning.
        This endpoint will be removed on 2026-01-01.
        """
        try:
            # Get analysis from new endpoint
            include_anchor = request.args.get("include_anchor", "true").lower() == "true"
            include_headline = request.args.get("include_headline", "true").lower() == "true"
            include_share_urls = request.args.get("include_share_urls", "true").lower() == "true"
            base_url = request.args.get("base_url", "")
            
            analysis_response = service.analyze(
                ticker=ticker.upper(),
                include_anchor=include_anchor,
                include_headline=include_headline,
                include_share_urls=include_share_urls,
                base_url=base_url,
            )
            
            # Wrap in deprecation warning
            deprecated_response = DeprecatedEndpointResponse(
                warning="This endpoint is deprecated and will be removed on 2026-01-01",
                deprecated_endpoint=f"/api/compression/{ticker}",
                new_endpoint=f"/api/analyze/{ticker}",
                migration_guide="https://docs.pescanner.com/migration-v2",
                sunset_date="2026-01-01",
                data=analysis_response,
            )
            
            response = jsonify(deprecated_response.model_dump(mode="json", exclude_none=True))
            response.status_code = 200
            response.headers["X-Deprecated"] = "true"
            response.headers["X-Sunset-Date"] = "2026-01-01"
            response.headers["Link"] = f'</api/analyze/{ticker}>; rel="successor-version"'
            
            return response
            
        except ValueError as e:
            error = ErrorResponse(
                error="InvalidTicker",
                message=str(e),
                ticker=ticker.upper(),
            )
            return jsonify(error.model_dump(mode="json")), 404
            
        except Exception as e:
            logger.error(f"Error analyzing {ticker}: {e}", exc_info=True)
            error = ErrorResponse(
                error="AnalysisError",
                message=f"Failed to analyze {ticker}: {str(e)}",
                ticker=ticker.upper(),
            )
            return jsonify(error.model_dump(mode="json")), 500


# =============================================================================
# Error Handlers
# =============================================================================


def register_error_handlers(app: Flask) -> None:
    """Register global error handlers."""
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors."""
        return jsonify({
            "error": "NotFound",
            "message": "The requested endpoint does not exist",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server Error."""
        logger.error(f"Internal server error: {error}", exc_info=True)
        return jsonify({
            "error": "InternalError",
            "message": "An internal server error occurred",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }), 500
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 Method Not Allowed errors."""
        return jsonify({
            "error": "MethodNotAllowed",
            "message": "The HTTP method is not allowed for this endpoint",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }), 405
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        """Handle 429 Too Many Requests errors."""
        return jsonify({
            "error": "RateLimitExceeded",
            "message": "Rate limit exceeded. Please try again later.",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }), 429


# =============================================================================
# CLI Entry Point
# =============================================================================


# Create default app instance for gunicorn
app = create_app()


def main():
    """Run the Flask development server."""
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()

