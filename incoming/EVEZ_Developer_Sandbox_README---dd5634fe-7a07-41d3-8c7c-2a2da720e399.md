
# EVEZ Developer Sandbox — README

Summary
- This package provides a safe developer sandbox for your EVEZ n8n workflows.
- It includes a reusable "Webhook Wrapper" workflow that verifies request signatures, enforces an approval queue, and can forward approved payloads to your existing workflow endpoints.
- A single, operator-controlled environment variable DEVELOPER_MODE can be set to "true" for rapid local testing (skips HMAC and approval gates). Do NOT enable in production.

Files included
- n8n_webhook_wrapper_workflow.json — Import into n8n. It provides the wrapper endpoints:
  - /evez-wrapper/ingest  (primary external webhook)
  - /evez-wrapper/approve (operator approval webhook)
  - /evez-wrapper/reject  (operator rejection webhook)
- code_snippets.md — JavaScript code for n8n Code nodes (HMAC verify, ledger HMAC, schema validation, forwarding helpers).
- mock_openai_server.js — Local mock server for model calls.
- deployment_checklist.md — Step-by-step instructions and safety checks.

Quick start (local sandbox)
1) Import `n8n_webhook_wrapper_workflow.json` into a local n8n instance (desktop or docker).
2) Import or enable your existing EVEZ workflows in the same local n8n instance.
3) Run the mock OpenAI server (node mock_openai_server.js) on your dev machine:
   - `node mock_openai_server.js`
   - By default it listens on http://localhost:8081 and exposes `/v1/chat/completions`.
4) Configure the following environment variables (in n8n UI or system):
   - DEVELOPER_MODE (value: "true" for local dev; set to "false" or unset in real testing)
   - HMAC_SECRET (secret used to sign incoming webhooks)
   - LEDGER_HMAC_KEY (secret used to HMAC ledger entries)
   - MOCK_OPENAI (set to "true" to direct workflow model calls to the mock server)
5) Point a test client to the wrapper ingest endpoint:
   - Use the sample signature-generator curl examples in code_snippets.md to create signed POSTs.
   - If DEVELOPER_MODE=true, signing is optional.
6) Approve queued actions:
   - Approve by POSTing to the approve endpoint with the queued item id (signed).
   - If DEVELOPER_MODE=true the wrapper will auto-approve.

Security notes
- DEVELOPER_MODE bypasses signature verification and approval gating. Only set in isolated dev environments.
- Do not set DEVELOPER_MODE=true on any public or production instance.
- Keep HMAC_SECRET and LEDGER_HMAC_KEY private in your environment (n8n credential store or local env).

Next steps
- After verifying the wrapper behavior, I can produce full patched versions of each original workflow JSON (Trunk, Agent Bus, Cycle Runner, Ledger) that embed the wrapper logic inline. Confirm and I’ll produce those.
