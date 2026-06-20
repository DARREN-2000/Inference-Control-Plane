import { Outlet } from "react-router";
import { Navigation } from "@/components/Navigation";
import { Footer } from "@/components/Footer";

export const MainLayout = () => {
  return (
    <div className="min-h-screen flex flex-col bg-black text-zinc-50 font-sans selection:bg-cyan-500/30">
      <Navigation />
      <main className="flex-grow flex flex-col relative pt-20">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
};
