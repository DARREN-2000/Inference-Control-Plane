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

## Quality Checks

```bash
npm run lint
npm run build
```

## Current UI Scope

- Control-plane overview shell
- Live inference playground integrated with backend generate endpoint
- Operational highlights and baseline dashboard cards

## Next Milestones

- OAuth/JWT session flow and protected routes
- API key management screens
- Usage analytics and request log explorer
- End-to-end tests and accessibility automation
