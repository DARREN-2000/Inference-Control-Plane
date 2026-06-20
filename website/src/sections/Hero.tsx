import { motion } from "framer-motion";
import { ArrowRight, Terminal } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";

export const Hero = () => {
  return (
    <section className="relative pt-32 pb-20 md:pt-48 md:pb-32 overflow-hidden">
      {/* Background Grid & Glow */}
      <div className="absolute inset-0 z-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]"></div>
      <div className="absolute left-0 right-0 top-0 -z-10 m-auto h-[310px] w-[310px] rounded-full bg-violet-500 opacity-20 blur-[100px]"></div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="flex flex-col items-center text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Badge variant="glow" className="mb-8">
              <span className="flex h-2 w-2 rounded-full bg-cyan-400 mr-2"></span>
              Laminar 1.0 is now generally available
            </Badge>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="text-5xl md:text-7xl font-bold tracking-tight mb-8 max-w-4xl bg-clip-text text-transparent bg-gradient-to-b from-white to-white/70"
          >
            The Enterprise Control Plane for LLMs.
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-lg md:text-xl text-zinc-400 max-w-2xl mb-10 leading-relaxed"
          >
            Unify, route, and observe your AI traffic with a single gateway. Laminar brings intelligent caching, automatic fallbacks, and zero-latency failovers to production AI teams.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto"
          >
            <Button size="lg" className="gap-2 w-full sm:w-auto text-base">
              Start Building <ArrowRight className="w-4 h-4" />
            </Button>
            <Button size="lg" variant="outline" className="w-full sm:w-auto text-base">
              Read the Docs
            </Button>
          </motion.div>
        </div>

        {/* Terminal Mockup */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.5 }}
          className="mt-20 mx-auto max-w-4xl rounded-xl border border-white/10 bg-black/50 backdrop-blur-xl shadow-2xl overflow-hidden"
        >
          <div className="flex items-center px-4 py-3 border-b border-white/10 bg-zinc-900/50">
            <div className="flex gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500/80"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-500/80"></div>
              <div className="w-3 h-3 rounded-full bg-green-500/80"></div>
            </div>
            <div className="mx-auto flex items-center text-xs text-zinc-500 font-mono gap-2">
              <Terminal className="w-3 h-3" /> bash ~ laminar start
            </div>
          </div>
          <div className="p-6 font-mono text-sm text-zinc-300 bg-zinc-950/80 overflow-x-auto">
            <div className="flex gap-4">
              <span className="text-zinc-500">$</span>
              <span className="text-cyan-400">laminar</span> start --watch
            </div>
            <div className="mt-2 text-zinc-400">Initializing Laminar Gateway v1.0.0...</div>
            <div className="mt-1 text-emerald-400">✓ Redis connected (10.0.0.4:6379)</div>
            <div className="mt-1 text-emerald-400">✓ Asyncpg pool ready (20 connections)</div>
            <div className="mt-1 text-zinc-400">Loading routing policies...</div>
            <div className="mt-1 text-emerald-400">✓ Loaded 3 policies (openai-fallback, local-first, low-cost)</div>
            <div className="mt-4 text-violet-400">🚀 Gateway listening on 0.0.0.0:8000</div>
            <div className="mt-2 animate-pulse">
              <span className="text-zinc-500">[2023-10-27 14:32:01]</span> <span className="text-cyan-400">INFO:</span> Route /v1/chat/completions → cache_hit=true latency=1.2ms
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};
