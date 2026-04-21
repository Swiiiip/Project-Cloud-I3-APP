# Blurmoji

Blurmoji is an emoji guessing game where each wrong guess progressively reveals more image detail until the player solves the daily challenge.

## Gameplay behavior
- Daily challenge with a fixed max attempts count
- Session-scoped progression keyed by `session_id` cookie
- `/render` returns blurred or full image depending on current game state
- Emoji picker is driven by grouped Emoji Kitchen metadata

## Runtime architecture

### Services
- `gateway-api`: public API edge, cookie/session validation, request orchestration
- `game-service`: challenge state lifecycle (`start`, `guess`, `status`)
- `emoji-catalog-service`: supported emoji metadata endpoint
- `render-service`: image processing endpoint; fetches challenge status from `game-service`
- `frontend-web`: NiceGUI application

### Data and infrastructure
- `redis`: session challenge state storage for low-latency read/write gameplay loops
- `mysql`: relational storage target for future history, analytics, and leaderboard workloads
- `azurite`: blob storage target for image assets and rendered variants

### Request ownership
- Public routes stay under `/api/v1/daily/*` on `gateway-api`
- `gateway-api` delegates internally:
  - `/start`, `/guess`, `/get_status` -> `game-service`
  - `/supported_emojis` -> `emoji-catalog-service`
  - `/render` -> `render-service`

## Why these technology choices fit this game

### FastAPI service split
- Keeps each gameplay capability isolated and deployable
- Lets rendering scale independently from state transitions
- Keeps gateway focused on session and API edge behavior

### Redis for challenge state
- Very fast mutable state updates for every guess
- TTL support matches expiring daily-session style state
- Ideal for high-frequency, small payload read/write patterns

### MySQL for relational workloads
- Fits deterministic history and leaderboard queries
- Durable transactional model for future player/account features
- Enables SQL-based reporting without affecting hot gameplay state

### Azurite/blob model for images
- Mirrors production blob-storage workflow locally
- Suitable for immutable image objects and generated render outputs
- Decouples large binary storage from application containers

### Kubernetes primitives
- Deployments/Services: independent horizontal scaling per service
- Ingress: single host entry with path-based routing for API and UI
- ConfigMaps/Secrets: environment-driven runtime and secret management
- CronJobs: scheduled precompute and metadata refresh workflows
- PVC-backed infra: durable MySQL and Azurite volumes

## Final source layout

```
src/
  services/
    gateway/
      app.py
      internal_client.py
      main.py
      session/signed_cookie_session_resolver.py
    game/
      app.py
      main.py
    emoji_catalog/
      app.py
      main.py
    render/
      app.py
      game_service_client.py
      main.py
    common/runtime_env.py
  common/contracts/
    game_contracts.py
  deploy/
    docker/
      Dockerfile.gateway
      Dockerfile.game
      Dockerfile.catalog
      Dockerfile.render
      Dockerfile.frontend
    helm/blurmoji/
      Chart.yaml
      values.yaml
      values.prod.yaml
      templates/*.yaml
  frontend/
    main.py
```

## Environment variables

Use `.env.example` as the reference source of required runtime variables.

Core groups:
- Gateway edge: `API_HOST`, `API_PORT`, `SESSION_COOKIE_SECRET`
- Internal services: `GAME_SERVICE_*`, `CATALOG_SERVICE_*`, `RENDER_SERVICE_*`
- Service discovery: `*_BASE_URL`, `INTERNAL_HTTP_TIMEOUT_SECONDS`
- Frontend: `API_BASE_URL`, `FRONTEND_HOST`, `FRONTEND_PORT`
- Challenge storage: `CHALLENGE_STORAGE_BACKEND`, `REDIS_*`
- Infra secret: `MYSQL_ROOT_PASSWORD`

## Run locally (multi-process)

1) Install dependencies.
2) Configure `.env` from `.env.example`.
3) Start each service in a separate terminal.

```powershell
python -m src.services.game.main
python -m src.services.emoji_catalog.main
python -m src.services.render.main
python -m src.services.gateway.main
python -m src.frontend.main
```

Gateway URL: `http://localhost:8000`  
Frontend URL: `http://localhost:8001`

## Run with Docker Compose

```powershell
docker compose up --build
```

This starts:
- `gateway-api`, `game-service`, `emoji-catalog-service`, `render-service`, `frontend`
- `redis`, `mysql`, `azurite`

Smoke test after startup:

```powershell
python -m src.smoke_test_split_services
```

## Kubernetes deployment

Helm chart path: `src/deploy/helm/blurmoji`

```powershell
helm upgrade --install blurmoji src/deploy/helm/blurmoji --create-namespace
```

Production-like override:

```powershell
helm upgrade --install blurmoji src/deploy/helm/blurmoji -f src/deploy/helm/blurmoji/values.prod.yaml --create-namespace
```

## Cron workloads included
- Daily precompute cron: warms daily challenge path by calling `game-service`
- Emoji sync cron: refreshes/validates catalog path by calling `emoji-catalog-service`

## API contract (public)
- `GET /api/v1/daily/start`
- `POST /api/v1/daily/guess`
- `GET /api/v1/daily/get_status`
- `GET /api/v1/daily/render`
- `GET /api/v1/daily/supported_emojis`

Payload conventions are preserved:
- `keyboardPosition` for emoji payload entries
- `resultImageUrl` for emoji combination assets
