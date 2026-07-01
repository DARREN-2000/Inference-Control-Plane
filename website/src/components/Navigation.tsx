import { useState, useEffect } from "react";
import { Link } from "react-router";
import { Menu, X, Hexagon } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/Button";

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
        isScrolled ? "glass border-[rgba(255,255,255,0.08)] py-3 shadow-lg" : "bg-transparent py-4"
      )}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center">
          <div className="flex items-center">
            <Link to="/" className="flex items-center gap-2 group">
              <div className="w-8 h-8 rounded-md bg-white text-black flex items-center justify-center transition-transform group-hover:scale-105">
                <span className="font-bold text-lg leading-none">L</span>
              </div>
              <span className="text-white font-semibold text-xl tracking-tight">Inference Control Plane</span>
            </Link>
          </div>

          <div className="hidden md:flex items-center space-x-8">
            <a href="#features" className="text-sm font-medium text-zinc-400 hover:text-white transition-colors">Features</a>
            <a href="#performance" className="text-sm font-medium text-zinc-400 hover:text-white transition-colors">Performance</a>
            <a href="#enterprise" className="text-sm font-medium text-zinc-400 hover:text-white transition-colors">Enterprise</a>
            <a href="#docs" className="text-sm font-medium text-zinc-400 hover:text-white transition-colors">Docs</a>
            <a href="./dashboard/" className="text-sm font-medium text-zinc-400 hover:text-white transition-colors">Dashboard</a>
          </div>

          <div className="hidden md:flex items-center space-x-4">
            <a href="https://github.com/DARREN-2000/Inference-Control-Plane" target="_blank" rel="noopener noreferrer" className="text-zinc-400 hover:text-white transition-colors">
              <Hexagon className="w-5 h-5" />
            </a>
            <Button variant="ghost" size="sm">Sign In</Button>
            <Button size="sm">Get Started</Button>
          </div>

          <div className="md:hidden flex items-center">
            <button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)} className="text-zinc-400 hover:text-white focus:outline-none">
              {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {isMobileMenuOpen && (
        <div className="md:hidden glass border-t border-white/10 absolute top-full left-0 w-full shadow-2xl">
          <div className="px-4 pt-2 pb-6 space-y-1">
            <a href="#features" onClick={() => setIsMobileMenuOpen(false)} className="block px-3 py-3 text-base font-medium text-zinc-300 hover:text-white hover:bg-white/5 rounded-md">Features</a>
            <a href="#performance" onClick={() => setIsMobileMenuOpen(false)} className="block px-3 py-3 text-base font-medium text-zinc-300 hover:text-white hover:bg-white/5 rounded-md">Performance</a>
            <a href="#enterprise" onClick={() => setIsMobileMenuOpen(false)} className="block px-3 py-3 text-base font-medium text-zinc-300 hover:text-white hover:bg-white/5 rounded-md">Enterprise</a>
            <a href="./dashboard/" onClick={() => setIsMobileMenuOpen(false)} className="block px-3 py-3 text-base font-medium text-zinc-300 hover:text-white hover:bg-white/5 rounded-md">Dashboard</a>
            <div className="pt-4 flex flex-col gap-2">
              <Button variant="outline" className="w-full justify-center">Sign In</Button>
              <Button className="w-full justify-center">Get Started</Button>
            </div>
          </div>
        </div>
      )}
    </nav>
  );
};
