import * as React from "react"
import { motion, AnimatePresence } from "framer-motion"
import { ChevronDown } from "lucide-react"
import { cn } from "@/lib/utils"

const AccordionContext = React.createContext<{
  expanded: string | null;
  setExpanded: (id: string | null) => void;
}>({ expanded: null, setExpanded: () => {} });

export function Accordion({ children, className }: { children: React.ReactNode, className?: string }) {
  const [expanded, setExpanded] = React.useState<string | null>(null);

  return (
    <AccordionContext.Provider value={{ expanded, setExpanded }}>
      <div className={cn("space-y-4", className)}>
        {children}
      </div>
    </AccordionContext.Provider>
  )
}

export function AccordionItem({ id, title, children }: { id: string, title: string, children: React.ReactNode }) {
  const { expanded, setExpanded } = React.useContext(AccordionContext);
  const isOpen = expanded === id;

  return (
    <div className="border border-white/10 rounded-lg overflow-hidden bg-zinc-950/50 backdrop-blur-sm transition-colors hover:border-white/20">
      <button
        type="button"
        className="w-full px-6 py-4 flex items-center justify-between text-left focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500"
        onClick={() => setExpanded(isOpen ? null : id)}
        aria-expanded={isOpen}
      >
        <span className="font-medium text-white">{title}</span>
        <ChevronDown
          className={cn(
            "w-5 h-5 text-zinc-400 transition-transform duration-300",
            isOpen && "transform rotate-180 text-white"
          )}
        />
      </button>
      <AnimatePresence initial={false}>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
          >
            <div className="px-6 pb-4 pt-0 text-zinc-400 leading-relaxed">
              {children}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
