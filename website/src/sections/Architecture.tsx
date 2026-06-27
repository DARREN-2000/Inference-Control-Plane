import { ArrowRight, Database, Server, Cpu } from "lucide-react";

export const Architecture = () => {
  return (
    <section id="architecture" className="py-24 relative overflow-hidden bg-zinc-950 border-t border-b border-white/5">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col lg:flex-row gap-16 items-center">

          <div className="lg:w-1/2">
            <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-6">
              Built for extreme scale.
            </h2>
            <p className="text-lg text-zinc-400 mb-8">
              Inference Control Plane sits transparently between your application and your AI providers. Written in Python with FastAPI and Asyncpg, it's designed to process thousands of requests per second with near-zero latency overhead.
            </p>

            <ul className="space-y-6">
              {[
                { title: "Stateless Gateway", desc: "Easily horizontally scalable. Deploy as many nodes as you need." },
                { title: "Redis Backed", desc: "Distributed rate limiting and semantic caching layer." },
                { title: "PostgreSQL Config", desc: "Centralized configuration and routing policy management." }
              ].map((item, i) => (
                <li key={i} className="flex gap-4">
                  <div className="mt-1 w-6 h-6 rounded-full bg-cyan-500/10 flex items-center justify-center border border-cyan-500/30 flex-shrink-0">
                    <div className="w-2 h-2 rounded-full bg-cyan-400" />
                  </div>
                  <div>
                    <h4 className="text-white font-medium mb-1">{item.title}</h4>
                    <p className="text-zinc-400 text-sm">{item.desc}</p>
                  </div>
                </li>
              ))}
            </ul>
          </div>

          <div className="lg:w-1/2 w-full">
            <div className="relative p-8 rounded-2xl border border-white/10 bg-black/50 backdrop-blur-sm">
              <div className="absolute inset-0 bg-linear-to-tr from-violet-500/10 to-cyan-500/10 rounded-2xl" />

              <div className="relative flex flex-col gap-8">
                {/* App Layer */}
                <div className="flex justify-center">
                  <div className="bg-zinc-900 border border-white/10 px-6 py-3 rounded-lg flex items-center gap-2">
                    <Cpu className="w-4 h-4 text-zinc-400" /> Your Application
                  </div>
                </div>

                <div className="flex justify-center">
                  <ArrowRight className="w-5 h-5 text-zinc-600 rotate-90" />
                </div>

                {/* Inference Control Plane Layer */}
                <div className="bg-linear-to-r from-violet-600/20 to-cyan-600/20 border border-white/20 p-6 rounded-xl flex flex-col items-center">
                  <div className="font-bold text-white mb-4">Inference Control Plane Gateway</div>
                  <div className="flex gap-4 w-full">
                    <div className="flex-1 bg-black/50 border border-white/10 p-3 rounded text-center text-xs text-zinc-300">Router</div>
                    <div className="flex-1 bg-black/50 border border-white/10 p-3 rounded text-center text-xs text-zinc-300">Cache</div>
                    <div className="flex-1 bg-black/50 border border-white/10 p-3 rounded text-center text-xs text-zinc-300">Auth</div>
                  </div>
                </div>

                <div className="flex justify-between px-12">
                  <ArrowRight className="w-5 h-5 text-zinc-600 rotate-90" />
                  <ArrowRight className="w-5 h-5 text-zinc-600 rotate-90" />
                </div>

                {/* DB & Providers Layer */}
                <div className="flex justify-between gap-4">
                  <div className="flex-1 bg-zinc-900 border border-white/10 p-4 rounded-lg flex flex-col items-center gap-2">
                    <Database className="w-5 h-5 text-cyan-400" />
                    <span className="text-xs text-zinc-400 text-center">Redis & Postgres</span>
                  </div>
                  <div className="flex-1 bg-zinc-900 border border-white/10 p-4 rounded-lg flex flex-col items-center gap-2">
                    <Server className="w-5 h-5 text-violet-400" />
                    <span className="text-xs text-zinc-400 text-center">LLM Providers</span>
                  </div>
                </div>

              </div>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
};
