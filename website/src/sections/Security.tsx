import { motion } from "framer-motion";
import { Shield, EyeOff, LockKeyhole, FileKey2 } from "lucide-react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/Card";

export const Security = () => {
  return (
    <section className="py-24 relative overflow-hidden bg-black border-t border-white/5">
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-lg h-[400px] bg-amber-500/10 blur-[100px] -z-10 rounded-full" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center mb-16 max-w-3xl mx-auto">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-amber-500/10 text-amber-500 mb-6 border border-amber-500/20">
            <Shield className="w-6 h-6" />
          </div>
          <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-6">
            Zero-Trust by design.
          </h2>
          <p className="text-lg text-zinc-400">
            Enterprise AI requires enterprise security. Inference Control Plane
            ensures sensitive data never reaches third-party APIs without
            explicit consent.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {[
            {
              icon: EyeOff,
              title: "On-the-fly PII Redaction",
              desc: "Automatically detect and mask emails, SSNs, and credit cards before they leave your infrastructure using local NLP models.",
            },
            {
              icon: LockKeyhole,
              title: "Local Secret Management",
              desc: "Provider API keys remain securely encrypted in your PostgreSQL instance. Never expose raw keys to application developers.",
            },
            {
              icon: FileKey2,
              title: "RBAC & Virtual Keys",
              desc: "Issue granular virtual keys to teams or clients with strict spend limits and model access controls.",
            },
          ].map((item, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
            >
              <Card className="h-full bg-zinc-950/40 hover:bg-zinc-900/50 transition-colors">
                <CardHeader>
                  <item.icon className="w-6 h-6 text-amber-400 mb-4" />
                  <CardTitle className="text-xl">{item.title}</CardTitle>
                  <CardDescription className="text-base text-zinc-400 mt-2">
                    {item.desc}
                  </CardDescription>
                </CardHeader>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};
