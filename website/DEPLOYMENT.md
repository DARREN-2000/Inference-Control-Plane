# Deployment Instructions

The Inference Control Plane website is built with React 19, Vite, and Tailwind CSS v4, and is deployed to GitHub Pages.

## GitHub Pages Deployment

The website is automatically deployed to GitHub Pages when changes are pushed to the `main` branch, specifically affecting the `website/` directory.

### Workflow

The deployment is handled by a GitHub Actions workflow located at `.github/workflows/deploy.yml`. This workflow deploys BOTH the main website and the Next.js dashboard frontend.

1.  **Trigger**: The workflow runs on pushes to `main` or manually via `workflow_dispatch`.
2.  **Build Website**: It installs dependencies using `npm install` and builds the static assets using `npm run build` inside the `website/` directory.
3.  **Build Dashboard**: It installs dependencies using `pnpm install` and builds the static assets using `pnpm run build` inside the `frontend/` directory.
4.  **Merge**: The dashboard build (`frontend/out`) is copied into the website build (`website/dist/dashboard`).
5.  **Upload & Deploy**: The merged build output (`website/dist`) is uploaded as an artifact and deployed to GitHub Pages.

### Manual Deployment (Local Build)

If you need to build the site locally to inspect the output:

```bash
cd website
npm install
npm run build
```

This will generate the static files in the `website/dist/` directory.

### GitHub Pages Configuration

Ensure that your GitHub repository settings are configured correctly:

1.  Go to **Settings** > **Pages**.
2.  Under **Build and deployment**, select **GitHub Actions** as the source.
3.  The `deploy.yml` workflow will automatically handle the rest.

### React Router on GitHub Pages

GitHub Pages doesn't natively support client-side routing (Single Page Applications) out of the box because it expects a physical file for every route.

To handle this, we use a `404.html` file in the `website/public/` directory. When a user navigates directly to a route (e.g., `/features`), GitHub Pages serves the `404.html`. This file contains a script that redirects the user back to `index.html` with the requested route passed as a query parameter. The React app then decodes this and renders the correct view.

Ensure `basename="/Inference-Control-Plane"` (or your repository name) is correctly set in `App.tsx` and `vite.config.ts`.
