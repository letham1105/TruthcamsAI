
import { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import {
  ShieldCheck,
  Menu,
  X,
  Clock3,
  FileSearch,
  BookOpen,
  LogIn,
  UserPlus,
  LogOut,
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";

const navItems = [
  { label: "Verify", path: "/", icon: ShieldCheck, end: true },
  { label: "History", path: "/history", icon: Clock3 },
  { label: "Evidence", path: "/evidence", icon: FileSearch },
  { label: "How it works", path: "/how-it-works", icon: BookOpen },
];

function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const closeMenu = () => setMenuOpen(false);

  const handleEvidenceNavigation = () => {
    closeMenu();

    const lastSessionId = localStorage.getItem(
      "truthcams_last_session_id",
    );

    if (lastSessionId && /^\d+$/.test(lastSessionId)) {
      navigate(`/evidence?sessionId=${lastSessionId}`);
    } else {
      navigate("/history");
    }
  };

  const handleLogout = () => {
    logout();
    closeMenu();
    navigate("/login", { replace: true });
  };

  return (
    <header className="sticky top-0 z-50 border-b border-[#E5E5E0] bg-white/95 backdrop-blur-md">
      <div className="mx-auto flex h-[68px] max-w-[1600px] items-center justify-between px-4 sm:px-6 lg:px-8">

        {/* Logo */}
        <NavLink
          to="/"
          onClick={closeMenu}
          className="flex shrink-0 items-center gap-2.5"
        >
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#142C4E]">
            <ShieldCheck size={22} className="text-white" />
          </div>

          <div>
            <h1 className="text-base font-bold leading-tight tracking-tight text-[#142C4E] sm:text-lg">
              TruthCams AI
            </h1>
            <p className="hidden text-[10px] uppercase tracking-[1.4px] text-gray-500 sm:block">
              Evidence-based verification
            </p>
          </div>
        </NavLink>

        {/* Desktop navigation */}
        <nav className="hidden items-center gap-1 lg:flex">
          {navItems.map((item) => {
            const Icon = item.icon;

            if (item.path === "/evidence") {
              return (
                <button
                  key={item.path}
                  type="button"
                  onClick={handleEvidenceNavigation}
                  className="flex items-center gap-2 rounded-xl px-3 py-2.5 text-sm transition-all text-gray-600 hover:bg-gray-50 hover:text-[#142C4E]"
                >
                  <Icon size={17} />
                  {item.label}
                </button>
              );
            }

            return (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.end}
                className={({ isActive }) =>
                  `flex items-center gap-2 rounded-xl px-3 py-2.5 text-sm transition-all ${
                    isActive
                      ? "bg-[#EEF3F8] font-semibold text-[#142C4E]"
                      : "text-gray-600 hover:bg-gray-50 hover:text-[#142C4E]"
                  }`
                }
              >
                <Icon size={17} />
                {item.label}
              </NavLink>
            );
          })}
        </nav>

        {/* Desktop auth actions */}
        <div className="hidden items-center gap-3 lg:flex">
          {isAuthenticated ? (
            <>
              <span className="max-w-[180px] truncate text-sm font-medium text-[#142C4E]">
                {user?.name}
              </span>

              <button
                type="button"
                onClick={handleLogout}
                className="flex items-center gap-2 rounded-xl border border-[#E5E5E0] px-4 py-2.5 text-sm font-medium text-gray-600 transition hover:border-red-200 hover:bg-red-50 hover:text-red-600"
              >
                <LogOut size={17} />
                Logout
              </button>
            </>
          ) : (
            <>
              <NavLink
                to="/login"
                className="flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-medium text-[#142C4E] transition hover:bg-gray-50"
              >
                <LogIn size={17} />
                Login
              </NavLink>

              <NavLink
                to="/register"
                className="flex items-center gap-2 rounded-xl bg-[#142C4E] px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-[#203E65] hover:shadow-md"
              >
                <UserPlus size={17} />
                Get started
              </NavLink>
            </>
          )}
        </div>

        {/* Mobile menu button */}
        <button
          type="button"
          onClick={() => setMenuOpen((prev) => !prev)}
          aria-label={menuOpen ? "Close navigation menu" : "Open navigation menu"}
          aria-expanded={menuOpen}
          className="flex h-10 w-10 items-center justify-center rounded-xl border border-[#E5E5E0] text-[#142C4E] transition hover:bg-gray-50 lg:hidden"
        >
          {menuOpen ? <X size={21} /> : <Menu size={21} />}
        </button>
      </div>

      {/* Mobile navigation */}
      {menuOpen && (
        <div className="border-t border-[#E5E5E0] bg-white px-4 pb-4 pt-3 lg:hidden">
          <nav className="flex flex-col gap-1">
            {navItems.map((item) => {
              const Icon = item.icon;

              if (item.path === "/evidence") {
                return (
                  <button
                    key={item.path}
                    type="button"
                    onClick={handleEvidenceNavigation}
                    className="flex items-center gap-3 rounded-xl px-4 py-3 text-sm text-gray-600 hover:bg-gray-50"
                  >
                    <Icon size={18} />
                    {item.label}
                  </button>
                );
              }

              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  end={item.end}
                  onClick={closeMenu}
                  className={({ isActive }) =>
                    `flex items-center gap-3 rounded-xl px-4 py-3 text-sm ${
                      isActive
                        ? "bg-[#EEF3F8] font-semibold text-[#142C4E]"
                        : "text-gray-600 hover:bg-gray-50"
                    }`
                  }
                >
                  <Icon size={18} />
                  {item.label}
                </NavLink>
              );
            })}
          </nav>

          <div className="mt-3 border-t border-[#E5E5E0] pt-3">
            {isAuthenticated ? (
              <div className="space-y-3">
                <p className="px-2 text-sm font-medium text-[#142C4E]">
                  {user?.name}
                </p>

                <button
                  type="button"
                  onClick={handleLogout}
                  className="flex w-full items-center justify-center gap-2 rounded-xl border border-[#E5E5E0] px-4 py-3 text-sm font-medium text-gray-600 transition hover:bg-red-50 hover:text-red-600"
                >
                  <LogOut size={17} />
                  Logout
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-2">
                <NavLink
                  to="/login"
                  onClick={closeMenu}
                  className="flex items-center justify-center gap-2 rounded-xl border border-[#E5E5E0] px-4 py-3 text-sm font-medium text-[#142C4E] transition hover:bg-gray-50"
                >
                  <LogIn size={17} />
                  Login
                </NavLink>

                <NavLink
                  to="/register"
                  onClick={closeMenu}
                  className="flex items-center justify-center gap-2 rounded-xl bg-[#142C4E] px-4 py-3 text-sm font-semibold text-white transition hover:bg-gray-50"
                >
                  <UserPlus size={17} />
                  Register
                </NavLink>
              </div>
            )}
          </div>
        </div>
      )}
    </header>
  );
}

export default Navbar;
