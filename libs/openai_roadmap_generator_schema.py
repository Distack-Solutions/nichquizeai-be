# SCHEMA = {
#     "type": "object",
#     "properties": {
#         "title": {"type": "string", "description": "The title of the roadmap"},
#         "description": {"type": "string", "description": "Description of the roadmap starting with thanking user to take this quiz"},
#         "performance_analytics": {
#             "type": "array",
#             "description": "Performance metrics based on quiz results",
#             "items": {
#                 "type": "object",
#                 "properties": {
#                     "param_name": {
#                         "type": "string",
#                         "description": "The name of the performance parameter, e.g., 'Sleep Quality' or 'Stress Level'"
#                     },
#                     "param_description": {
#                         "type": "string",
#                         "description": "Detailed description of the parameter"
#                     },
#                     "score": {
#                         "type": "object",
#                         "description": "Scoring details",
#                         "properties": {
#                             "value": {
#                                 "type": "number",
#                                 "description": "The score for this parameter"
#                             },
#                             "max_value": {
#                                 "type": "number",
#                                 "description": "The maximum possible score for this parameter"
#                             }
#                         },
#                         "required": ["value", "max_value"]
#                     }
#                 },
#                 "required": ["param_name", "param_description", "score"]
#             }
#         },
#         "sections": {
#             "type": "array",
#             "items": {
#                 "type": "object",
#                 "properties": {
#                     "title": {"type": "string", "description": "Title of the section"},
#                     "steps": {
#                         "type": "array",
#                         "description": "at least 4-6 steps should be added to systematically explain the section",
#                         "items": {
#                             "type": "object",
#                             "properties": {
#                                 "title": {"type": "string", "description": "Name of the step"},
#                                 "description": {"type": "string", "description": "Details about the step"}
#                             },
#                             "required": ["title", "description"]
#                         }
#                     }
#                 },
#                 "required": ["title", "steps"]
#             }
#         },
#         "insights": {
#             "type": "array",
#             "items": {
#                 "type": "object",
#                 "properties": {
#                     "insight": {"type": "string", "description": "General insight or tip based on quiz results"}
#                 },
#                 "required": ["insight"]
#             }
#         },
#         "product_recommendation": {
#             "type": "array",
#             "description": "List of product picked for user from the given list of products based on the given response",
#             "items": {
#                 "type": "object",
#                 "properties": {
#                     "product_key": {"type": "string", "description": "Key of the product recommended for user among the given products"},
#                     "benefits": {"type": "array", "items": {"type": "string", "description": "Product benefits, personalized how it can benefit to user"}},
#                     "usage_instructions": {"type": "string", "description": "personalized How to use the product"}
#                 },
#                 "required": ["product_key", "benefits", "usage_instructions"]
#             }
#         },
#         "encouragement": {
#             "type": "string",
#             "description": "Motivational message to inspire the user on their journey"
#         }
#     },
#     "required": [
#         "title", 
#         "description",
#         "performance_analytics",
#         "sections",
#         "insights",
#         "product_recommendation",
#         "encouragement"
#     ]
# }





SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "description": "The title of the roadmap"},
        "description": {"type": "string", "description": "A good paragraph Description of the roadmap starting with thanking and motivating user to take this quiz"},
        "longevity_score": {
            "type": "object",
            "description": "longevity score object to show overall health and wellness of user based on his responses out of 100",
            "properties": {
                "score": {
                    "type": "object",
                    "description": "Scoring details",
                    "properties": {
                        "value": {
                            "type": "number",
                            "description": "The score for this parameter out of 100"
                        },
                        "max_value": {
                            "type": "number",
                            "description": "The maximum possible score for this parameter, i.e 100"
                        }
                    },
                    "required": ["value", "max_value"]
                },
                "status": {
                    "type": "string",
                    "description": "status of the longevity_score i.e Critical, Low, Balanced, Good, Perfect"
                },
                "description": {
                    "type": "string",
                    "description": "Description of the current Longevity score with motivating words a/c to the status"
                }
            },
            "required": ["score", "status", "description"]
        },
        "morning_routine": {
            "type": "object",
            "description": "Steps to energize your day naturally through hydration, a nutritious breakfast, and light movement.",
            "properties": {
                "title": {
                    "type": "string",
                },
                "steps": {
                    "type": "array",
                    "description": "At least 4-6 steps to explain how to energize your day naturally.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Name of the step"
                            },
                            "description": {
                                "type": "string",
                                "description": "Details about the step"
                            }
                        },
                        "required": ["title", "description"]
                    }
                }
            },
            "required": ["title", "steps"]
        },
        "midday_strategy": {
            "type": "object",
            "description": "Tips to combat energy dips, improve digestion, and maintain focus with balanced meals and mindful breaks.",
            "properties": {
                "title": {
                    "type": "string",
                },
                "steps": {
                    "type": "array",
                    "description": "At least 4-6 steps to explain strategies for combating midday energy dips and maintaining focus.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Name of the step"
                            },
                            "description": {
                                "type": "string",
                                "description": "Details about the step"
                            }
                        },
                        "required": ["title", "description"]
                    }
                }
            },
            "required": ["title", "steps"]
        },
        "evening_habits": {
            "type": "object",
            "description": "Techniques for relaxation, light dinner suggestions, and preparing for restorative sleep.",
            "properties": {
                "title": {
                    "type": "string",
                },
                "steps": {
                    "type": "array",
                    "description": "At least 4-6 steps to explain evening habits for relaxation and preparing for sleep.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Name of the step"
                            },
                            "description": {
                                "type": "string",
                                "description": "Details about the step"
                            }
                        },
                        "required": ["title", "description"]
                    }
                }
            },
            "required": ["title", "steps"]
        },
        "specific_lifestyle_tips": {
            "type": "object",
            "description": "Personalized lifestyle changes such as mindful eating, regular physical activity, and stress management.",
            "properties": {
                "title": {
                    "type": "string",
                },
                "steps": {
                    "type": "array",
                    "description": "At least 4-6 steps for specific lifestyle tips related to mindful eating, activity, and stress management.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Name of the step"
                            },
                            "description": {
                                "type": "string",
                                "description": "Details about the step"
                            }
                        },
                        "required": ["title", "description"]
                    }
                }
            },
            "required": ["title", "steps"]
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
            "description": "List of product picked for user from the given list of products based on the given response, maximum 2 products should be recommended",
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
            "description": "Motivational paragraph to inspire the user on their journey"
        }
    },
    "required": [
        "title", 
        "description",
        "longevity_score",
        "morning_routine",
        "midday_strategy",
        "evening_habits",
        "specific_lifestyle_tips",
        "insights",
        "product_recommendation",
        "encouragement"
    ]
}
