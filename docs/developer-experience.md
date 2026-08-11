# Developer Experience (DX) & Onboarding

Welcome to the Inference Control Plane codebase! This document outlines our repository structure, coding conventions, and CI/CD pipelines to help you contribute effectively.

## Repository Structure

Inference Control Plane is a monorepo containing multiple interconnected applications.

```text
Inference-Control-Plane/
├── src/inference_control_plane/  # Python FastAPI backend (The Proxy API)
│   ├── api/                      # Route definitions
│   ├── core/                     # Configuration, Security setup
│   ├── db/                       # SQLAlchemy models, sessions, Redis client
│   ├── schemas/                  # Pydantic validation models
│   └── services/                 # Business logic (Routing, Caching, LLM integration)
├── frontend/                     # Next.js 15 React Dashboard
│   ├── app/                      # Next.js App Router pages
│   ├── components/               # Reusable React/shadcn UI components
│   └── lib/                      # API clients, utilities
├── website/                      # Static product marketing site (Vite/React)
├── docs/                         # Markdown documentation (You are here)
├── tests/                        # Pytest suite for the backend
├── alembic/                      # Database migration scripts
├── deploy/                       # Kubernetes, Docker Compose manifests
└── Makefile                      # Development shortcut commands
```

## Python Backend Conventions

The backend is written in Python 3.12+ using FastAPI.

### 1. Asynchronous I/O

The proxy must be highly concurrent. **Never use synchronous I/O in the request path.**

- Use `asyncpg` via SQLAlchemy's `AsyncSession` for database queries.
- Use `redis.asyncio` for caching.
- Use `httpx.AsyncClient` for outbound API calls to LLM providers. Ensure the client is instantiated globally to utilize connection pooling.

### 2. Dependency Injection

Use FastAPI's `Depends()` for passing configuration, database sessions, and authentication contexts into routes. This makes unit testing vastly easier.

### 3. Pydantic

All incoming requests and outgoing responses must be validated using Pydantic models defined in `src/schemas`.

### 4. Code Quality Tools

We enforce strict linting and formatting using `ruff`.

```bash
# Check for linting errors
make lint-backend
# Or manually: uv run ruff check src/ tests/

# Automatically fix format issues
uv run ruff check --fix src/
```

### 5. Testing

We use `pytest`. Tests must be asynchronous (using `pytest-asyncio`). Mock external HTTP calls using `respx` or by patching the HTTPX client.

```bash
make test
```

## Frontend Conventions

The frontend uses Next.js (App Router), React, TypeScript, and Tailwind CSS v4.

### 1. Package Manager

You **must** use `pnpm` in the `frontend/` directory. Do not use `npm` or `yarn`.

### 2. Styling

Use Tailwind CSS exclusively. Do not write inline CSS or use other UI frameworks (Material, Chakra). For complex UI elements, we utilize `shadcn/ui` which builds on top of Radix UI primitives.
_Note: Tailwind v4 uses `@utility` instead of `@layer utilities`._

### 3. State and Data Fetching

Use React Server Components where possible for initial data load. For client-side interactivity and mutations, use standard React hooks.

### 4. Formatting and Linting

```bash
cd frontend
pnpm run lint
pnpm run type-check
```

## CI/CD Pipeline (GitHub Actions)

Our CI pipeline enforces quality before merges. The workflows are located in `.github/workflows/`.

### Continuous Integration (`ci.yml`)

Runs on every Pull Request and push to `main`.

1. **Backend Matrix:** Runs `pytest` and `ruff` on multiple Python versions.
2. **Frontend Build:** Runs `pnpm lint`, `pnpm type-check`, and `pnpm test`. Ensures the Next.js app builds successfully.

### Deployment (`deploy.yml`)

Runs when code is merged to `main`.

- Builds the static `website/` and Next.js `frontend/` (configured with `DEPLOY_TARGET=github-pages`).
- Merges the builds and deploys them to GitHub Pages.

### Release Process

1. Update version numbers in `src/inference_control_plane/__init__.py` and `frontend/package.json`.
2. Create a GitHub Release with the tag format `vX.Y.Z`.
3. The release workflow will automatically build and push Docker images to GHCR and upload Python artifacts.

## Branch Strategy

We use standard GitHub Flow.

1. Branch from `main` (e.g., `feature/add-qdrant-cache` or `fix/token-leak`).
2. Keep PRs small and focused.
3. PRs require passing CI checks and at least one code review approval before merging.
