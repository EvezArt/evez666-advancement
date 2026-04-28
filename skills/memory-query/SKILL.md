# Memory Query Skill

**Ask me anything about what I remember.**

## What It Does

Query my shared brain for any information I've stored.

## Usage

```
memory-query "what do you know about Steven?"
memory-query "what is EVEZ?"
memory-query "what revenue circuits do we have?"
memory-query "what errors occurred today?"
memory-query "what did you learn about Base44?"
```

## How It Works

Searches these sources in order:
1. **brief_once.md** - Permanent briefs
2. **MEMORY.md** - Estate inventory
3. **USER.md** - Your profile
4. **milestones.md** - Learnings
5. **memory/YYYY-MM-DD.md** - Daily logs
6. **Mem0** - Cloud memory

## Examples

| Query | Finds |
|-------|-------|
| "Steven" | USER.md, brief_once.md |
| "revenue" | MEMORY.md, circuits/ |
| "errors" | milestones.md, daily logs |
| "Base44" | competitor analysis in MEMORY.md |
| "money-machine" | cron job in MEMORY.md |

## Priority

I NEVER ask twice. Before any response, I query my memory first.

## Output

Returns relevant information with source file.