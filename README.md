# ArtAssetsValidator

A technical artist harness that automatically validates, renames, and generates LODs for 3D assets using AI agents.

Drop an FBX or texture into the watch folder — the pipeline handles the rest.

## What it does

- Validates FBX files against studio naming and poly count conventions
- Auto-renames non-compliant assets
- Generates LOD1/2/3 via Blender headlessly
- Notifies Slack on validation failures
- Logs everything to timestamped files and JSON reports

## Why it exists

Technical artists spend significant time on repetitive asset QA — checking naming conventions, poly budgets, and generating LODs before handoff to engine. This harness automates that loop using an AI validation agent backed by a `CONVENTIONS.md` file that encodes studio rules.

The core idea is **harness engineering**: instead of prompting an AI to do a task, you build the environment around the agent — the right context, tools, and triggers — so it operates correctly without manual intervention.

## Project structure

```
asset-harness/
├── watch_folder/       ← drop assets here
├── logs/               ← timestamped run logs
├── reports/            ← timestamped JSON reports
├── CONVENTIONS.md      ← studio rules (edit this for your pipeline)
├── main.py             ← orchestration + file watcher
├── agents.py           ← all LLM calls (Groq)
├── mesh_utils.py       ← mesh data extraction (Open3D)
├── lod_generator.py    ← Blender headless LOD generation
├── reporter.py         ← JSON report writer
├── logger.py           ← logging setup
└── .env                ← secrets (not committed)
```

## Setup

**Requirements**
- Python 3.12+
- Blender 4.0+
- A Groq API key (free at console.groq.com)
- A Slack webhook URL (optional)

**Install**

```bash
python -m venv .venv
source .venv/bin/activate
pip install watchdog anthropic groq open3d python-dotenv
```

**Configure**

Create a `.env` file in the project root:

```
GROQ_API_KEY=<your-groq-key>
SLACK_WEBHOOK_URL=<your-slack-webhook>
BLENDER_PATH=<path-to-blender-executable>
```

Edit `CONVENTIONS.md` to match your studio's naming and poly budget rules.

**Run**

```bash
python main.py
```

Drop FBX or texture files into `watch_folder/`. The harness will validate, rename, and generate LODs automatically.

## Customizing conventions

All agent behavior is driven by `CONVENTIONS.md`. Edit it to change:
- Naming prefixes
- Poly limits per asset type
- UV requirements

The agent reads this file on every validation call — no code changes needed.
