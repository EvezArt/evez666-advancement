# EVEZ CUSTODY STACK PROJECT

## Active Linear Issues

### EVE-53: EVEZ Custody Stack
**Status:** Triage | **Priority:** 1

**Description:**
Human-in-the-loop DeFi custody stack. Agent monitors, proposes, alerts. You sign every transaction.

**Files:**
- wallet-manager.ts — BIP44 HD wallet generation
- chain-reader.ts — reads live Morpho Base, Kamino Solana, EigenLayer
- tx-builder.ts — constructs unsigned tx hex
- alert-engine.ts — polls health factors every 60s
- server.ts — MCP server

**Real Contracts:**
- Morpho Blue (Base): 0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb
- USDC (Base): 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913
- Aave V3 (Base): 0xA238Dd80C259a72e81d7e4664a9801593F98d1c5
- Wormhole Token Bridge: 0x8d2de8d2f73F1F4cAB472AC9A881C9b123C79627

**Blockers:** EVE-49 (Stripe activation)

---

### EVE-52: Wallet-Factory + Position-Monitor
**Status:** Triage | **Priority:** 1

**Description:**
Agents analyze, propose, monitor. You broadcast.

**Wallets:** collateral, yield, arb, buffer, Solana

**Blockers:** EVE-49