import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Tabs } from "@/components/ui/Tabs";

const tabs = [
  { id: "routing", label: "Smart Routing" },
  { id: "observability", label: "Observability" },
  { id: "keys", label: "Key Management" },
];

export const Screenshots = () => {
  const [activeTab, setActiveTab] = useState("routing");

  return (
    <section className="py-24 bg-zinc-950 border-t border-white/5">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 className="text-3xl font-bold tracking-tight mb-8">
          A control plane you'll actually want to use.
        </h2>

        <div className="flex justify-center mb-12">
          <Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} />
        </div>

        <div className="relative mx-auto max-w-5xl aspect-video rounded-xl border border-white/10 bg-black overflow-hidden shadow-2xl">
          <div className="absolute top-0 w-full h-10 border-b border-white/5 bg-zinc-900/50 flex items-center px-4 gap-2 z-20">
            <div className="w-3 h-3 rounded-full bg-white/20" />
            <div className="w-3 h-3 rounded-full bg-white/20" />
            <div className="w-3 h-3 rounded-full bg-white/20" />
            <div className="flex-1 text-xs text-zinc-500 font-mono text-center pr-8">
              app.inference-control-plane.ai
            </div>
          </div>

          <div className="pt-10 w-full h-full relative">
            <AnimatePresence mode="wait">
              {activeTab === "routing" && (
                <motion.div
                  key="routing"
                  initial={{ opacity: 0, scale: 0.98 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.98 }}
                  transition={{ duration: 0.3 }}
                  className="absolute inset-0 pt-10 p-8 flex items-center justify-center bg-linear-to-br from-violet-900/10 to-black"
                >
                  <div className="w-full max-w-3xl space-y-4">
                    <div className="h-8 w-48 bg-white/10 rounded" />
                    <div className="h-32 w-full bg-white/5 rounded-lg border border-white/10 flex items-center justify-between p-6">
                      <div className="space-y-2">
                        <div className="h-4 w-32 bg-white/20 rounded" />
                        <div className="h-4 w-48 bg-white/10 rounded" />
                      </div>
                      <div className="px-4 py-2 bg-emerald-500/20 text-emerald-400 rounded text-sm border border-emerald-500/20">
                        Active
                      </div>
                    </div>
                    <div className="flex gap-4">
                      <div className="h-24 flex-1 bg-white/5 rounded-lg border border-white/10" />
                      <div className="h-24 flex-1 bg-white/5 rounded-lg border border-white/10" />
                    </div>
                  </div>
                </motion.div>
              )}
              {activeTab === "observability" && (
                <motion.div
                  key="observability"
                  initial={{ opacity: 0, scale: 0.98 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.98 }}
                  transition={{ duration: 0.3 }}
                  className="absolute inset-0 pt-10 p-8 flex items-center justify-center bg-linear-to-br from-cyan-900/10 to-black"
                >
                  <div className="w-full max-w-4xl space-y-4">
                    <div className="flex gap-4">
                      <div className="h-20 flex-1 bg-white/5 rounded-lg border border-white/10 flex flex-col justify-center p-4">
                        <div className="h-3 w-16 bg-white/20 rounded mb-2" />
                        <div className="h-6 w-24 bg-white/40 rounded" />
                      </div>
                      <div className="h-20 flex-1 bg-white/5 rounded-lg border border-white/10 flex flex-col justify-center p-4">
                        <div className="h-3 w-20 bg-white/20 rounded mb-2" />
                        <div className="h-6 w-16 bg-white/40 rounded" />
                      </div>
                      <div className="h-20 flex-1 bg-white/5 rounded-lg border border-white/10 flex flex-col justify-center p-4">
                        <div className="h-3 w-16 bg-white/20 rounded mb-2" />
                        <div className="h-6 w-32 bg-white/40 rounded" />
                      </div>
                    </div>
                    <div className="h-64 w-full bg-white/5 rounded-lg border border-white/10 p-4 relative overflow-hidden">
                      <div className="absolute bottom-0 left-0 w-full h-1/2 bg-linear-to-t from-cyan-500/20 to-transparent" />
                    </div>
                  </div>
                </motion.div>
              )}
              {activeTab === "keys" && (
                <motion.div
                  key="keys"
                  initial={{ opacity: 0, scale: 0.98 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.98 }}
                  transition={{ duration: 0.3 }}
                  className="absolute inset-0 pt-10 p-8 flex items-center justify-center bg-linear-to-br from-rose-900/10 to-black"
                >
                  <div className="w-full max-w-3xl">
                    <div className="flex justify-between items-center mb-6">
                      <div className="h-8 w-48 bg-white/10 rounded" />
                      <div className="h-8 w-32 bg-white/20 rounded" />
                    </div>
                    <div className="space-y-2">
                      {[1, 2, 3].map((i) => (
                        <div
                          key={i}
                          className="h-16 w-full bg-white/5 rounded border border-white/10 flex items-center justify-between px-6"
                        >
                          <div className="h-4 w-64 bg-white/10 rounded" />
                          <div className="h-4 w-24 bg-white/5 rounded" />
                        </div>
                      ))}
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </section>
  );
};
