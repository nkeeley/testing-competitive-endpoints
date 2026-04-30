"""Exa runner — wraps exa-py SDK + REST for schema-based extraction."""
import os
import sys
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import EXA_API_KEY

REST_BASE = "https://api.exa.ai"


def _client():
    from exa_py import Exa
    return Exa(api_key=EXA_API_KEY)


def search(query, num_results=5):
    return _client().search(query, num_results=num_results)


def search_and_contents(query, num_results=5):
    return _client().search_and_contents(query, num_results=num_results, text=True)


def _strip_union_types(schema):
    """Exa's schema validator rejects JSON Schema union types like
    ["string", "null"] — it requires single-string types. Walk the schema and
    pick the first non-null type from each union. Returns a copy."""
    import copy
    schema = copy.deepcopy(schema)

    def _walk(node):
        if not isinstance(node, dict):
            return
        if isinstance(node.get("type"), list):
            non_null = [t for t in node["type"] if t != "null"]
            node["type"] = non_null[0] if non_null else "string"
        for v in node.values():
            if isinstance(v, dict):
                _walk(v)
            elif isinstance(v, list):
                for item in v:
                    if isinstance(item, dict):
                        _walk(item)
    _walk(schema)
    return schema


def contents_with_schema(url, schema, query="Extract structured data following the schema"):
    """Schema-based extraction via Exa /contents with summary.schema.
    Verified against exa.ai/docs/reference/get-contents.
    Note: LLM-based, not server-enforced. Exa enforces stricter JSON Schema
    syntax than Firecrawl/SGAI (no union types) so we strip those before sending.
    """
    exa_schema = _strip_union_types(schema)
    resp = requests.post(
        f"{REST_BASE}/contents",
        headers={
            "x-api-key": EXA_API_KEY,
            "Content-Type": "application/json",
        },
        json={
            "urls": [url],
            "summary": {"query": query, "schema": exa_schema},
        },
    )
    resp.raise_for_status()
    return resp.json()
