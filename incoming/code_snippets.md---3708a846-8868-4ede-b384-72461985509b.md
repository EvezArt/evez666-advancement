
# n8n Code Node Snippets and Helpers

Use these exact JS snippets inside n8n Code nodes. They are written to be pasted as the Code field in n8n "Function / Code" nodes (type: n8n-nodes-base.code). Adjust node names and variable access as needed.

1) HMAC-SHA256 Verification (use in Verify-HMAC node)
- Purpose: verify header X-EVEZ-SIG, otherwise reject. Honors DEVELOPER_MODE env var to bypass in local dev.

JS:
const crypto = require('crypto');
const raw = $input.first().binary ? Buffer.from($input.first().binary['data'].data, 'base64') : Buffer.from(JSON.stringify($input.first().json));
const sigHeader = $json["headers"]?.["x-evez-sig"] || $json["headers"]?.["X-EVEZ-SIG"] || '';
const secret = process.env.HMAC_SECRET || '';
const dev = (process.env.DEVELOPER_MODE || '').toLowerCase() === 'true';
function safeCompare(a, b) {
  if (!a || !