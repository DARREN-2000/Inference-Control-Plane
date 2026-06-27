import type { NextConfig } from "next";

const isGithubPages = process.env.DEPLOY_TARGET === "github-pages";
const basePath = isGithubPages ? "/Inference-Control-Plane/dashboard" : "";

const nextConfig: NextConfig = {
  output: isGithubPages ? "export" : undefined,
  basePath: isGithubPages ? basePath : undefined,
  assetPrefix: isGithubPages ? `${basePath}/` : undefined,
  trailingSlash: isGithubPages,
  images: {
    unoptimized: isGithubPages,
  },
};

export default nextConfig;
