import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Play, RotateCcw, AlertTriangle, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/Button";

export const Workflow = () => {
  const [step, setStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  const startSimulation = () => {
    setIsPlaying(true);
    setStep(0);

    setTimeout(() => setStep(1), 800);
    setTimeout(() => setStep(2), 2000);
    setTimeout(() => setStep(3), 3200);
    setTimeout(() => {
      setStep(4);
      setIsPlaying(false);
    }, 4500);
  };

  return (
    <section className="py-24 bg-black">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row gap-12 items-center">

          <div className="md:w-1/2">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">
              See the fallback chain in action.
            </h2>
            <p className="text-zinc-400 mb-8 leading-relaxed">
              When OpenAI goes down, your app shouldn't. Laminar detects timeouts and automatically routes the exact same request to Anthropic, entirely transparent to your end-user.
            </p>

            <Button
              onClick={startSimulation}
              disabled={isPlaying}
              variant="outline"
              className="gap-2"
            >
              {isPlaying ? <RotateCcw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
              {isPlaying ? "Simulating Outage..." : "Simulate Provider Outage"}
            </Button>
          </div>

          <div className="md:w-1/2 w-full">
            <div className="bg-zinc-950 border border-white/10 rounded-xl p-6 font-mono text-sm shadow-2xl relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-1 bg-linear-to-r from-violet-500 to-cyan-500" />

              <div className="space-y-4">
                <div className="flex gap-3 text-zinc-500">
                  <span>&gt;</span>
                  <span className="text-zinc-300">User requests chat completion...</span>
                </div>

                <AnimatePresence>
                  {step >= 1 && (
                    <motion.div
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      className="flex gap-3 text-blue-400"
                    >
                      <span>Laminar:</span>
                      <span>Routing to Primary (OpenAI GPT-4)</span>
                    </motion.div>
                  )}

                  {step >= 2 && (
                    <motion.div
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      className="flex gap-3 text-destructive"
                    >
                      <AlertTriangle className="w-4 h-4 mt-0.5" />
                      <span>Timeout: OpenAI API unresponsve (5000ms)</span>
                    </motion.div>
                  )}

                  {step >= 3 && (
                    <motion.div
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      className="flex gap-3 text-amber-400"
                    >
                      <span>Laminar:</span>
                      <span>Executing Fallback Strategy (Anthropic Claude-3)</span>
                    </motion.div>
                  )}

                  {step >= 4 && (
                    <motion.div
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      className="flex gap-3 text-emerald-400 bg-emerald-400/10 p-2 rounded border border-emerald-400/20 mt-4"
                    >
                      <CheckCircle className="w-4 h-4 mt-0.5" />
                      <div>
                        <div>Success: 200 OK (Claude-3)</div>
                        <div className="text-xs text-emerald-500/70 mt-1">Total Latency: 5.8s • Client oblivious to failure</div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
};
