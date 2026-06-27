import { motion } from "framer-motion";
import { Cpu, Database, Cloud, Network, Server, Lock } from "lucide-react";

const technologies = [
  { name: "OpenAI", icon: Cpu },
  { name: "Anthropic", icon: Network },
  { name: "FastAPI", icon: Server },
  { name: "PostgreSQL", icon: Database },
  { name: "Redis", icon: Database },
  { name: "AWS", icon: Cloud },
  { name: "Docker", icon: Server },
  { name: "OAuth2", icon: Lock },
];

export const Integrations = () => {
  return (
    <section className="py-12 border-b border-white/5 bg-zinc-950/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <p className="text-center text-sm font-medium text-zinc-500 mb-8 uppercase tracking-widest">
          Integrates seamlessly with the modern AI stack
        </p>

        <div className="flex flex-wrap justify-center items-center gap-8 md:gap-16 opacity-60 grayscale hover:grayscale-0 transition-all duration-700">
          {technologies.map((tech, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1, duration: 0.5 }}
              className="flex items-center gap-2 text-zinc-400 hover:text-white transition-colors"
            >
              <tech.icon className="w-6 h-6" />
              <span className="font-semibold text-lg hidden sm:block tracking-tight">{tech.name}</span>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};
