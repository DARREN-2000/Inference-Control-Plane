import { motion } from "framer-motion";
import { AlertCircle, TrendingUp, Clock, FileCode2 } from "lucide-react";
import { Card, CardContent } from "@/components/ui/Card";

const painPoints = [
  {
    icon: TrendingUp,
    title: "Runaway Inference Costs",
    description: "Without granular routing and caching, a single unoptimized LLM deployment can drain thousands of dollars in redundant compute."
  },
  {
    icon: Clock,
    title: "Unacceptable Latency",
    description: "Waiting 5-10 seconds for standard API responses breaks user experience. You need sub-millisecond cache hits for scale."
  },
  {
    icon: AlertCircle,
    title: "Provider Outages",
    description: "Relying on a single AI provider means your application goes down when they do. Manual failovers are too slow for production."
  },
  {
    icon: FileCode2,
    title: "Spaghetti Integrations",
    description: "Maintaining 15 different SDKs and parsing logic for every new model release grinds feature development to a halt."
  }
];

export const Problem = () => {
  return (
    <section className="py-32 relative bg-black border-b border-white/5">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

        <div className="grid lg:grid-cols-2 gap-16 items-center">
          <div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5 }}
            >
              <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-6">
                Scaling AI is <span className="text-zinc-400">painful</span>.
              </h2>
              <p className="text-lg text-zinc-400 mb-8 leading-relaxed">
                Building a quick prototype with an LLM is easy. But putting it into production exposes your infrastructure to unpredictable costs, rate limits, latency spikes, and provider unreliability.
              </p>

              <div className="space-y-6">
                {painPoints.slice(0, 2).map((point, index) => (
                  <div key={index} className="flex gap-4">
                    <div className="flex-shrink-0 mt-1">
                      <div className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center border border-white/10">
                        <point.icon className="w-5 h-5 text-zinc-400" />
                      </div>
                    </div>
                    <div>
                      <h4 className="text-white font-medium text-lg mb-1">{point.title}</h4>
                      <p className="text-zinc-400 text-sm leading-relaxed">{point.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>

          <div className="relative">
            {/* Visual representation of the mess */}
            <div className="absolute inset-0 bg-linear-to-tr from-zinc-800/40 to-transparent rounded-2xl blur-3xl -z-10" />
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <Card className="border-white/5 bg-black/50 overflow-hidden">
                <CardContent className="p-0">
                  <div className="bg-white/5 border-b border-white/5 px-4 py-3 flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 text-zinc-400" />
                    <span className="text-sm font-mono text-zinc-400">Production Alerts (Last 24h)</span>
                  </div>
                  <div className="p-4 space-y-3 font-mono text-sm">
                    {[
                      { time: '14:22:01', msg: 'ERR_RATE_LIMIT_EXCEEDED: OpenAI API', type: 'error' },
                      { time: '14:25:40', msg: 'WARN_LATENCY_SPIKE: Anthropic Claude 3 (12.4s)', type: 'warn' },
                      { time: '15:10:05', msg: 'ERR_BUDGET_EXCEEDED: Daily limit reached', type: 'error' },
                      { time: '16:01:22', msg: 'ERR_PROVIDER_DOWN: Timeout after 30s', type: 'error' },
                    ].map((log, i) => (
                      <div key={i} className="flex gap-3">
                        <span className="text-zinc-600">{log.time}</span>
                        <span className={log.type === 'error' ? 'text-zinc-400' : 'text-zinc-500'}>{log.msg}</span>
                      </div>
                    ))}
                    <div className="animate-pulse flex gap-3 opacity-50 mt-4">
                      <span className="text-zinc-600">16:02:00</span>
                      <span className="text-zinc-400">Waiting for failover...</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  );
};
