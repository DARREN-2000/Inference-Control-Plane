# Inference Control Plane Frontend

Production-focused Next.js App Router UI for the Inference Control Plane backend.

## Stack

- Next.js 16 + React 19 + TypeScript
- Tailwind CSS 4
- API integration with the backend `/api/v1` routes

## Local Development

1. Ensure backend is running on `http://localhost:8000`.
2. Configure environment values:

```bash
cp .env.example .env.local
```

3. Install dependencies and run the dev server:

```bash
npm install
npm run dev
```

4. Open `http://localhost:3000`.

## Environment Variables

- `NEXT_PUBLIC_API_BASE_URL`: Backend base URL. Default value in `.env.example` is `http://localhost:8000/api/v1`.
- `NEXT_PUBLIC_DEMO_MODE`: When `true`, uses simulated responses for a live demo without a backend.
- `DEPLOY_TARGET`: Set to `github-pages` to export a static demo build.

## Quality Checks

```bash
npm run lint
npm run build
```

## Deployment

- Deploy the backend on Render (or another host) and set
  `NEXT_PUBLIC_API_BASE_URL` to the service URL.
- Set `NEXT_PUBLIC_DEMO_MODE=false` for production traffic.
- For a static demo build only, set `DEPLOY_TARGET=github-pages` and keep
  `NEXT_PUBLIC_DEMO_MODE=true`.

## Current UI Scope

- Control-plane overview shell
- Live inference playground integrated with backend generate endpoint
- Operational highlights and baseline dashboard cards

## Next Milestones

- OAuth/JWT session flow and protected routes
- API key management screens
- Usage analytics and request log explorer
- End-to-end tests and accessibility automation
