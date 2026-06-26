
import { motion } from "framer-motion"
import { cn } from "@/lib/utils"

interface TabsProps {
  tabs: { id: string; label: string }[];
  activeTab: string;
  onChange: (id: string) => void;
  className?: string;
}

export function Tabs({ tabs, activeTab, onChange, className }: TabsProps) {
  return (
    <div className={cn("flex space-x-1 p-1 bg-white/5 rounded-lg border border-white/10", className)}>
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => onChange(tab.id)}
            className={cn(
              "relative px-4 py-2 text-sm font-medium rounded-md transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500",
              isActive ? "text-white" : "text-zinc-400 hover:text-white"
            )}
            style={{ WebkitTapHighlightColor: "transparent" }}
          >
            {isActive && (
              <motion.span
                layoutId="bubble"
                className="absolute inset-0 z-10 bg-white/10 border border-white/10 shadow-sm rounded-md mix-blend-difference"
                transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
              />
            )}
            {tab.label}
          </button>
        );
      })}
    </div>
  );
}
