#!/usr/bin/env python3
import argparse, datetime as dt, json, pathlib, random

def utcnow():
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def load_config(path):
    return json.loads(pathlib.Path(path).read_text())

def append_log(root: pathlib.Path, line: str):
    log = root / "logs" / "daemon.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a") as f:
        f.write(line + "\n")

def chronicle_entry(root: pathlib.Path, mode: str, agent: dict, action: str):
    ts = utcnow()
    entry = {
        "timestamp": ts,
        "mode": mode,
        "agent": agent["name"],
        "action": action,
        "result": random.choice(["advanced","logged","challenged","archived","reviewed"]),
        "next": random.choice([
            "continue current loop",
            "spawn subagent",
            "review evidence",
            "archive stale outputs",
            "benchmark candidate"
        ])
    }
    out = root / "output" / "chronicle" / f"{ts}_{agent['name']}_{action}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(entry, indent=2))
    append_log(root, f"{ts} [{mode}] {agent['name']}::{action} -> {entry['result']}")
    return entry

def run_mode(root, config, mode):
    enabled_agents = [a for a in config["agents"] if a.get("enabled")]
    entries = []
    for agent in enabled_agents:
        for action in agent.get("daemon_actions", []):
            if mode == "daemon_pass" or mode == "once":
                entries.append(chronicle_entry(root, mode, agent, action))
            elif mode == "maintenance_pass" and agent["name"] in {"chronicler","archivist","skeptic"}:
                entries.append(chronicle_entry(root, mode, agent, action))
            elif mode == "hourly_chronicle" and agent["name"] in {"chronicler","coordinator"}:
                entries.append(chronicle_entry(root, mode, agent, action))
            elif mode == "daily_report" and agent["name"] in {"benchmarker","promoter","coordinator"}:
                entries.append(chronicle_entry(root, mode, agent, action))
            elif mode == "weekly_archive" and agent["name"] in {"archivist","chronicler"}:
                entries.append(chronicle_entry(root, mode, agent, action))
    summary = {
        "timestamp": utcnow(),
        "mode": mode,
        "entries_written": len(entries),
        "agents_touched": sorted(set(e["agent"] for e in entries)) if entries else []
    }
    summary_path = root / "output" / f"summary_{mode}_{summary['timestamp'].replace(':','-')}.json"
    summary_path.write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--mode", default="once")
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()

    root = pathlib.Path(__file__).resolve().parents[1]
    config = load_config(args.config)
    mode = "once" if args.once else args.mode
    run_mode(root, config, mode)

if __name__ == "__main__":
    main()
