# Image Analysis Agent

AI-powered image tagging: upload product images, get structured tags (season, theme, colors, etc.) via LangGraph and OpenAI, store in Supabase, search in the UI.

## Run with Docker

The project runs with Docker. From the repo root:

```bash
docker compose up --build
```

- **App:** http://localhost:3000  
- **API:** http://localhost:8000  

Set `OPENAI_API_KEY` (and optionally `DATABASE_URI` for Supabase) in a `.env` file at the project root. See [docs/quickstart/DOCKER_SETUP.md](docs/quickstart/DOCKER_SETUP.md) for full Docker instructions, env vars, and pushing to a registry.

## Docs and setup

- [Quickstart (Docker + local)](docs/quickstart/README.md)
- [Phase setup guides](docs/plans/README.md)
- [Architecture and API](docs/architecture/README.md)
