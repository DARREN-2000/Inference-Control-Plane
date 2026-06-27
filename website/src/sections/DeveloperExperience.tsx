import { motion } from "framer-motion";
import { Terminal, Command, Zap } from "lucide-react";

export const DeveloperExperience = () => {
  return (
    <section className="py-24 bg-black">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16 max-w-2xl mx-auto">
          <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-4">
            Loved by developers.
          </h2>
          <p className="text-lg text-zinc-400">
            We built Inference Control Plane to feel invisible. No new paradigms to learn, just standard APIs supercharged with enterprise capabilities.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {[
            {
              icon: Terminal,
              title: "Native SDK Support",
              desc: "Works natively with OpenAI, Anthropic, and LangChain SDKs. Drop-in replacement."
            },
            {
              icon: Command,
              title: "CLI Tooling",
              desc: "Manage routing configs, view live logs, and test prompts directly from your terminal."
            },
            {
              icon: Zap,
              title: "Instant Setup",
              desc: "From zero to production in under 5 minutes with our managed cloud offering or Docker."
            }
          ].map((item, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="p-6 rounded-xl border border-white/5 bg-zinc-950 hover:bg-zinc-900 transition-colors"
            >
              <div className="w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center mb-4 border border-white/10">
                <item.icon className="w-5 h-5 text-zinc-300" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">{item.title}</h3>
              <p className="text-sm text-zinc-400 leading-relaxed">{item.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};
