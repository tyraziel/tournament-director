"""
Quick test to verify API server starts and OpenAPI spec is valid.

AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
"""

import json
from src.api.main import app


def test_openapi_spec():
    """Test that OpenAPI spec is generated correctly."""
    openapi_schema = app.openapi()

    print("📋 OpenAPI Specification Generated")
    print("=" * 60)
    print(f"Title: {openapi_schema['info']['title']}")
    print(f"Version: {openapi_schema['info']['version']}")
    print(f"Description: {openapi_schema['info']['description'][:80]}...")
    print()

    # Count paths
    paths = openapi_schema.get('paths', {})
    print(f"API Endpoints: {len(paths)} paths")
    print()

    # List all endpoints
    print("Available Endpoints:")
    print("-" * 60)
    for path, methods in sorted(paths.items()):
        for method in methods.keys():
            if method in ['get', 'post', 'put', 'delete', 'patch']:
                operation = methods[method]
                summary = operation.get('summary', 'No summary')
                print(f"  {method.upper():7} {path:40} - {summary}")

    print()

    # Validate required OpenAPI fields
    assert 'openapi' in openapi_schema, "Missing openapi version"
    assert 'info' in openapi_schema, "Missing info section"
    assert 'paths' in openapi_schema, "Missing paths section"

    print("✅ OpenAPI specification is valid")
    print()

    # Write to file
    with open('/tmp/openapi.json', 'w') as f:
        json.dump(openapi_schema, f, indent=2)
    print("📁 OpenAPI spec saved to /tmp/openapi.json")


if __name__ == "__main__":
    test_openapi_spec()
