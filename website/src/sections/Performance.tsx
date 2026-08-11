import { motion } from "framer-motion";
import { Zap, Server, Activity } from "lucide-react";

const metrics = [
  { label: "P99 Overhead", value: "< 2ms", icon: Zap },
  { label: "Requests / Sec", value: "10k+", icon: Activity },
  { label: "Cache Hit Speed", value: "0.5ms", icon: Server },
];

export const Performance = () => {
  return (
    <section id="performance" className="py-24 bg-black">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          <div>
            <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-6">
              Written in Python, <br />
              <span className="text-zinc-500">optimized for speed.</span>
            </h2>
            <p className="text-lg text-zinc-400 mb-8 leading-relaxed">
              Inference Control Plane is built on FastAPI and Asyncpg, utilizing
              an entirely asynchronous, non-blocking architecture. Connection
              pooling and optimized Redis caching ensure your proxy never
              becomes the bottleneck.
            </p>

            <div className="grid grid-cols-2 gap-8">
              {metrics.map((metric, i) => (
                <div key={i}>
                  <div className="flex items-center gap-2 text-zinc-400 mb-2">
                    <metric.icon className="w-4 h-4" />
                    <span className="text-sm uppercase tracking-wider font-medium">
                      {metric.label}
                    </span>
                  </div>
                  <div className="text-3xl font-bold text-white tracking-tight">
                    {metric.value}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="relative">
            <div className="absolute inset-0 bg-linear-to-tr from-cyan-500/10 to-violet-500/10 blur-3xl rounded-full" />
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="bg-zinc-950/80 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-2xl relative"
            >
              <div className="flex justify-between items-center mb-6">
                <span className="text-sm font-mono text-zinc-400">
                  Latency Distribution (Last 1h)
                </span>
                <span className="text-xs text-emerald-400 bg-emerald-400/10 px-2 py-1 rounded">
                  Live
                </span>
              </div>

              <div className="space-y-4">
                {[
                  {
                    label: "P50",
                    ms: "0.8ms",
                    w: "w-[15%]",
                    color: "bg-emerald-500",
                  },
                  {
                    label: "P90",
                    ms: "1.2ms",
                    w: "w-[25%]",
                    color: "bg-cyan-500",
                  },
                  {
                    label: "P99",
                    ms: "1.9ms",
                    w: "w-[40%]",
                    color: "bg-violet-500",
                  },
                ].map((item, i) => (
                  <div key={i} className="flex items-center gap-4">
                    <div className="w-8 text-sm font-mono text-zinc-500">
                      {item.label}
                    </div>
                    <div className="flex-1 h-2 bg-white/5 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        whileInView={{
                          width: item.w.replace("w-[", "").replace("]", ""),
                        }}
                        viewport={{ once: true }}
                        transition={{
                          delay: 0.2 + i * 0.1,
                          duration: 0.8,
                          ease: "easeOut",
                        }}
                        className={`h-full ${item.color}`}
                      />
                    </div>
                    <div className="w-12 text-sm font-mono text-white text-right">
                      {item.ms}
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  );
};
