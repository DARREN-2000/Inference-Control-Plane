import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/Button";

export const Cta = () => {
  return (
    <section className="py-32 relative overflow-hidden bg-black">
      <div className="absolute inset-0 bg-linear-to-b from-transparent to-violet-900/20" />
      <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[800px] h-[300px] bg-violet-600/30 blur-[120px] rounded-full pointer-events-none" />

      <div className="max-w-4xl mx-auto px-4 text-center relative z-10">
        <h2 className="text-4xl md:text-6xl font-bold mb-6 tracking-tight text-white leading-tight">
          Ready to secure your <br />
          <span className="text-gradient-primary">AI traffic?</span>
        </h2>
        <p className="text-xl text-zinc-400 mb-10 max-w-2xl mx-auto">
          Deploy Inference Control Plane in minutes and gain complete control, visibility, and reliability over your LLM inference.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button size="lg" className="gap-2">
            Get Started Free <ArrowRight className="w-4 h-4" />
          </Button>
          <Button size="lg" variant="outline" className="glass">
            Book a Demo
          </Button>
        </div>
      </div>
    </section>
  );
};
