
import {
    ShieldCheck,
    Clock3,
    FileSearch,
    BookOpen,
    LayoutDashboard,
  } from "lucide-react";
  import { NavLink } from "react-router-dom";
  
  const menuItems = [
    {
      label: "Verify",
      path: "/",
      icon: ShieldCheck,
    },
    {
      label: "History",
      path: "/history",
      icon: Clock3,
    },
    {
      label: "Evidence",
      path: "/evidence",
      icon: FileSearch,
    },
    {
      label: "How it works",
      path: "/how-it-works",
      icon: BookOpen,
    },
  ];
  
  function Sidebar() {
    return (
      <aside className="w-[240px] shrink-0 bg-white border-r border-[#E5E5E0] min-h-[calc(100vh-68px)] hidden lg:flex flex-col">
        <div className="p-5">
          <p className="text-[11px] font-semibold uppercase tracking-[1.5px] text-gray-400 mb-4">
            Workspace
          </p>
  
          <nav className="space-y-1">
            {menuItems.map((item) => {
              const Icon = item.icon;
  
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  end={item.path === "/"}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-3 rounded-xl text-sm transition-colors ${
                      isActive
                        ? "bg-[#EEF3F8] text-[#142C4E] font-semibold"
                        : "text-gray-600 hover:bg-gray-50"
                    }`
                  }
                >
                  <Icon size={19} />
                  {item.label}
                </NavLink>
              );
            })}
          </nav>
        </div>
  
        <div className="mt-auto p-5">
          <div className="rounded-2xl bg-[#F5F7FA] p-4">
            <div className="flex items-center gap-2 mb-2">
              <LayoutDashboard size={17} className="text-[#557CA6]" />
              <span className="text-sm font-semibold text-[#142C4E]">
                About TruthCams
              </span>
            </div>
  
            <p className="text-xs leading-5 text-gray-500">
              AI-assisted claim analysis with ranked evidence and transparent
              explanations.
            </p>
          </div>
        </div>
      </aside>
    );
  }
  
  export default Sidebar;
  