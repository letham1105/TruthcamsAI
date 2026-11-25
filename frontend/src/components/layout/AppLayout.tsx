import { Outlet } from "react-router-dom";
import Navbar from "./Navbar";

function AppLayout() {
  return (
    <div className="min-h-screen bg-[#FAF9F6]">
      <Navbar />

      <main className="mx-auto w-full max-w-[1600px] min-w-0">
        <Outlet />
      </main>

      <footer className="border-t border-[#E5E5E0] bg-white">
        <div className="mx-auto max-w-[1600px] px-4 py-5 sm:px-6 lg:px-8">
          <p className="text-center text-xs leading-5 text-gray-500">
            TruthCams AI · AI-assisted verification with transparent evidence.
            Results should be reviewed critically.
          </p>
        </div>
      </footer>
    </div>
  );
}

export default AppLayout;
