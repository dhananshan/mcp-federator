# mcp-federator
MCP-Federator is a federated Model Context Protocol (MCP) agent that connects to multiple upstream MCP servers, aggregates or proxies their model contexts, and re-exposes them through a unified MCP-compatible interface. It acts as both a client and a server, enabling centralized access to distributed model context data.

# Instruction
create a .env and add your secrets. In this example we use github and atlassian MCP servers so I am adding required secrets for them. 

`export AZURE_OPENAI_API_HOST="<YOUR VALUE>"`

`export AZURE_OPENAI_API_VERSION="<YOUR VALUE>"`

`export AZURE_OPENAI_DEPLOYMENT_NAME="<YOUR VALUE>"`

`export AZURE_OPENAI_API_KEY="<YOUR VALUE>"`

`export GITHUB_PERSONAL_ACCESS_TOKEN="<YOUR VALUE>"`

`export GITHUB_HOST="<YOUR VALUE>"`

`export CONFLUENCE_URL="<YOUR VALUE>"`

`export CONFLUENCE_USERNAME="<YOUR VALUE>"`

`export CONFLUENCE_API_TOKEN="<YOUR VALUE>"`

`export JIRA_URL="<YOUR VALUE>"`

`export JIRA_USERNAME="<YOUR VALUE>"`

`export JIRA_API_TOKEN="<YOUR VALUE>"`
