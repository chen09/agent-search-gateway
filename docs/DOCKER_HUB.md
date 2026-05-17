# Docker Hub Publishing

This project can publish the `retrieval-api` service image to Docker Hub. SearXNG, Valkey, and optional Jina Reader continue to use their upstream images through Docker Compose.

## Maintainer Setup

Create a Docker Hub repository:

```text
chen920/agent-search-gateway
```

Create a Docker Hub access token, then add these GitHub repository secrets:

```text
DOCKERHUB_USERNAME=<dockerhub-username>
DOCKERHUB_TOKEN=<docker-hub-access-token>
```

Required Docker Hub token permissions:

- Image publishing only: public repository read/write is enough.
- Image publishing plus Docker Hub Overview sync: public repository read/write/delete is required by the Docker Hub description update action.

The workflow is:

```text
.github/workflows/docker-image.yml
```

If either GitHub secret is missing, the workflow exits successfully after printing a skip notice. This keeps release tags from failing before Docker Hub automation is configured.

It publishes multi-architecture images for:

- `linux/amd64`
- `linux/arm64`

## Release Flow

Push a release tag:

```bash
git tag -a v0.2.1 -m "v0.2.1"
git push origin v0.2.1
```

Expected Docker tags for `v0.2.1`:

```text
chen920/agent-search-gateway:0.2.1
chen920/agent-search-gateway:0.2
chen920/agent-search-gateway:latest
```

You can also run the `Docker Image` workflow manually from GitHub Actions and provide an `image_tag`, for example `dev`.

## Docker Hub Overview

The public Docker Hub page should also explain `.env` setup because many users discover the image there before reading GitHub.

The source file for Docker Hub's long overview is:

```text
docs/DOCKER_HUB_OVERVIEW.md
```

It is synchronized by:

```text
.github/workflows/dockerhub-description.yml
```

The short Docker Hub description is:

```text
Self-hosted search and extraction gateway for AI agents
```

## User Setup With Prebuilt Image

Users still need their own `.env`. The image does not contain API keys.

```bash
git clone https://github.com/chen09/agent-search-gateway.git
cd agent-search-gateway
cp .env.example .env
```

Generate local secrets:

```bash
SEARXNG_SECRET="$(openssl rand -hex 32)" RETRIEVAL_API_KEY="$(openssl rand -hex 32)" \
  perl -0pi -e 's/^SEARXNG_SECRET=.*/SEARXNG_SECRET=$ENV{SEARXNG_SECRET}/m; s/^RETRIEVAL_API_KEY=.*/RETRIEVAL_API_KEY=$ENV{RETRIEVAL_API_KEY}/m' .env
```

For the default image-based Compose stack, keep these values in `.env`:

```dotenv
SEARXNG_BASE_URLS=http://searxng:8080
SEARXNG_HOST_PORT=8888
TAVILY_ENABLED=false
BRAVE_ENABLED=false
RERANKER_ENABLED=false
```

See [ENVIRONMENT.md](ENVIRONMENT.md) for the full `.env` guide.

Start from Docker Hub instead of building locally:

```bash
docker compose -f docker-compose.image.yml up -d
```

The default image is:

```text
docker.io/chen920/agent-search-gateway:latest
```

If you maintain a fork under another Docker Hub namespace, set the image explicitly:

```bash
RETRIEVAL_API_IMAGE=docker.io/<dockerhub-username>/agent-search-gateway:0.2.1 \
  docker compose -f docker-compose.image.yml up -d
```

Verify:

```bash
curl http://127.0.0.1:8010/healthz
curl 'http://127.0.0.1:8888/search?q=searxng&format=json' | head
```

## Secret Policy

- Never bake `.env`, provider keys, logs, extracted content, or cache data into the image.
- Keep hosted provider keys in the runtime `.env` only.
- Keep Tavily and Brave disabled by default unless the operator explicitly configures keys and quota limits.
