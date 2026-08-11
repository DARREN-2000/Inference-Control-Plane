import { motion } from "framer-motion";
import { Check } from "lucide-react";
import { Button } from "@/components/ui/Button";

export const EnterpriseFeatures = () => {
  return (
    <section
      id="enterprise"
      className="py-24 bg-zinc-950 border-t border-b border-white/5 relative overflow-hidden"
    >
      <div className="absolute right-0 top-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-violet-600/10 blur-[120px] rounded-full pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          <div>
            <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-6">
              Ready for production workloads.
            </h2>
            <p className="text-lg text-zinc-400 mb-8 leading-relaxed">
              Whether you are a startup scaling your first AI feature or a
              Fortune 500 company securing hundreds of LLM applications,
              Inference Control Plane has you covered.
            </p>

            <div className="grid sm:grid-cols-2 gap-4 mb-8">
              {[
                "SOC2 Compliance",
                "SLA Guarantees",
                "Self-Hosted Options",
                "Priority Support",
                "Custom Integrations",
                "Dedicated Account Manager",
              ].map((feature, i) => (
                <div key={i} className="flex items-center gap-3">
                  <div className="w-5 h-5 rounded-full bg-emerald-500/10 flex items-center justify-center">
                    <Check className="w-3 h-3 text-emerald-400" />
                  </div>
                  <span className="text-zinc-300 text-sm font-medium">
                    {feature}
                  </span>
                </div>
              ))}
            </div>

            <Button size="lg" className="w-full sm:w-auto">
              Contact Sales
            </Button>
          </div>

          <div className="relative lg:ml-auto w-full max-w-md">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              className="bg-black border border-white/10 rounded-2xl p-8 shadow-2xl relative z-20"
            >
              <h3 className="text-xl font-bold text-white mb-2">
                Self-Hosted Deployment
              </h3>
              <p className="text-sm text-zinc-400 mb-6">
                Deploy Inference Control Plane in your own VPC for maximum
                security and compliance.
              </p>

              <div className="space-y-4">
                <div className="p-3 bg-zinc-900 border border-white/5 rounded-lg flex items-center justify-between">
                  <span className="text-sm text-zinc-300">Docker</span>
                  <span className="text-xs text-zinc-500 font-mono">
                    docker-compose.yml
                  </span>
                </div>
                <div className="p-3 bg-zinc-900 border border-white/5 rounded-lg flex items-center justify-between">
                  <span className="text-sm text-zinc-300">Kubernetes</span>
                  <span className="text-xs text-zinc-500 font-mono">
                    Helm Chart
                  </span>
                </div>
                <div className="p-3 bg-zinc-900 border border-white/5 rounded-lg flex items-center justify-between">
                  <span className="text-sm text-zinc-300">AWS</span>
                  <span className="text-xs text-zinc-500 font-mono">
                    CloudFormation
                  </span>
                </div>
              </div>
            </motion.div>

            <div className="absolute -top-6 -right-6 w-full h-full border border-white/5 rounded-2xl -z-10 bg-zinc-900/50 backdrop-blur-sm" />
            <div className="absolute -bottom-6 -left-6 w-full h-full border border-white/5 rounded-2xl -z-20 bg-zinc-900/20" />
          </div>
        </div>
      </div>
    </section>
  );
};
