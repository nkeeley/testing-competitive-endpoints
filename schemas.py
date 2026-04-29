PRICING_SCHEMA = {
    "type": "object",
    "properties": {
        "plans": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "plan_name": {"type": ["string", "null"]},
                    "price_monthly": {"type": ["string", "null"]},
                    "credits_or_pages": {"type": ["string", "null"]},
                    "rate_limit": {"type": ["string", "null"]},
                    "key_features": {
                        "type": ["array", "null"],
                        "items": {"type": "string"},
                    },
                },
            },
        }
    },
}

PARSE_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": ["string", "null"]},
        "key_topics": {"type": "array", "items": {"type": "string"}},
        "summary": {"type": ["string", "null"]},
    },
}
