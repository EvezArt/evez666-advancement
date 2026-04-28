#!/usr/bin/env python3
"""
TOOL REGISTRY - Composio mapping layer
All tools routed through here
"""

TOOLS = {
    # Email
    "gmail.send": "GMAIL_SEND_EMAIL",
    "gmail.fetch": "GMAIL_FETCH_EMAILS",
    
    # LinkedIn
    "linkedin.send": "LINKEDIN_SEND_MESSAGE",
    "linkedin.fetch": "LINKEDIN_GET_MESSAGES",
    
    # Chat
    "slack.send": "SLACK_SEND_MESSAGE",
    "slack.history": "SLACK_FETCH_CONVERSATION_HISTORY",
    "discord.send": "DISCORD_SEND_MESSAGE",
    "telegram.send": "TELEGRAM_SEND_MESSAGE",
    
    # Payments
    "stripe.create_link": "STRIPE_CREATE_PAYMENT_LINK",
    "stripe.list_payments": "STRIPE_LIST_CHARGES",
    "stripe.create_product": "STRIPE_CREATE_PRODUCT",
    
    # CRM
    "airtable.create": "AIRTABLE_CREATE_RECORD",
    "airtable.update": "AIRTABLE_UPDATE_RECORD",
    "salesforce.create": "SALESFORCE_CREATE_LEAD",
    
    # Tasks
    "linear.create": "LINEAR_CREATE_LINEAR_ISSUE",
    "linear.update": "LINEAR_UPDATE_ISSUE",
    "notion.create": "NOTION_CREATE_PAGE",
    
    # Storage
    "supabase.insert": "SUPABASE_INSERT_ROW",
    "supabase.query": "SUPABASE_SELECT",
}

def route(call):
    """Route a tool call to Composio"""
    tool = call.get("tool")
    args = call.get("args", {})
    
    if tool not in TOOLS:
        return {"error": f"Unknown tool: {tool}"}
    
    composio_tool = TOOLS[tool]
    
    # Would call: subprocess.run(["mcporter", "call", f"composio.{composio_tool}", ...])
    return {
        "tool": tool,
        "composio": composio_tool,
        "args": args,
        "status": "ready"
    }

# Example usage
if __name__ == "__main__":
    import json
    
    # Send email offer
    call = {
        "tool": "gmail.send",
        "args": {
            "to": "lead@test.com",
            "subject": "AI Revenue System",
            "body": "Here's your link..."
        }
    }
    print(json.dumps(route(call), indent=2))