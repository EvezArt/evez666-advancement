1. Start the stack with Docker Compose after copying `.env.example` to `.env` and replacing placeholders.
2. Import the master orchestrator JSON into n8n.
3. Import the watchdog JSON into n8n.
4. Create n8n credentials for OpenAI and GitHub, then bind those credentials to the imported nodes.
5. Place `evez-agent.yml` in `.github/workflows/evez-agent.yml` in the target repository.
6. Add repository secrets for `OPENAI_API_KEY` and `N8N_WEBHOOK_URL` in GitHub.
7. Create or edit the Custom GPT, add the system prompt, then import the OpenAPI schema as an action.
8. In the GPT editor, test the action routes in Preview mode.
9. Run `./smoke_test.sh http://YOUR_N8N_HOST/webhook`.
10. Activate the two n8n workflows only after the smoke test passes.
