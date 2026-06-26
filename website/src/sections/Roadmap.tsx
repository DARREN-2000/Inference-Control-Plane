import { CheckCircle2, CircleDashed } from "lucide-react";

const roadmapItems = [
  { status: "done", quarter: "Q1 2024", title: "Core Proxy & Caching", desc: "Redis-backed semantic caching and basic OpenAI routing." },
  { status: "done", quarter: "Q2 2024", title: "Observability & Tracing", desc: "OpenTelemetry integration and latency metrics dashboard." },
  { status: "current", quarter: "Q3 2024", title: "Enterprise Controls", desc: "PII redaction, RBAC, and virtual key management." },
  { status: "planned", quarter: "Q4 2024", title: "Edge Deployment", desc: "Wasm edge worker support for ultra-low latency caching." },
];

export const Roadmap = () => {
  return (
    <section className="py-24 bg-zinc-950">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="text-3xl font-bold tracking-tight mb-12 text-center">
          Product Roadmap
        </h2>

        <div className="relative border-l border-white/10 ml-4 md:ml-0 md:pl-8 space-y-12">
          {roadmapItems.map((item, i) => (
            <div key={i} className="relative pl-8 md:pl-0">
              <div className="absolute -left-12 md:-left-12 top-0 mt-1 bg-zinc-950">
                {item.status === "done" ? (
                  <CheckCircle2 className="w-6 h-6 text-emerald-500 bg-zinc-950" />
                ) : item.status === "current" ? (
                  <div className="w-6 h-6 rounded-full border-2 border-violet-500 bg-violet-500/20 shadow-[0_0_10px_rgba(139,92,246,0.5)]" />
                ) : (
                  <CircleDashed className="w-6 h-6 text-zinc-600 bg-zinc-950" />
                )}
              </div>

              <div>
                <div className="flex items-center gap-3 mb-1">
                  <span className={`text-xs font-mono px-2 py-1 rounded ${
                    item.status === 'done' ? 'bg-white/5 text-zinc-400' :
                    item.status === 'current' ? 'bg-violet-500/20 text-violet-300' :
                    'bg-white/5 text-zinc-600'
                  }`}>
                    {item.quarter}
                  </span>
                </div>
                <h3 className={`text-lg font-semibold ${item.status === 'planned' ? 'text-zinc-400' : 'text-white'}`}>
                  {item.title}
                </h3>
                <p className="text-zinc-500 text-sm mt-1">{item.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
