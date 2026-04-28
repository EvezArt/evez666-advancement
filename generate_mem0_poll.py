#!/usr/bin/env python3
import json

payload = {
    "tools": [
        {
            "tool_slug": "MEM0_GET_EVENT_STATUS_BY_EVENT_ID",
            "arguments": {"event_id": "0ebf667f-3298-4ed2-a8ea-6a914b57db93"}
        },
        {
            "tool_slug": "MEM0_GET_EVENT_STATUS_BY_EVENT_ID",
            "arguments": {"event_id": "c7a842cf-def5-401d-a8c3-edaed4767e3c"}
        }
    ],
    "memory": {"mem0_poll": ["Polling event status for batch save at 18:16Z"]},
    "sync_response_to_workbench": False,
    "current_step": "POLLING_EVENT_STATUS",
    "session_id": "hill"
}
print(json.dumps(payload, ensure_ascii=False, separators=(',', ':')))
