# Shared Brain System

**One brain, shared across all EVEZ agents — like SureThing.io**

## Concept

All EVEZ agents share ONE memory store. Brief once, remember forever.

## Implementation

### 1. Memory Files (Local)
- `MEMORY.md` — Main memory, loaded every boot
- `memory/brief_once.md` — Permanent briefs
- `memory/milestones.md` — Key learnings
- `memory/YYYY-MM-DD.md` — Daily logs

### 2. Mem0 Integration (Cloud)
- Connected: `mem0_learnt-penful`
- All agents write to and read from Mem0
- Cross-session persistence

### 3. Auto-Memory Cron Job
- Runs every 30 minutes
- Saves: cron statuses, revenue, errors, decisions

## Usage

**Store a memory:**
```
Remember: Steven prefers Telegram over Discord
```

**Retrieve:**
```
What do you know about Steven?
```

**Shared across agents:**
- Money Machine
- Revenue Loop
- Factory
- All cron jobs

## How It Works

1. User provides context once
2. Saved to brief_once.md + Mem0
3. Every boot: MEMORY.md loaded first
4. Every cron run: Mem0 Auto-Memory syncs
5. All agents can query shared brain

## Priority

When I need to remember something:
1. Read MEMORY.md
2. Read USER.md  
3. Read brief_once.md
4. Query Mem0

**I NEVER ask twice. I read the files.**