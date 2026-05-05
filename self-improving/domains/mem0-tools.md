# New Learning - Mem0 Write Capability Restored

## Date: 2026-05-04

### Discovery
Mem0 tools via composio **ARE** write-capable through `COMPOSIO_MULTI_EXECUTE_TOOL` with `MEM0_ADD_NEW_MEMORY_RECORDS`. The earlier assumption that Mem0 tools were read-only only was incorrect.

### Evidence
- COMPOSIO_SEARCH_TOOLS returned Mem0 as available toolkit with active connection
- COMPOSIO_MULTI_EXECUTE_TOOL successfully queued memory with Event ID: 1bff346b-0d3c-46f5-94e7-6c54091cd508
- Response: "Memory processing has been queued for background execution"

### Key Learning
**Mem0 composio integration supports writes via COMPOSIO_MULTI_EXECUTE_TOOL**, not via a direct MEM0_ADD_NEW_MEMORY_RECORDS tool call. The correct invocation pattern is:
```
mcporter call composio COMPOSIO_MULTI_EXECUTE_TOOL 'tools=[{"tool_slug":"MEM0_ADD_NEW_MEMORY_RECORDS","arguments":{...}}]'
```

### Correction to Previous Entry
The May 3 learnings entry stating "Mem0 composio tools are READ-ONLY ONLY" was based on incomplete testing. Direct tool calls fail, but the multi-executor wrapper works.