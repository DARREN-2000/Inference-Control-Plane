import { useState, useEffect } from "react";
import { Link } from "react-router";
import { Menu, X, Hexagon } from "lucide-react";
import { cn } from "@/lib/utils";

export const Navigation = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <nav
      className={cn(
        "fixed top-0 w-full z-50 transition-all duration-300 border-b border-transparent",
        isScrolled ? "glass border-[rgba(255,255,255,0.08)] py-4" : "bg-transparent py-6"
      )}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center">
          <div className="flex items-center">
            <Link to="/" className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-md bg-gradient-to-tr from-violet-600 to-cyan-500 flex items-center justify-center">
                <span className="text-white font-bold text-lg">L</span>
              </div>
              <span className="text-white font-semibold text-xl tracking-tight">Laminar</span>
            </Link>
          </div>

          <div className="hidden md:flex items-center space-x-8">
            <a href="#features" className="text-sm font-medium text-zinc-400 hover:text-white transition-colors">Features</a>
            <a href="#architecture" className="text-sm font-medium text-zinc-400 hover:text-white transition-colors">Architecture</a>
            <a href="#performance" className="text-sm font-medium text-zinc-400 hover:text-white transition-colors">Performance</a>
            <a href="#enterprise" className="text-sm font-medium text-zinc-400 hover:text-white transition-colors">Enterprise</a>
            <a href="/docs" className="text-sm font-medium text-zinc-400 hover:text-white transition-colors">Docs</a>
          </div>

          <div className="hidden md:flex items-center space-x-4">
            <a href="https://github.com/DARREN-2000/Inference-Control-Plane" target="_blank" rel="noopener noreferrer" className="text-zinc-400 hover:text-white transition-colors">
              <Hexagon className="w-5 h-5" />
            </a>
            <button className="px-4 py-2 text-sm font-medium text-white bg-white/10 hover:bg-white/20 rounded-md transition-colors border border-white/10">
              Sign In
            </button>
            <button className="px-4 py-2 text-sm font-medium text-black bg-white hover:bg-zinc-200 rounded-md transition-colors">
              Get Started
            </button>
          </div>

          <div className="md:hidden flex items-center">
            <button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)} className="text-zinc-400 hover:text-white">
              {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {isMobileMenuOpen && (
        <div className="md:hidden glass border-t border-white/10 absolute top-full left-0 w-full">
          <div className="px-4 pt-2 pb-6 space-y-1">
            <a href="#features" className="block px-3 py-2 text-base font-medium text-zinc-400 hover:text-white">Features</a>
            <a href="#architecture" className="block px-3 py-2 text-base font-medium text-zinc-400 hover:text-white">Architecture</a>
            <a href="#performance" className="block px-3 py-2 text-base font-medium text-zinc-400 hover:text-white">Performance</a>
            <a href="#enterprise" className="block px-3 py-2 text-base font-medium text-zinc-400 hover:text-white">Enterprise</a>
            <div className="pt-4 flex flex-col gap-2">
              <button className="w-full px-4 py-2 text-sm font-medium text-white bg-white/10 rounded-md border border-white/10">Sign In</button>
              <button className="w-full px-4 py-2 text-sm font-medium text-black bg-white rounded-md">Get Started</button>
            </div>
          </div>
        </div>
      )}
    </nav>
  );
};
