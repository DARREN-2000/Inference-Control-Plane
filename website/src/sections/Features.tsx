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
    description: "Route requests based on cost, latency, or custom logic to optimize your AI spend across multiple providers.",
    icon: GitMerge,
    color: "text-blue-400",
    bg: "bg-blue-400/10",
    border: "border-blue-400/20"
  },
  {
    title: "Semantic Caching",
    description: "Sub-millisecond response times for similar queries using Redis-backed vector search. Save up to 90% on compute.",
    icon: Layers,
    color: "text-violet-400",
    bg: "bg-violet-400/10",
    border: "border-violet-400/20"
  },
  {
    title: "Automatic Fallbacks",
    description: "Zero-latency failover chain (OpenAI → Anthropic → Local) to ensure 99.99% uptime during provider outages.",
    icon: ShieldAlert,
    color: "text-emerald-400",
    bg: "bg-emerald-400/10",
    border: "border-emerald-400/20"
  },
  {
    title: "Rate Limiting",
    description: "Protect your budgets and prevent abuse with distributed token-bucket algorithms and user-level quotas.",
    icon: Lock,
    color: "text-rose-400",
    bg: "bg-rose-400/10",
    border: "border-rose-400/20"
  },
  {
    title: "Real-time Observability",
    description: "Complete visibility into every token, prompt, and latency metric with OpenTelemetry integration.",
    icon: Activity,
    color: "text-cyan-400",
    bg: "bg-cyan-400/10",
    border: "border-cyan-400/20"
  },
  {
    title: "Zero-Trust Security",
    description: "Automatic PII redaction and secure enterprise key management. Never leak sensitive data to external LLMs.",
    icon: KeyRound,
    color: "text-amber-400",
    bg: "bg-amber-400/10",
    border: "border-amber-400/20"
  },
  {
    title: "Prompt Management",
    description: "Version control your prompts independent of your codebase. Run A/B tests on prompts without deployments.",
    icon: TerminalSquare,
    color: "text-fuchsia-400",
    bg: "bg-fuchsia-400/10",
    border: "border-fuchsia-400/20"
  },
  {
    title: "Universal Support",
    description: "Write once, run on any LLM. Normalized request and response schemas across 20+ provider APIs.",
    icon: Globe2,
    color: "text-indigo-400",
    bg: "bg-indigo-400/10",
    border: "border-indigo-400/20"
  }
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5 }
  }
};

export const Features = () => {
  return (
    <section id="features" className="py-32 relative bg-black border-t border-white/5">
      <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-[0.03] pointer-events-none mix-blend-overlay"></div>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center mb-20 max-w-3xl mx-auto">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-3xl md:text-5xl font-bold tracking-tight mb-6"
          >
            Everything you need for production AI.
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="text-lg text-zinc-400"
          >
            Stop building boilerplate. Inference Control Plane provides a complete, enterprise-grade suite of tools to make your LLM applications fast, reliable, and observable.
          </motion.p>
        </div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
        >
          {features.map((feature, index) => (
            <motion.div key={index} variants={itemVariants} className="group h-full">
              <Card className="h-full bg-zinc-950/40 border-white/5 hover:border-white/20 hover:bg-zinc-900/50 transition-all duration-300 relative overflow-hidden">
                <div className="absolute inset-0 bg-linear-to-br from-white/[0.02] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                <CardHeader>
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4 transition-transform duration-300 group-hover:scale-110 group-hover:-rotate-3 ${feature.bg} ${feature.border} border`}>
                    <feature.icon className={`w-6 h-6 ${feature.color}`} />
                  </div>
                  <CardTitle className="text-xl group-hover:text-white transition-colors">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base text-zinc-400 group-hover:text-zinc-300 transition-colors">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
};
