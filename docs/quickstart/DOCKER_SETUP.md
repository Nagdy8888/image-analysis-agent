# Docker Setup

The project is intended to run with Docker. Backend and frontend each run in a container.

## Prerequisites

- Docker and Docker Compose installed
- Project root `.env` with at least `OPENAI_API_KEY` (for analysis in later phases)

## Build and run

From the **project root**:

```bash
docker compose up --build
```

- **Frontend:** http://localhost:3000  
- **Backend API:** http://localhost:8000  
- **Health check:** http://localhost:8000/api/health  

This is the standard way to run the Image Analysis Agent.  

## Environment variables

- **Backend** uses the root `.env` file via `env_file: .env` in docker-compose.
- **Frontend** gets `NEXT_PUBLIC_API_URL` at **build time**. Default in docker-compose is `http://localhost:8000` so the browser (on your machine) can call the API.

To use a different API URL (e.g. production backend), rebuild with a build arg:

```bash
docker compose build --build-arg NEXT_PUBLIC_API_URL=https://api.yoursite.com
docker compose up -d
```

## Persisted uploads

Uploaded images are stored in a Docker volume `backend_uploads`. They persist across `docker compose down`. To remove them:

```bash
docker compose down -v
```

## Logs and troubleshooting

- View logs: `docker compose logs -f`
- Backend only: `docker compose logs -f backend`
- Restart after changing code: `docker compose up --build -d`

## Building for a registry

To push images to a registry (e.g. for deployment):

```bash
# Tag and push (replace with your registry path)
docker compose build
docker tag image-analysis-agent-backend your-registry/image-analysis-agent-backend:latest
docker tag image-analysis-agent-frontend your-registry/image-analysis-agent-frontend:latest
docker push your-registry/image-analysis-agent-backend:latest
docker push your-registry/image-analysis-agent-frontend:latest
```

Run the backend with the same env vars (mount or pass `.env`). Run the frontend with `NEXT_PUBLIC_API_URL` set to the public URL of your backend.
