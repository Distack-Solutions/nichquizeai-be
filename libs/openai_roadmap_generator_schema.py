SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "description": "The title of the roadmap"},
        "description": {"type": "string", "description": "Description of the roadmap starting with thanking user to take this quiz"},
        "performance_analytics": {
            "type": "array",
            "description": "Performance metrics based on quiz results",
            "items": {
                "type": "object",
                "properties": {
                    "param_name": {
                        "type": "string",
                        "description": "The name of the performance parameter, e.g., 'Sleep Quality' or 'Stress Level'"
                    },
                    "param_description": {
                        "type": "string",
                        "description": "Detailed description of the parameter"
                    },
                    "score": {
                        "type": "object",
                        "description": "Scoring details",
                        "properties": {
                            "value": {
                                "type": "number",
                                "description": "The score for this parameter"
                            },
                            "max_value": {
                                "type": "number",
                                "description": "The maximum possible score for this parameter"
                            }
                        },
                        "required": ["value", "max_value"]
                    }
                },
                "required": ["param_name", "param_description", "score"]
            }
        },
        "sections": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Title of the section"},
                    "steps": {
                        "type": "array",
                        "description": "at least 4-6 steps should be added to systematically explain the section",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string", "description": "Name of the step"},
                                "description": {"type": "string", "description": "Details about the step"}
                            },
                            "required": ["title", "description"]
                        }
                    }
                },
                "required": ["title", "steps"]
            }
        },
        "insights": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "insight": {"type": "string", "description": "General insight or tip based on quiz results"}
                },
                "required": ["insight"]
            }
        },
        "product_recommendation": {
            "type": "array",
            "description": "List of product picked for user from the given list of products based on the given response",
            "items": {
                "type": "object",
                "properties": {
                    "product_key": {"type": "string", "description": "Key of the product recommended for user among the given products"},
                    "benefits": {"type": "array", "items": {"type": "string", "description": "Product benefits, personalized how it can benefit to user"}},
                    "usage_instructions": {"type": "string", "description": "personalized How to use the product"}
                },
                "required": ["product_key", "benefits", "usage_instructions"]
            }
        },
        "encouragement": {
            "type": "string",
            "description": "Motivational message to inspire the user on their journey"
        }
    },
    "required": [
        "title", 
        "description",
        "performance_analytics",
        "sections",
        "insights",
        "product_recommendation",
        "encouragement"
    ]
}
