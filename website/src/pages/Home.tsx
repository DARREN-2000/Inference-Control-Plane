import { Hero } from "@/sections/Hero";
import { Features } from "@/sections/Features";
import { Architecture } from "@/sections/Architecture";

export default function Home() {
  return (
    <div className="w-full flex flex-col">
      <Hero />
      <Features />
      <Architecture />

      {/* CTA Section */}
      <section className="py-32 relative overflow-hidden">
        <div className="absolute inset-0 bg-violet-900/10" />
        <div className="max-w-4xl mx-auto px-4 text-center relative z-10">
          <h2 className="text-4xl md:text-5xl font-bold mb-6 tracking-tight text-white">
            Ready to secure your AI traffic?
          </h2>
          <p className="text-xl text-zinc-400 mb-10 max-w-2xl mx-auto">
            Deploy Laminar in minutes and gain complete control over your LLM inference.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="px-8 py-4 bg-white text-black font-semibold rounded-md hover:bg-zinc-200 transition-colors">
              Get Started for Free
            </button>
            <button className="px-8 py-4 bg-zinc-900 text-white font-semibold rounded-md border border-white/10 hover:bg-zinc-800 transition-colors">
              Contact Sales
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
