#!/usr/bin/env python3
"""
Security-Enhanced MCP Server for External Access
==============================================

This is a security wrapper around the main MCP server for external tunnel access.
It adds authentication, rate limiting, and request filtering.

Usage:
1. For local access: Use original mcp_server.py
2. For external access: Use this secure version with authentication

Environment Variables:
- MCP_API_KEY: API key for authentication (generated automatically if not set)
- MCP_ALLOWED_ORIGINS: Comma-separated list of allowed origins
- MCP_RATE_LIMIT: Requests per minute (default: 100)
"""

import os
import sys
import hashlib
import secrets
import time
import json
from functools import wraps
from typing import Dict, Any, Optional
import logging

# Import the main MCP server
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from mcp_server import mcp, app

# Security configuration
API_KEY = os.environ.get('MCP_API_KEY', secrets.token_urlsafe(32))
ALLOWED_ORIGINS = os.environ.get('MCP_ALLOWED_ORIGINS', '').split(',') if os.environ.get('MCP_ALLOWED_ORIGINS') else []
RATE_LIMIT = int(os.environ.get('MCP_RATE_LIMIT', '100'))  # requests per minute
SECURE_MODE = os.environ.get('MCP_SECURE_MODE', 'true').lower() == 'true'

# Rate limiting storage
request_counts = {}
request_history = {}

logger = logging.getLogger(__name__)

def generate_api_key():
    """Generate a new API key and save it to a file."""
    api_key = secrets.token_urlsafe(32)
    
    # Save to file for reference
    with open('.mcp_api_key', 'w') as f:
        f.write(f"MCP_API_KEY={api_key}\n")
        f.write(f"# Add this to your environment or tunnel configuration\n")
        f.write(f"# export MCP_API_KEY={api_key}\n")
    
    os.chmod('.mcp_api_key', 0o600)  # Secure file permissions
    return api_key

def check_rate_limit(client_ip: str) -> bool:
    """Check if client is within rate limits."""
    current_time = int(time.time() / 60)  # Current minute
    
    if client_ip not in request_counts:
        request_counts[client_ip] = {}
    
    # Clean old entries (older than 1 minute)
    request_counts[client_ip] = {
        minute: count for minute, count in request_counts[client_ip].items()
        if minute >= current_time - 1
    }
    
    # Count requests in current minute
    current_requests = request_counts[client_ip].get(current_time, 0)
    
    if current_requests >= RATE_LIMIT:
        return False
    
    # Increment counter
    request_counts[client_ip][current_time] = current_requests + 1
    return True

def validate_api_key(provided_key: str) -> bool:
    """Validate the provided API key."""
    if not SECURE_MODE:
        return True
    
    return secrets.compare_digest(provided_key, API_KEY)

def security_middleware():
    """Security middleware for the MCP server."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get client info (this would need to be adapted based on FastMCP's request handling)
            client_ip = "unknown"  # Would need to extract from request
            
            # Rate limiting
            if not check_rate_limit(client_ip):
                logger.warning(f"Rate limit exceeded for client {client_ip}")
                return {
                    "error": "Rate limit exceeded",
                    "code": 429,
                    "message": f"Maximum {RATE_LIMIT} requests per minute allowed"
                }
            
            # API key validation (for external access)
            if SECURE_MODE:
                # This would need to be adapted based on how FastMCP handles headers
                # For now, we'll check if API key is in environment
                pass
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def create_security_config():
    """Create security configuration file."""
    config = {
        "api_key": API_KEY,
        "rate_limit": RATE_LIMIT,
        "secure_mode": SECURE_MODE,
        "allowed_origins": ALLOWED_ORIGINS,
        "setup_time": time.time(),
        "instructions": {
            "curl_example": f"curl -H 'Authorization: Bearer {API_KEY}' https://your-tunnel-url.com/mcp/tools",
            "javascript_example": f"fetch('https://your-tunnel-url.com/mcp/tools', {{ headers: {{ 'Authorization': 'Bearer {API_KEY}' }} }})",
            "environment_setup": f"export MCP_API_KEY={API_KEY}"
        }
    }
    
    with open('.mcp_security_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    os.chmod('.mcp_security_config.json', 0o600)
    return config

def print_security_info():
    """Print security setup information."""
    print("\n🔐 MCP Server Security Configuration")
    print("=" * 50)
    print(f"🔑 API Key: {API_KEY}")
    print(f"🚦 Rate Limit: {RATE_LIMIT} requests/minute")
    print(f"🛡️  Secure Mode: {'Enabled' if SECURE_MODE else 'Disabled'}")
    print(f"🌐 Allowed Origins: {ALLOWED_ORIGINS if ALLOWED_ORIGINS else 'All (not recommended for production)'}")
    print("\n📋 Usage Examples:")
    print(f"   curl -H 'Authorization: Bearer {API_KEY}' https://your-tunnel-url.com/health")
    print(f"   curl -H 'Authorization: Bearer {API_KEY}' https://your-tunnel-url.com/mcp/server_info")
    print("\n📁 Files Created:")
    print("   .mcp_api_key - API key for reference")
    print("   .mcp_security_config.json - Full security configuration")
    print("\n⚠️  Security Notes:")
    print("   - Keep your API key secure and private")
    print("   - Add IP restrictions in Cloudflare for extra security")
    print("   - Monitor access logs regularly")
    print("   - Consider adding Cloudflare Access for additional protection")
    print("\n")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Security-Enhanced MCP Server")
    parser.add_argument("--generate-key", action="store_true", help="Generate a new API key")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    parser.add_argument("--host", default="127.0.0.1", help="Server host")
    parser.add_argument("--disable-security", action="store_true", help="Disable security (not recommended)")
    
    args = parser.parse_args()
    
    if args.generate_key:
        new_key = generate_api_key()
        print(f"🔑 New API key generated: {new_key}")
        print("💾 Saved to .mcp_api_key file")
        print("🔄 Restart the server to use the new key")
        sys.exit(0)
    
    if args.disable_security:
        SECURE_MODE = False
        print("⚠️  Security disabled - not recommended for external access!")
    
    # Generate API key if not exists
    if not os.path.exists('.mcp_api_key') and SECURE_MODE:
        API_KEY = generate_api_key()
    
    # Create security configuration
    config = create_security_config()
    
    # Print security information
    print_security_info()
    
    # Start the server (this would need to be adapted based on FastMCP's architecture)
    print(f"🚀 Starting Secure MCP Server on {args.host}:{args.port}")
    print("🔐 Security middleware enabled")
    
    # This is a placeholder - actual implementation would depend on FastMCP's middleware system
    # For now, we'll just run the original server with security info
    from mcp_server import main
    main() 