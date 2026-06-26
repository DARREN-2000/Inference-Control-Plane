import { motion } from "framer-motion";
import { ArrowRight, Cpu, Network, Server, Database, Lock, ShieldCheck } from "lucide-react";

export const HowItWorks = () => {
  return (
    <section className="py-32 relative bg-zinc-950 border-t border-b border-white/5 overflow-hidden">
      <div className="absolute inset-0 bg-grid-white/[0.02] bg-[size:32px_32px]" />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">

        <div className="text-center mb-24 max-w-3xl mx-auto">
          <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-6">
            Architected for extreme scale.
          </h2>
          <p className="text-lg text-zinc-400">
            Laminar sits transparently between your application and your AI providers. Written in Python with FastAPI and Asyncpg, it processes thousands of requests per second with near-zero latency overhead.
          </p>
        </div>

        <div className="relative">
          {/* Connecting Line (Desktop) */}
          <div className="hidden md:block absolute top-1/2 left-0 w-full h-px bg-linear-to-r from-transparent via-white/20 to-transparent -translate-y-1/2" />

          <div className="grid md:grid-cols-3 gap-8 relative">

            {/* Step 1 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="bg-black/80 backdrop-blur-md border border-white/10 rounded-2xl p-8 relative z-10 hover:border-white/20 transition-colors"
            >
              <div className="w-12 h-12 rounded-xl bg-violet-500/10 border border-violet-500/20 flex items-center justify-center mb-6">
                <Cpu className="w-6 h-6 text-violet-400" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-3">1. Your Application</h3>
              <p className="text-zinc-400 text-sm leading-relaxed mb-6">
                Send standard OpenAI-formatted requests to the Laminar Gateway instead of directly to providers. No SDK changes required.
              </p>
              <div className="p-3 bg-white/5 rounded-lg border border-white/5 font-mono text-xs text-zinc-500">
                POST /v1/chat/completions
              </div>
            </motion.div>

            {/* Step 2 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
              className="bg-linear-to-b from-violet-900/20 to-cyan-900/20 backdrop-blur-md border border-white/20 rounded-2xl p-8 relative z-10 shadow-[0_0_30px_rgba(139,92,246,0.1)]"
            >
              <div className="absolute -top-3 -right-3">
                <span className="flex h-6 w-6 relative">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-6 w-6 bg-cyan-500 border-2 border-black"></span>
                </span>
              </div>

              <div className="w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center mb-6">
                <Network className="w-6 h-6 text-cyan-400" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-3">2. Laminar Control Plane</h3>
              <ul className="space-y-3 text-sm text-zinc-300">
                <li className="flex items-center gap-2"><ShieldCheck className="w-4 h-4 text-emerald-400" /> Auth & Rate Limiting</li>
                <li className="flex items-center gap-2"><Lock className="w-4 h-4 text-amber-400" /> PII Redaction</li>
                <li className="flex items-center gap-2"><Database className="w-4 h-4 text-violet-400" /> Semantic Cache Check</li>
                <li className="flex items-center gap-2"><ArrowRight className="w-4 h-4 text-cyan-400" /> Dynamic Routing</li>
              </ul>
            </motion.div>

            {/* Step 3 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.4 }}
              className="bg-black/80 backdrop-blur-md border border-white/10 rounded-2xl p-8 relative z-10 hover:border-white/20 transition-colors"
            >
              <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center mb-6">
                <Server className="w-6 h-6 text-emerald-400" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-3">3. LLM Providers</h3>
              <p className="text-zinc-400 text-sm leading-relaxed mb-6">
                Requests are securely executed against the optimal provider. Responses are normalized, metrics are logged, and results are returned.
              </p>
              <div className="flex gap-2">
                <div className="flex-1 p-2 bg-white/5 rounded border border-white/5 text-center text-xs text-zinc-500">OpenAI</div>
                <div className="flex-1 p-2 bg-white/5 rounded border border-white/5 text-center text-xs text-zinc-500">Anthropic</div>
                <div className="flex-1 p-2 bg-white/5 rounded border border-white/5 text-center text-xs text-zinc-500">Local</div>
              </div>
            </motion.div>

          </div>
        </div>
      </div>
    </section>
  );
};
