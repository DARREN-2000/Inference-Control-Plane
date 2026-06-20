// Removing lucide-react brand icons as they are not available in this version. Using an alternative.
import { Hexagon, MessageCircle, Briefcase } from "lucide-react";

export const Footer = () => {
  return (
    <footer className="border-t border-white/10 bg-black pt-16 pb-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-12">
          <div className="col-span-2 md:col-span-1">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-6 h-6 rounded-md bg-gradient-to-tr from-violet-600 to-cyan-500 flex items-center justify-center">
                <span className="text-white font-bold text-xs">L</span>
              </div>
              <span className="text-white font-semibold tracking-tight">Laminar</span>
            </div>
            <p className="text-sm text-zinc-400 mb-6 max-w-xs">
              The enterprise control plane for AI inference. Route, cache, and observe all your LLM traffic.
            </p>
            <div className="flex items-center space-x-4 text-zinc-400">
              <a href="#" className="hover:text-white transition-colors"><Hexagon className="w-5 h-5" /></a>
              <a href="#" className="hover:text-white transition-colors"><MessageCircle className="w-5 h-5" /></a>
              <a href="#" className="hover:text-white transition-colors"><Briefcase className="w-5 h-5" /></a>
            </div>
          </div>

          <div>
            <h3 className="text-sm font-semibold text-white mb-4">Product</h3>
            <ul className="space-y-3">
              <li><a href="#" className="text-sm text-zinc-400 hover:text-white transition-colors">Features</a></li>
              <li><a href="#" className="text-sm text-zinc-400 hover:text-white transition-colors">Integrations</a></li>
              <li><a href="#" className="text-sm text-zinc-400 hover:text-white transition-colors">Pricing</a></li>
              <li><a href="#" className="text-sm text-zinc-400 hover:text-white transition-colors">Changelog</a></li>
              <li><a href="#" className="text-sm text-zinc-400 hover:text-white transition-colors">Docs</a></li>
            </ul>
          </div>

          <div>
            <h3 className="text-sm font-semibold text-white mb-4">Company</h3>
            <ul className="space-y-3">
              <li><a href="#" className="text-sm text-zinc-400 hover:text-white transition-colors">About</a></li>
              <li><a href="#" className="text-sm text-zinc-400 hover:text-white transition-colors">Blog</a></li>
              <li><a href="#" className="text-sm text-zinc-400 hover:text-white transition-colors">Careers</a></li>
              <li><a href="#" className="text-sm text-zinc-400 hover:text-white transition-colors">Customers</a></li>
              <li><a href="#" className="text-sm text-zinc-400 hover:text-white transition-colors">Contact</a></li>
            </ul>
          </div>

          <div>
            <h3 className="text-sm font-semibold text-white mb-4">Legal</h3>
            <ul className="space-y-3">
              <li><a href="#" className="text-sm text-zinc-400 hover:text-white transition-colors">Privacy Policy</a></li>
              <li><a href="#" className="text-sm text-zinc-400 hover:text-white transition-colors">Terms of Service</a></li>
              <li><a href="#" className="text-sm text-zinc-400 hover:text-white transition-colors">Cookie Policy</a></li>
              <li><a href="#" className="text-sm text-zinc-400 hover:text-white transition-colors">Security</a></li>
            </ul>
          </div>
        </div>

        <div className="pt-8 border-t border-white/10 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-xs text-zinc-500">
            &copy; {new Date().getFullYear()} Laminar Inc. All rights reserved.
          </p>
          <div className="flex items-center gap-2">
            <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="text-xs text-zinc-500">All systems operational</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
