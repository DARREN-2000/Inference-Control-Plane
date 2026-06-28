import { motion } from "framer-motion";
import { ArrowRight, Terminal } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";

export const Hero = () => {
  return (
    <section className="relative pt-32 pb-20 md:pt-48 md:pb-32 overflow-hidden min-h-screen flex items-center justify-center">
      {/* Animated Background Gradients */}
      <div className="absolute inset-0 bg-black -z-20" />
      <motion.div
        animate={{
          opacity: [0.3, 0.5, 0.3],
          scale: [1, 1.05, 1],
        }}
        transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
        className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-white/5 blur-[120px] rounded-full -z-10 pointer-events-none"
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 w-full">
        <div className="text-center max-w-4xl mx-auto flex flex-col items-center">

          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Badge variant="premium" className="mb-8 px-4 py-1">
              <span className="flex items-center gap-2">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-zinc-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-zinc-500"></span>
                </span>
                Laminar v2.0 is now generally available
                <ArrowRight className="w-3 h-3 ml-1" />
              </span>
            </Badge>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="text-5xl md:text-7xl lg:text-8xl font-bold tracking-tighter mb-8 leading-[1.1]"
          >
            The enterprise <br />
            <span className="text-gradient-primary">LLM Gateway</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-lg md:text-xl text-zinc-400 mb-10 max-w-2xl mx-auto font-medium"
          >
            Intelligent routing, semantic caching, and real-time observability for AI inference traffic. Built for extreme scale and zero-trust security.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto justify-center"
          >
            <Button size="lg" variant="default" className="gap-2 w-full sm:w-auto" asChild>
              <a href="./dashboard/">
                Start Building Free <ArrowRight className="w-4 h-4" />
              </a>
            </Button>
            <Button size="lg" variant="outline" className="gap-2 w-full sm:w-auto glass">
              <Terminal className="w-4 h-4" /> Read Documentation
            </Button>
          </motion.div>
        </div>

        {/* Interactive Dashboard / Terminal Mockup */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.5 }}
          className="mt-20 relative mx-auto max-w-5xl"
        >
          <div className="absolute inset-0 bg-linear-to-t from-black via-transparent to-transparent z-10 bottom-0 h-1/3 pointer-events-none" />

          <div className="rounded-xl border border-white/5 bg-black backdrop-blur-xl shadow-2xl overflow-hidden relative">
            {/* Mac OS window controls */}
            <div className="h-10 border-b border-white/5 bg-white/5 flex items-center px-4 gap-2">
              <div className="w-3 h-3 rounded-full bg-zinc-800" />
              <div className="w-3 h-3 rounded-full bg-zinc-800" />
              <div className="w-3 h-3 rounded-full bg-zinc-800" />
              <div className="flex-1 flex justify-center text-xs text-zinc-500 font-mono">
                laminar-dashboard
              </div>
            </div>

            <div className="p-6 md:p-8 flex flex-col md:flex-row gap-8">
              {/* Fake Sidebar */}
              <div className="hidden md:flex w-48 flex-col gap-2">
                {['Overview', 'Routing', 'Caching', 'Observability', 'API Keys'].map((item, i) => (
                  <div key={item} className={`px-3 py-2 rounded-md text-sm ${i === 0 ? 'bg-white/10 text-white font-medium' : 'text-zinc-500 hover:text-zinc-300 transition-colors'}`}>
                    {item}
                  </div>
                ))}
              </div>

              {/* Fake Content area */}
              <div className="flex-1 space-y-6">
                <div className="flex justify-between items-end">
                  <div>
                    <h3 className="text-xl font-semibold text-white mb-1">Inference Traffic</h3>
                    <p className="text-sm text-zinc-500">Last 24 hours across all providers</p>
                  </div>
                  <Badge variant="glass" className="text-zinc-400 border-zinc-500/20">System Healthy</Badge>
                </div>

                {/* Fake Chart */}
                <div className="h-48 border border-white/5 rounded-lg bg-black/50 p-4 relative flex items-end justify-between gap-2 overflow-hidden">
                   {Array.from({ length: 24 }).map((_, i) => {
                     const height = 20 + ((i * 13) % 100) / 100 * 60;
                     const isHigh = height > 60;
                     return (
                       <motion.div
                         key={i}
                         initial={{ height: 0 }}
                         animate={{ height: `${height}%` }}
                         transition={{ delay: 0.6 + (i * 0.05), duration: 0.5 }}
                         className={`w-full rounded-t-sm ${isHigh ? 'bg-zinc-600' : 'bg-zinc-800'}`}
                       />
                     )
                   })}
                   <div className="absolute inset-0 bg-linear-to-t from-black/80 to-transparent pointer-events-none" />
                </div>

                {/* Fake Stats */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {[
                    { label: 'Total Requests', value: '1.2M' },
                    { label: 'Cache Hit Rate', value: '42.8%' },
                    { label: 'Avg Latency', value: '45ms' },
                    { label: 'Cost Saved', value: '$840' },
                  ].map((stat, i) => (
                    <div key={i} className="p-4 rounded-lg bg-white/5 border border-white/5">
                      <div className="text-xs text-zinc-500 mb-1">{stat.label}</div>
                      <div className="text-xl font-semibold text-white">{stat.value}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};
