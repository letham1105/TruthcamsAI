import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { ShieldCheck, Eye, EyeOff, ArrowRight } from "lucide-react";
import { useAuth } from "../context/AuthContext";

function RegisterPage() {
  const { register, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (password.length < 8) {
      setError("Password must contain at least 8 characters.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      await register(name, email, password);
      navigate("/", { replace: true });
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Registration failed."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-68px)] px-4 py-10 sm:px-6 sm:py-16">
      <div className="mx-auto grid w-full max-w-5xl overflow-hidden rounded-3xl border border-[#E5E5E0] bg-white shadow-sm lg:grid-cols-2">

        {/* Introduction */}
        <div className="hidden flex-col justify-between bg-[#142C4E] p-10 text-white lg:flex xl:p-14">
          <div>
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-white/10">
                <ShieldCheck size={25} />
              </div>

              <div>
                <h1 className="font-bold text-lg">TruthCams AI</h1>
                <p className="text-xs text-blue-200">
                  Evidence-based verification
                </p>
              </div>
            </div>

            <div className="mt-20">
              <p className="text-xs font-semibold uppercase tracking-[2px] text-blue-200">
                Research the claim
              </p>

              <h2 className="mt-4 max-w-sm text-4xl font-semibold leading-tight">
                Information deserves examination.
              </h2>

              <p className="mt-5 max-w-sm text-sm leading-7 text-blue-100/80">
                Discover relevant sources, explore supporting
                and contradicting evidence, and understand
                how claims are assessed.
              </p>
            </div>
          </div>

          <div className="border-t border-white/15 pt-5">
            <p className="text-xs leading-6 text-blue-100/70">
              Explore evidence. Check sources. Think critically.
            </p>
          </div>
        </div>

        {/* Registration form */}
        <div className="flex items-center justify-center p-6 sm:p-10 lg:p-12">
          <div className="w-full max-w-md">

            {/* Mobile logo */}
            <div className="mb-8 flex items-center gap-3 lg:hidden">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#142C4E]">
                <ShieldCheck size={22} className="text-white" />
              </div>

              <div>
                <h1 className="font-bold text-[#142C4E]">
                  TruthCams AI
                </h1>
                <p className="text-xs text-gray-500">
                  Evidence-based verification
                </p>
              </div>
            </div>

            <div>
              <p className="text-xs font-semibold uppercase tracking-[1.5px] text-[#557CA6]">
                Get started
              </p>

              <h2 className="mt-2 text-3xl font-bold tracking-tight text-[#142C4E]">
                Create an account
              </h2>

              <p className="mt-3 text-sm leading-6 text-gray-500">
                Create your account to get started.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="mt-8 space-y-5">
              <div>
                <label
                  htmlFor="name"
                  className="mb-2 block text-sm font-medium text-[#202A35]"
                >
                  Full name
                </label>

                <input
                  id="name"
                  type="text"
                  autoComplete="name"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Your name"
                  className="w-full rounded-xl border border-[#E5E5E0] px-4 py-3 text-sm outline-none transition focus:border-[#557CA6] focus:ring-2 focus:ring-[#557CA6]/10"
                />
              </div>

              <div>
                <label
                  htmlFor="email"
                  className="mb-2 block text-sm font-medium text-[#202A35]"
                >
                  Email address
                </label>

                <input
                  id="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@example.com"
                  className="w-full rounded-xl border border-[#E5E5E0] px-4 py-3 text-sm outline-none transition focus:border-[#557CA6] focus:ring-2 focus:ring-[#557CA6]/10"
                />
              </div>

              <div>
                <label
                  htmlFor="password"
                  className="mb-2 block text-sm font-medium text-[#202A35]"
                >
                  Password
                </label>

                <div className="relative">
                  <input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    autoComplete="new-password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="At least 8 characters"
                    className="w-full rounded-xl border border-[#E5E5E0] px-4 py-3 pr-12 text-sm outline-none transition focus:border-[#557CA6] focus:ring-2 focus:ring-[#557CA6]/10"
                  />

                  <button
                    type="button"
                    onClick={() => setShowPassword((prev) => !prev)}
                    aria-label={
                      showPassword
                        ? "Hide password"
                        : "Show password"
                    }
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-[#142C4E]"
                  >
                    {showPassword ? (
                      <EyeOff size={18} />
                    ) : (
                      <Eye size={18} />
                    )}
                  </button>
                </div>
              </div>

              <div>
                <label
                  htmlFor="confirmPassword"
                  className="mb-2 block text-sm font-medium text-[#202A35]"
                >
                  Confirm password
                </label>

                <input
                  id="confirmPassword"
                  type="password"
                  autoComplete="new-password"
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Confirm your password"
                  className="w-full rounded-xl border border-[#E5E5E0] px-4 py-3 text-sm outline-none transition focus:border-[#557CA6] focus:ring-2 focus:ring-[#557CA6]/10"
                />
              </div>

              {error && (
                <div
                  role="alert"
                  className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600"
                >
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="flex w-full items-center justify-center gap-2 rounded-xl bg-[#142C4E] px-4 py-3.5 text-sm font-semibold text-white transition hover:bg-[#203E65] disabled:cursor-not-allowed disabled:opacity-60"
              >
                {loading ? "Creating account..." : "Create account"}

                {!loading && <ArrowRight size={17} />}
              </button>
            </form>

            <p className="mt-6 text-center text-sm text-gray-500">
              Already have an account?{" "}
              <Link
                to="/login"
                className="font-semibold text-[#142C4E] hover:underline"
              >
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default RegisterPage;