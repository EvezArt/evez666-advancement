1. Copy `.env.example` to `.env` and replace all placeholders.
2. Start the stack with `docker compose -f docker-compose.redis.yml up -d --build`.
3. Import `n8n-master-orchestrator-redis.json` and `n8n-watchdog-redis.json` into n8n.
4. In n8n, bind a real OpenAI credential to `OpenAI Chat Model` and a real GitHub credential to the GitHub node(s).
5. Commit `.github/workflows/evez-agent.yml` into the target repository.
6. Add `OPENAI_API_KEY` and `N8N_WEBHOOK_URL` as GitHub Actions secrets in the repository.
7. Configure the Custom GPT with `custom-gpt-openapi.yaml` and `evez-master-system-prompt.txt`.
8. Run `./smoke_test_redis.sh`.
9. Activate the n8n workflows only after the smoke test passes.

Notes:
- The Redis state service replaces the earlier workflow static-data store for run state and watchdog counters.
- The n8n webhook base assumed here is `http://localhost:5678/webhook`.
- The GitHub Actions workflow still requires repository-side secrets and permission to write contents/issues/actions.
