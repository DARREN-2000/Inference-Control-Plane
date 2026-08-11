import { Outlet } from "react-router";
import { Navigation } from "@/components/Navigation";
import { Footer } from "@/components/Footer";

export const MainLayout = () => {
  return (
    <div className="min-h-screen flex flex-col bg-black text-white relative">
      <Navigation />
      <main className="flex-grow flex flex-col relative z-0">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
};
