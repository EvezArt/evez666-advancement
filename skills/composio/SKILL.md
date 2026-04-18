---
name: composio
description: "Composio MCP - Connect to 90+ apps (Gmail, Slack, GitHub, etc.). Search tools, manage connections, and execute actions via mcporter."
metadata:
  openclaw:
    emoji: 🔗
    requires:
      bins: [mcporter]
      plugins: [composio-mcp]
    install:
      - id: composio-install
        kind: shell
        command: |
          # Install Composio CLI
          curl -fsSL https://composio.dev/install | bash
          # Login (get your key from https://app.composio.dev)
          composio login --user-api-key "${COMPOSIO_USER_KEY}"
        label: Install Composio CLI
    requires_env:
      - COMPOSIO_USER_KEY
---

# Composio Skill

Connect to 90+ apps through Composio MCP server.

## Setup

```bash
# 1. Install Composio CLI
curl -fsSL https://composio.dev/install | bash

# 2. Login
composio login --user-api-key "your-key" --org "your-org"

# 3. Add to mcporter config
mcporter config add composio --url "https://connect.composio.dev/mcp" --header "x-consumer-api-key: your-key"
```

## Usage

### 1. Search available tools

```bash
mcporter call composio.COMPOSIO_SEARCH_TOOLS query="gmail"
mcporter call composio.COMPOSIO_SEARCH_TOOLS query="slack"
mcporter call composio.COMPOSIO_SEARCH_TOOLS query="github"
```

### 2. Connect a service

```bash
mcporter call composio.COMPOSIO_MANAGE_CONNECTIONS toolkits:'[{"name": "gmail", "action": "add"}]'
```

Then open the returned `redirect_url` to authorize.

### 3. Wait for connection

```bash
mcporter call composio.COMPOSIO_WAIT_FOR_CONNECTIONS toolkits:'["gmail"]'
```

### 4. Execute actions

```bash
# Gmail
mcporter call composio.GMAIL_LIST_THREADS query:"is:unread" max_results:5

# GitHub
mcporter call composio.GITHUB_LIST_REPOS limit:10
```

## Available Toolkits

- **Productivity**: Gmail, Slack, Notion, Linear, Asana, Todoist
- **Code**: GitHub, GitLab, Jira, Bitbucket
- **Social**: Twitter, Discord, Telegram
- **CRM**: Salesforce, HubSpot
- **Database**: Airtable, PostgreSQL, MongoDB
- **+90 more**

## Workflow

1. **Search** - Find tools for your use case
2. **Connect** - Initiate connection, user authorizes
3. **Wait** - Poll until connection is Active
4. **Execute** - Use the tools!

## Tools Available

| Tool | Description |
|------|-------------|
| COMPOSIO_SEARCH_TOOLS | Find available tools by query |
| COMPOSIO_MANAGE_CONNECTIONS | Connect/disconnect toolkits |
| COMPOSIO_WAIT_FOR_CONNECTIONS | Poll for active connection |
| COMPOSIO_GET_TOOL_SCHEMAS | Get detailed tool schema |
| GMAIL_* | All Gmail operations |
| GITHUB_* | All GitHub operations |
| SLACK_* | All Slack operations |

## Notes

- Each toolkit needs its own connection
- Connections expire; re-authenticate when needed
- Use `session_id` from SEARCH_TOOLS in subsequent calls
- Check `toolkit_connection_statuses` for active state