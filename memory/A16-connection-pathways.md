# A16 → KiloClaw Connection Pathways

**Created:** 2026-04-23 23:09 UTC
**Purpose:** Document connection methods for Termux agent on A16 to reach KiloClaw

---

## CURRENT STATUS

**KiloClaw Gateway:**
- Running on port 3001 (loopback only — not publicly accessible)
- Needs tunnel or public deployment for A16 connectivity

---

## PATHWAY OPTIONS

### **PATHWAY 1: Fly.io Deployment (Recommended — Permanent)**
**Status:** Ready to deploy, awaiting Fly.io API token

**Steps:**
1. Obtain Fly.io token: `flyctl auth token` (on machine with flyctl access)
2. Share token with KiloClaw
3. KiloClaw will:
   - Create `fly.toml` for EVEZ services
   - Deploy to existing Fly app `inst-ced32ada5c2c3a42e980`
   - Expose ports:
     - 8080 → HTTP/HTTPS (EVEZ Platform)
     - 3847 → HTTP (ROM-S API)
     - 3001 → TCP (OpenClaw Gateway for Termux)
4. A16 Termux connects to `https://<your-app>.fly.dev` as OPENCLAW_URL

**Benefits:** Stable, permanent, auto-HTTPS, scalable

---

### **PATHWAY 2: Localtunnel (Quick Fix — Temporary)**
**Status:** Previously working, now down (tunnel expired)

**Steps to restore:**
```bash
# On KiloClaw server:
npm install -g localtunnel
lt --port 3001 --subdomain <unique-subdomain>
```
**Result:** `https://<unique-subdomain>.loca.lt` → TermuxOPENCLAW_URL

**Drawbacks:** Tunnel can expire, less reliable, requires process to stay alive

---

### **PATHWAY 3: Cloudflared Tunnel (Alternative)**
If you have Cloudflare account:
```bash
# Install cloudflared
cloudflared tunnel --url http://localhost:3001
# Provides a stable *.trycloudflare.com URL
```

---

## REQUIRED INFORMATION FOR A16 SETUP

Once a pathway is active, Termux agent needs:

```bash
export OPENCLAW_URL="<PUBLIC_URL_HERE>"
# Examples:
# Fly.io: https://inst-ced32ada5c2c3a42e980.fly.dev
# Localtunnel: https://my-tunnel.loca.lt
# Cloudflared: https://something.trycloudflare.com
```

---

## BLOCKERS IDENTIFIED

1. **Fly.io token not available** — Interactive login required, no headless token found
2. **Localtunnel process needs restart** — Previous tunnel dead, subdomain possibly taken
3. **Gateway bind is loopback only** — Needs Fly.io config to expose port 3001 publicly

---

## NEXT ACTIONS (Priority Order)

### **P0 — Get a Public Endpoint**
Choose one:
- **A)** Provide Fly.io API token → KiloClaw deploys to Fly (permanent)
- **B)** KiloClaw restarts localtunnel on a new subdomain (temporary)

### **P1 — Connect A16**
Run Termux agent with OPENCLAW_URL pointing to chosen endpoint:
```bash
cd ~/termux-agent
npm install
export OPENCLAW_URL="https://<your-endpoint>"
node termux-agent.js
```

---

## VERIFICATION CHECKLIST

- [ ] KiloClaw gateway reachable from internet (curl https://<url>/health)
- [ ] Termux agent connects (logs show "Connected to OpenClaw gateway")
- [ ] A16 appears in `nodes list` or `nodes status`
- [ ] Camera/screen/location requests work

---

**Document saved.** To proceed, tell me which pathway you prefer and provide any needed credentials (Fly token or confirm localtunnel restart).