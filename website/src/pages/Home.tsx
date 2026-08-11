import { lazy, Suspense } from "react";
import { Hero } from "@/sections/Hero";
import { Integrations } from "@/sections/Integrations";
import { Problem } from "@/sections/Problem";

// Lazy load below-the-fold components for performance
const Solution = lazy(() =>
  import("@/sections/Solution").then((m) => ({ default: m.Solution })),
);
const Features = lazy(() =>
  import("@/sections/Features").then((m) => ({ default: m.Features })),
);
const HowItWorks = lazy(() =>
  import("@/sections/HowItWorks").then((m) => ({ default: m.HowItWorks })),
);
const Workflow = lazy(() =>
  import("@/sections/Workflow").then((m) => ({ default: m.Workflow })),
);
const Screenshots = lazy(() =>
  import("@/sections/Screenshots").then((m) => ({ default: m.Screenshots })),
);
const Performance = lazy(() =>
  import("@/sections/Performance").then((m) => ({ default: m.Performance })),
);
const Security = lazy(() =>
  import("@/sections/Security").then((m) => ({ default: m.Security })),
);
const EnterpriseFeatures = lazy(() =>
  import("@/sections/EnterpriseFeatures").then((m) => ({
    default: m.EnterpriseFeatures,
  })),
);
const DeveloperExperience = lazy(() =>
  import("@/sections/DeveloperExperience").then((m) => ({
    default: m.DeveloperExperience,
  })),
);
const ApiSection = lazy(() =>
  import("@/sections/ApiSection").then((m) => ({ default: m.ApiSection })),
);
const Documentation = lazy(() =>
  import("@/sections/Documentation").then((m) => ({
    default: m.Documentation,
  })),
);
const Roadmap = lazy(() =>
  import("@/sections/Roadmap").then((m) => ({ default: m.Roadmap })),
);
const Faq = lazy(() =>
  import("@/sections/Faq").then((m) => ({ default: m.Faq })),
);
const Cta = lazy(() =>
  import("@/sections/Cta").then((m) => ({ default: m.Cta })),
);

export default function Home() {
  return (
    <div className="w-full flex flex-col bg-black text-white">
      {/* Above the fold */}
      <Hero />
      <Integrations />
      <Problem />

      {/* Below the fold (Lazy Loaded) */}
      <Suspense
        fallback={
          <div className="h-screen bg-black flex items-center justify-center text-zinc-500 font-mono text-sm animate-pulse">
            Loading Inference Control Plane Control Plane...
          </div>
        }
      >
        <Solution />
        <Features />
        <HowItWorks />
        <Workflow />
        <Screenshots />
        <Performance />
        <Security />
        <EnterpriseFeatures />
        <DeveloperExperience />
        <ApiSection />
        <Documentation />
        <Roadmap />
        <Faq />
        <Cta />
      </Suspense>
    </div>
  );
}
