#!/usr/bin/env python3
import argparse, pathlib, json

def render(template_path: pathlib.Path, **kwargs) -> str:
    return template_path.read_text().format(**kwargs)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--role", required=True)
    parser.add_argument("--goal", required=True)
    parser.add_argument("--task", required=True)
    parser.add_argument("--outdir", default="output/subagents")
    args = parser.parse_args()

    root = pathlib.Path(__file__).resolve().parents[1]
    tpl = root / "templates"
    out = root / args.outdir / args.name
    out.mkdir(parents=True, exist_ok=True)

    mapping = {
        "AGENT.md": "agent.md.tpl",
        "TASK.md": "task.md.tpl",
        "SOUL.md": "soul.md.tpl",
        "TOOLS.md": "tools.md.tpl",
        "MEMORY.md": "memory.md.tpl",
        "DAEMON.md": "daemon.md.tpl",
        "PROMPT.md": "prompt.md.tpl",
    }
    kwargs = {
        "name": args.name,
        "role": args.role,
        "goal": args.goal,
        "task": args.task,
    }
    for target, source in mapping.items():
        (out / target).write_text(render(tpl / source, **kwargs))
    manifest = {
        "name": args.name,
        "role": args.role,
        "goal": args.goal,
        "task": args.task,
        "generated_at": __import__("datetime").datetime.utcnow().isoformat() + "Z"
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(str(out))

if __name__ == "__main__":
    main()
