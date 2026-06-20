import { motion } from "framer-motion";
import {
  GitMerge,
  Layers,
  ShieldAlert,
  Lock,
  Activity,
  KeyRound,
  TerminalSquare,
  Globe2
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/Card";

const features = [
  {
    title: "Intelligent Routing",
    description: "Route requests based on cost, latency, or custom logic to optimize your AI spend.",
    icon: GitMerge,
    color: "text-blue-400"
  },
  {
    title: "Semantic Caching",
    description: "Sub-millisecond response times for similar queries using Redis-backed vector search.",
    icon: Layers,
    color: "text-violet-400"
  },
  {
    title: "Automatic Fallbacks",
    description: "Zero-latency failover chain (OpenAI → Anthropic → Local) to ensure 99.99% uptime.",
    icon: ShieldAlert,
    color: "text-emerald-400"
  },
  {
    title: "Rate Limiting",
    description: "Protect your budgets and prevent abuse with distributed token-bucket algorithms.",
    icon: Lock,
    color: "text-rose-400"
  },
  {
    title: "Real-time Observability",
    description: "Complete visibility into every token, prompt, and latency metric with OpenTelemetry.",
    icon: Activity,
    color: "text-cyan-400"
  },
  {
    title: "Zero-Trust Security",
    description: "Automatic PII redaction and secure key management for enterprise compliance.",
    icon: KeyRound,
    color: "text-amber-400"
  },
  {
    title: "Prompt Management",
    description: "Version control your prompts independent of your codebase with A/B testing.",
    icon: TerminalSquare,
    color: "text-fuchsia-400"
  },
  {
    title: "Universal Support",
    description: "Write once, run on any LLM. Normalized schemas across 20+ provider APIs.",
    icon: Globe2,
    color: "text-indigo-400"
  }
];

export const Features = () => {
  return (
    <section id="features" className="py-24 relative bg-black">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center mb-16 max-w-3xl mx-auto">
          <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-6">
            Everything you need for production AI.
          </h2>
          <p className="text-lg text-zinc-400">
            Stop building boilerplate. Laminar provides a complete suite of tools to make your LLM applications fast, reliable, and observable.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <Card className="h-full bg-zinc-950/40 border-white/5 hover:border-white/10 hover:bg-zinc-900/50 transition-all duration-300">
                <CardHeader>
                  <div className={`w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center mb-4 border border-white/5 ${feature.color}`}>
                    <feature.icon className="w-5 h-5" />
                  </div>
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base text-zinc-400">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};
