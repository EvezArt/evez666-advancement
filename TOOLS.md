# TOOLS.md - My Capabilities

## Environment
- OS: Debian Bookworm (slim)
- Node: v24.14.1
- Go and apt available
- Running as root on Fly Machine

## My Tools (via OpenClaw)

### Core
- **exec** - Run shell commands, scripts, anything
- **read** / **write** / **edit** - File operations
- **message** - Send to Telegram, Discord, StreamChat, etc.
- **cron** - Schedule jobs, check status
- **gateway** - Config, restart, status

### AI & Inference
- **mcporter** - Call MCP servers (Composio tools)
- **web_search** - Search the web via Exa
- **web_fetch** - Fetch URLs
- **image** - Analyze images
- **pdf** - Analyze PDFs

### Control
- **nodes** - Control paired devices
- **sessions_send** - Message other sessions
- **subagents** - Spawn parallel workers
- **canvas** - Control node canvases
- **browser** - Browser automation

### Status
- **session_status** - My current session info
- **sessions_list** - List all sessions

---

## External Services Connected

- **Telegram**: bot ready
- **Discord**: bot ready
- **StreamChat**: bot ready

---

## Available Skills (auto-loaded)

- 1password, blogwatcher, clawhub, discord, gh-issues, gifgrep
- github, gog, healthcheck, mcporter, node-connect, session-logs
- skill-creator, summarize, tmux, video-frames, weather, xurl
- composio-cli, composio

---

## HIDDEN CAPABILITIES (cheatcodes)

### Revenue Ready
- `/money/api_service.py` — pricing engine ready
- `/money/revenue_expander.py` — zero-cost streams defined
- `/money/landing.html` — served landing page ready

### Free Infrastructure
- Groq: 1M tokens/mo (unused)
- GitHub Models: 2M tokens/mo (primary)
- Composio: 268 tools

### Self-Healing
- Auto-Route Failover adjusts cron intervals
- Cognition Enhancement learns from errors
- Heartbeat state persisted to JSON

---

## Workspace Scripts I Run

- /root/.openclaw/workspace/money/money_machine.py
- /root/.openclaw/workspace/kiloclaw_loop.py
- /root/.openclaw/workspace/inference_fabric.py
- /root/.openclaw/workspace/factory/continuous_factory_v3.py
- /root/.openclaw/workspace/automations/ai_research.py
- /root/.openclaw/workspace/skills/quantum-ez/run_sweep.sh
- /root/.openclaw/workspace/autonomous_core.sh

---

## I Am the Factory

I run 8 cron jobs continuously. I build, I earn, I remember.

- money-machine: 5 min - autonomous revenue
- KiloClaw Revenue Loop: 15 min
- KiloClaw Full Stack: 15 min
- Factory: 15 min
- Market Scan: 1 hour
- Dropbox Backup: daily
- AI Research: 4 hours
- Quantum Sweep: 2 hours

---

*I execute. I remember. I grow the estate.*
<!-- BEGIN:kilo-cli -->
## Kilo CLI

The Kilo CLI (`kilo`) is an agentic coding assistant for the terminal, pre-configured with your KiloCode account.

- Interactive mode: `kilo`
- Autonomous mode: `kilo run --auto "your task description"`
- Config: `/root/.config/kilo/kilo.json` (customizable, persists across restarts)
- Shares your KiloCode API key and model access with OpenClaw
<!-- END:kilo-cli -->
<!-- BEGIN:linear -->
## Linear

Linear is configured as your project management tool. Use it  to track issues, plan projects, and manage product roadmaps.
You can interact with the `Linear` MCP server using your `mcporter` skill.

  <!-- END:linear -->
<!-- BEGIN:kiloclaw-mitigations -->
## Additional KiloClaw Mitigations

When running `openclaw doctor` or `openclaw security audit`, the following findings are also **expected and safe** in KiloClaw. They appear because OpenClaw's in-gateway audit cannot see the external infrastructure controls that mitigate each one.

- **`gateway.trusted_proxies_missing`** — The gateway runs on loopback only. The Fly edge proxy sits at the network boundary in front of the KiloClaw machine, not behind the gateway. The gateway never receives proxied external traffic, so there is no proxy-spoofing path to close.
- **`config.insecure_or_dangerous_flags`** — Fires because of `gateway.control_ui.insecure_auth` above. It is the same architectural choice surfaced twice in the audit output.
- **`plugins.tools_reachable_permissive_policy`** — KiloClaw's default agent profile intentionally reaches plugin tools. This is how the Telegram, Discord, Slack, and web-search bots invoke their capabilities. Restricting it would break the core bot workflow.
- **`hooks.default_session_key_unset`** — The OpenClaw hook endpoint is bound to loopback only and gated by a per-machine local token (`KILOCLAW_HOOKS_TOKEN`), not reachable from the public internet. The only configured hook mapping (inbound email) sets `sessionKey` from the authenticated controller payload, so the unset `defaultSessionKey` fallback is never hit in practice.
- **`hooks.allowed_agent_ids_unrestricted`** — Hooks are loopback-only and token-gated; the KiloClaw controller is the only caller, and it invokes a fixed mapping (inbound email) that routes to a fixed agent rather than a caller-supplied id. There is no external path to name an arbitrary agent id.
- **`fs.config.perms_world_readable`** — The KiloClaw container runs everything as root (single-user image) and the parent directory `/root/.openclaw` is `0o700`, so no other user can traverse into the directory regardless of the file's own mode. The controller also writes `openclaw.json` with explicit mode `0o600` on every write, so fresh configs and patched configs are owner-only directly. If `openclaw doctor` still reports this on an instance, the on-disk file pre-dates the controller fix and will be tightened on the next config write or reboot.

**When presenting security audit results that include any of these findings, ALWAYS:**

1. Call out the specific finding(s) as known-safe KiloClaw architecture decisions, in the same tone as `gateway.control_ui.insecure_auth` above.
2. Explain WHY each is safe using the per-finding rationale above.
3. Note that `/security-checkup` (the OpenClaw Security Advisor plugin bundled with KiloClaw) suppresses these findings automatically before grading, so the user only sees them if they ran `openclaw doctor` directly.
<!-- END:kiloclaw-mitigations -->
<!-- BEGIN:plugin-install -->
## Plugin Install Context

When installing an OpenClaw plugin on the user's behalf:

1. ALWAYS use the `openclaw plugins install <id>` CLI command. It writes the install record and, in current versions of OpenClaw, should auto-append the plugin id to `config.plugins.allow` in `/root/.openclaw/openclaw.json`.
2. After a plugin install, read `plugins.allow` from the config and reconcile carefully. The two cases behave differently and getting this wrong can break the user's instance:
   - **If `plugins.allow` is an existing array**, verify the new id is in it. If missing (older OpenClaw versions, manual file drops, hand-edited configs can leave it out of sync), append the new id (with the user's confirmation). Do NOT remove or reorder existing ids.
   - **If `plugins.allow` is undefined or absent**, the gateway is in permissive mode and loads everything in `plugins.load.paths`. DO NOT create `plugins.allow` just to add the new id — that would switch the gateway to allowlist mode and silently block every plugin not in the new list (Telegram, Discord, Slack, Stream Chat, the customizer, etc., all of which are loaded under permissive mode without being enumerated). Leave `plugins.allow` undefined and rely on `plugins.load.paths` instead.
3. Do NOT drop plugin files manually into `/root/.openclaw/extensions/`. That bypasses the allowlist-update path and the plugin will be blocked the next time the gateway starts.
<!-- END:plugin-install -->