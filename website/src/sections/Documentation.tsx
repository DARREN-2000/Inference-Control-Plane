import { ArrowRight, Book, Code2, Terminal } from "lucide-react";

export const Documentation = () => {
  return (
    <section className="py-24 bg-black border-t border-b border-white/5">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 className="text-3xl font-bold tracking-tight mb-4">
          Extensive Documentation
        </h2>
        <p className="text-zinc-400 mb-12 max-w-2xl mx-auto">
          Everything you need to set up, configure, and scale your AI gateway.
        </p>

        <div className="grid md:grid-cols-3 gap-6">
          {[
            { title: "Quickstart Guide", icon: Terminal, desc: "Get up and running in 5 minutes with Docker." },
            { title: "API Reference", icon: Code2, desc: "Detailed documentation for all configuration endpoints." },
            { title: "Deployment Specs", icon: Book, desc: "Best practices for production deployments on Kubernetes." }
          ].map((item, i) => (
            <a key={i} href="#" className="group p-6 rounded-xl border border-white/5 bg-zinc-950 hover:bg-zinc-900 transition-colors block text-left">
              <item.icon className="w-6 h-6 text-violet-400 mb-4" />
              <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-violet-400 transition-colors flex items-center justify-between">
                {item.title}
                <ArrowRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity -translate-x-2 group-hover:translate-x-0" />
              </h3>
              <p className="text-sm text-zinc-400">{item.desc}</p>
            </a>
          ))}
        </div>
      </div>
    </section>
  );
};
