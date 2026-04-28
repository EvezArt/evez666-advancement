# EVEZ Self-Updating Inference System

A self-improving AI system that automatically trains, evaluates, and redeploys itself using free-tier services (GitHub Actions, Hugging Face, Vercel).

## Architecture

```
[Vercel v0 App]  --> triggers --> [GitHub Actions] --> [Hugging Face Model] --> [EVEZ Runtime]
    ^                                                               |
    |___________________________ feedback __________________________|
```

## Components

- `control/trainer.py`: LoRA fine-tuning loop
- `control/deployer.py`: Pushes updated model to Hugging Face
- `.github/workflows/train.yml`: Automated training on schedule/manual dispatch
- `modeling_evez.py`: Hugging Face compatible model wrapper
- `configuration_evez.py`: Model configuration
- `__init__.py`: Registers the model with transformers

## Setup

1. Fork this repository
2. Add secrets:
   - `HF_TOKEN`: Hugging Face write token
   - `GITHUB_TOKEN`: GitHub token with workflow permissions
3. Optionally deploy the Vercel v0 frontend (see prompts below)

## Usage

- Trigger training manually via GitHub Actions UI or workflow dispatch
- System trains on schedule (every 6 hours by default)
- Updated model automatically available via Hugging Face Inference API