"""Tool schemas for LLM function calling."""
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": "Search the e-commerce product catalog for items matching the query. Use this when the user asks about products, wants to find something to buy, or mentions shopping.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The product name, description, or keywords to search for."
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Optional maximum price filter in USD."
                    },
                    "category": {
                        "type": "string",
                        "description": "Optional category filter (e.g., 'Electronics', 'Pet Supplies', 'Home & Kitchen')."
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_to_cart",
            "description": "Adds a product to the user's shopping cart. Use this when the user explicitly wants to add something to their cart.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "The product ID (ASIN or product_id) to add to the cart."
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "The number of units to add, defaults to 1.",
                        "default": 1
                    }
                },
                "required": ["product_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "grokipedia_search",
            "description": "Search Grokipedia for research information, facts, or educational content. Use this when the user asks 'what is', 'how does', 'explain', or wants to learn about something. Do NOT use this for product searches or shopping questions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The research topic, question, or subject to search for."
                    }
                },
                "required": ["query"]
            }
        }
    }
]

