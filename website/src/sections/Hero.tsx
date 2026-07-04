import { motion } from "framer-motion";
import { ArrowRight, Terminal } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";

export const Hero = () => {
  return (
    <section className="relative pt-32 pb-20 md:pt-48 md:pb-32 overflow-hidden min-h-screen flex items-center justify-center">
      {/* Animated Background Gradients */}
      <div className="absolute inset-0 bg-black -z-20" />
      <motion.div
        animate={{
          opacity: [0.3, 0.5, 0.3],
          scale: [1, 1.05, 1],
        }}
        transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
        className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-white/5 blur-[120px] rounded-full -z-10 pointer-events-none"
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 w-full">
        <div className="text-center max-w-4xl mx-auto flex flex-col items-center">

          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Badge variant="premium" className="mb-8 px-4 py-1">
              <span className="flex items-center gap-2">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-zinc-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-zinc-500"></span>
                </span>
                Inference Control Plane v2.0 is now generally available
                <ArrowRight className="w-3 h-3 ml-1" />
              </span>
            </Badge>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="text-5xl md:text-7xl lg:text-8xl font-bold tracking-tighter mb-8 leading-[1.1]"
          >
            The enterprise <br />
            <span className="text-gradient-primary">LLM Gateway</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-lg md:text-xl text-zinc-400 mb-10 max-w-2xl mx-auto font-medium"
          >
            Intelligent routing, semantic caching, and real-time observability for AI inference traffic. Built for extreme scale and zero-trust security.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto justify-center"
          >
            <Button size="lg" variant="default" className="gap-2 w-full sm:w-auto" asChild>
              <a href="./dashboard/">
                Start Building Free <ArrowRight className="w-4 h-4" />
              </a>
            </Button>
            <Button size="lg" variant="outline" className="gap-2 w-full sm:w-auto glass">
              <Terminal className="w-4 h-4" /> Read Documentation
            </Button>
          </motion.div>
        </div>

        {/* Interactive Dashboard / Terminal Mockup */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.5 }}
          className="mt-20 relative mx-auto max-w-5xl"
        >
          <div className="absolute inset-0 bg-linear-to-t from-black via-transparent to-transparent z-10 bottom-0 h-1/3 pointer-events-none" />

          <div className="rounded-xl border border-white/5 bg-black backdrop-blur-xl shadow-2xl overflow-hidden relative">
            {/* Mac OS window controls */}
            <div className="h-10 border-b border-white/5 bg-white/5 flex items-center px-4 gap-2">
              <div className="w-3 h-3 rounded-full bg-zinc-800" />
              <div className="w-3 h-3 rounded-full bg-zinc-800" />
              <div className="w-3 h-3 rounded-full bg-zinc-800" />
              <div className="flex-1 flex justify-center text-xs text-zinc-500 font-mono">
                inference_control_plane-dashboard
              </div>
            </div>

            <div className="relative w-full h-[600px] overflow-hidden bg-black/50">
              <iframe
                src={import.meta.env.DEV ? "http://localhost:3000/" : "./dashboard/"}
                className="w-full h-full border-0"
                title="Inference Control Plane Dashboard Playground"
                loading="lazy"
              />
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};
