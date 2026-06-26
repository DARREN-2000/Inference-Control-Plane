import { motion } from "framer-motion";
import { CheckCircle2 } from "lucide-react";
import { CodeBlock } from "@/components/ui/CodeBlock";

export const Solution = () => {
  return (
    <section className="py-32 relative bg-zinc-950">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-violet-900/10 via-transparent to-transparent pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center mb-16 max-w-3xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
          >
            <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-6">
              One unified API for <span className="text-gradient-primary">everything.</span>
            </h2>
            <p className="text-lg text-zinc-400">
              Replace dozens of messy SDKs with a single, intelligent proxy. Laminar handles the complexity of caching, routing, and fallbacks transparently.
            </p>
          </motion.div>
        </div>

        <div className="grid lg:grid-cols-2 gap-16 items-center">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <CodeBlock
              language="python"
              code={`import openai

# Just point your standard client to Laminar
client = openai.Client(
    base_url="https://api.laminar.ai/v1",
    api_key="lam_live_xxxxx"
)

# Request hits Laminar Gateway
response = client.chat.completions.create(
    model="gpt-4-turbo",      # Or 'claude-3', 'llama-3'
    messages=[...],
    extra_headers={
        "X-Laminar-Cache": "true",
        "X-Laminar-Route-To": "cheapest_available",
        "X-Laminar-Fallback": "claude-3-haiku"
    }
)`}
            />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="space-y-8"
          >
            {[
              { title: "Zero Code Changes", desc: "100% compatible with OpenAI SDKs. Just change the base URL." },
              { title: "Instant Semantic Caching", desc: "Sub-millisecond responses for similar queries out-of-the-box." },
              { title: "Automatic Fallbacks", desc: "If GPT-4 fails, instantly route to Claude 3 with zero latency penalty." }
            ].map((feature, i) => (
              <div key={i} className="flex gap-4 items-start">
                <CheckCircle2 className="w-6 h-6 text-emerald-400 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">{feature.title}</h3>
                  <p className="text-zinc-400 leading-relaxed">{feature.desc}</p>
                </div>
              </div>
            ))}
          </motion.div>
        </div>
      </div>
    </section>
  );
};
