import { useEffect, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  CheckCircle2,
  Search,
  BrainCircuit,
  FileText,
  ShieldCheck,
  Loader2,
} from "lucide-react";
import { analyzeText } from "../services/verification";

function VerificationProgressPage() {
  const location = useLocation();
  const navigate = useNavigate();

  const claim = (location.state?.claim as string) || "";
  const claims = (location.state?.claims as string[]) || [];
  const originalText = (location.state?.originalText as string) || "";

  const inputText = originalText || claim || claims.join("\n");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const hasStarted = useRef(false);

  useEffect(() => {
    if (!inputText.trim()) {
      navigate("/", { replace: true });
      return;
    }

    if (hasStarted.current) return;
    hasStarted.current = true;

    const runVerification = async () => {
      try {
        setLoading(true);
        setError("");

        const session = await analyzeText(inputText);

        navigate(`/result/${session.id}`, {
          replace: true,
        });
      } catch (err) {
        console.error("Verification API error:", err);

        setError(
          "Unable to complete verification. Please try again later.",
        );
      } finally {
        setLoading(false);
      }
    };

    runVerification();
  }, [inputText, navigate]);

  return (
    <div className="max-w-4xl mx-auto px-5 py-10 lg:px-10">
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-2 text-sm text-gray-500 hover:text-[#142C4E] mb-7"
      >
        <ArrowLeft size={17} />
        Back
      </button>

      <div className="mb-8">
        <p className="text-sm font-medium text-[#557CA6]">
          Verification
        </p>

        <h1 className="text-3xl font-bold text-[#142C4E] mt-3">
          Verification workflow
        </h1>

        <p className="text-gray-500 mt-3 leading-7">
          Your submitted information is being processed by the
          TruthCams AI verification pipeline.
        </p>
      </div>

      <section className="bg-white border border-[#E5E5E0] rounded-2xl p-5 md:p-6">
        <h2 className="font-semibold text-[#142C4E] mb-4">
          Submitted content
        </h2>

        <div className="bg-[#F5F7FA] rounded-xl p-4">
          <p className="text-sm text-[#202A35] leading-7 whitespace-pre-wrap">
            {inputText}
          </p>
        </div>
      </section>

      <section className="bg-white border border-[#E5E5E0] rounded-2xl p-5 md:p-6 mt-6">
        <h2 className="font-semibold text-[#142C4E] mb-6">
          Pipeline execution
        </h2>

        <div className="flex items-center gap-4">
          <div className="w-11 h-11 rounded-full bg-[#EEF3F8] flex items-center justify-center">
            {loading ? (
              <Loader2
                size={21}
                className="text-[#557CA6] animate-spin"
              />
            ) : (
              <CheckCircle2 size={21} className="text-green-600" />
            )}
          </div>

          <div>
            <h3 className="text-sm font-semibold text-[#142C4E]">
              {loading ? "Analyzing content..." : "Analysis completed"}
            </h3>

            <p className="text-sm text-gray-500 mt-1">
              {loading
                ? "Searching for information and evaluating retrieved evidence. This may take a while."
                : "The request has finished processing."}
            </p>
          </div>
        </div>

        <div className="mt-6 space-y-5">
          {[
            {
              title: "Claim extraction",
              icon: BrainCircuit,
            },
            {
              title: "Evidence retrieval",
              icon: Search,
            },
            {
              title: "Evidence analysis",
              icon: ShieldCheck,
            },
          ].map((step, index) => {
            const Icon = step.icon;

            return (
              <div key={index} className="flex gap-4">
                <div className="w-9 h-9 rounded-full bg-[#F0F2F5] flex items-center justify-center">
                  <Icon size={18} className="text-[#557CA6]" />
                </div>

                <div>
                  <h3 className="text-sm font-medium text-[#142C4E]">
                    {step.title}
                  </h3>

                  <p className="text-xs text-gray-400 mt-1">
                    Processed by the backend pipeline
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {error && (
        <div className="mt-6 bg-red-50 border border-red-200 rounded-xl p-5">
          <h3 className="font-semibold text-red-700">
            Verification failed
          </h3>

          <p className="text-sm text-red-600 mt-2">{error}</p>

          <button
            onClick={() => navigate("/", { replace: true })}
            className="mt-4 px-5 py-2.5 rounded-xl bg-[#142C4E] text-white text-sm"
          >
            Try again
          </button>
        </div>
      )}

      {!error && loading && (
        <div className="mt-6 flex items-start gap-3 bg-[#F0F4F8] rounded-xl p-4">
          <FileText size={20} className="text-[#557CA6] shrink-0" />

          <p className="text-xs text-gray-500 leading-6">
            Do not close this page while the verification request is being processed.
          </p>
        </div>
      )}
    </div>
  );
}

export default VerificationProgressPage;