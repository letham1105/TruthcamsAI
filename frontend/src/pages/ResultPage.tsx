
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  ArrowLeft,
  ShieldCheck,
  FileSearch,
  AlertCircle,
  Loader2,
  RefreshCw,
  History,
} from "lucide-react";
import {
  getVerification,
  type VerificationSession,
} from "../services/verification";

function ResultPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [session, setSession] = useState<VerificationSession | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id || isNaN(Number(id))) {
      navigate("/", { replace: true });
      return;
    }

    const fetchSession = async () => {
      try {
        setLoading(true);
        setError("");

        const result = await getVerification(Number(id));
        setSession(result);

        localStorage.setItem(
          "truthcams_last_session_id",
          String(result.id),
        );
      } catch (err) {
        console.error("Failed to load verification session:", err);
        setError("Unable to load this verification report.");
      } finally {
        setLoading(false);
      }
    };

    fetchSession();
  }, [id, navigate]);

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto px-5 py-24 flex flex-col items-center justify-center">
        <Loader2 size={36} className="animate-spin text-[#557CA6]" />

        <h2 className="text-lg font-semibold text-[#142C4E] mt-5">
          Preparing your verification report
        </h2>

        <p className="text-sm text-gray-500 mt-2 text-center">
          Please wait while we load the analysis results.
        </p>
      </div>
    );
  }

  if (error || !session) {
    return (
      <div className="max-w-5xl mx-auto px-5 py-10 lg:px-10">
        <div className="bg-red-50 border border-red-200 rounded-2xl p-6">
          <div className="flex items-start gap-3">
            <AlertCircle
              size={22}
              className="text-red-600 shrink-0 mt-1"
            />

            <div>
              <h2 className="font-semibold text-red-700">
                Report unavailable
              </h2>

              <p className="text-sm text-red-600 mt-2 leading-6">
                {error || "Verification session not found."}
              </p>

              <button
                onClick={() => navigate("/history")}
                className="mt-5 px-5 py-3 bg-[#142C4E] text-white rounded-xl text-sm font-medium hover:bg-[#203E65]"
              >
                View history
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const status = session.status;

  const statusConfig = {
    success: {
      label: "Analysis completed",
      className: "bg-green-100 text-green-700",
      description:
        "The verification analysis has completed. Explore the collected evidence and sources to review the findings.",
    },
    partial: {
      label: "Partially completed",
      className: "bg-yellow-100 text-yellow-700",
      description:
        "The analysis was partially completed. Some results may be unavailable, so review the evidence carefully.",
    },
    processing: {
      label: "Processing",
      className: "bg-blue-100 text-blue-700",
      description:
        "This verification is still being processed. Please check again later.",
    },
    failed: {
      label: "Analysis failed",
      className: "bg-red-100 text-red-700",
      description:
        "The analysis could not be completed. You may try submitting the content again.",
    },
  };

  const currentStatus = statusConfig[status];

  return (
    <div className="max-w-5xl mx-auto px-5 py-10 lg:px-10">
      {/* Back button */}
      <button
        onClick={() => navigate("/history")}
        className="flex items-center gap-2 text-sm text-gray-500 hover:text-[#142C4E] transition-colors mb-8"
      >
        <ArrowLeft size={17} />
        Back to history
      </button>

      {/* Header */}
      <div className="mb-8">
        <p className="text-sm font-medium text-[#557CA6]">
          Verification report
        </p>

        <h1 className="text-3xl font-bold text-[#142C4E] mt-3">
          Analysis results
        </h1>

        <p className="text-gray-500 mt-3 leading-7">
          Review the analysis status and explore the evidence
          collected for the submitted content.
        </p>
      </div>

      {/* Status card */}
      <section className="bg-white border border-[#E5E5E0] rounded-2xl p-6 lg:p-8">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 rounded-xl bg-[#EEF3F8] flex items-center justify-center shrink-0">
            <ShieldCheck size={25} className="text-[#557CA6]" />
          </div>

          <div className="flex-1">
            <h2 className="text-lg font-semibold text-[#142C4E]">
              Verification status
            </h2>

            <div className="mt-4">
              <span
                className={`inline-flex px-3 py-1.5 rounded-lg text-sm font-semibold ${currentStatus.className}`}
              >
                {currentStatus.label}
              </span>
            </div>

            <p className="text-sm text-gray-600 mt-4 leading-7">
              {currentStatus.description}
            </p>
          </div>
        </div>
      </section>

      {/* Submitted content */}
      <section className="bg-white border border-[#E5E5E0] rounded-2xl p-6 lg:p-8 mt-6">
        <h2 className="font-semibold text-[#142C4E]">
          Submitted content
        </h2>

        <div className="mt-4 bg-[#F5F7FA] rounded-xl p-5">
          <p className="text-sm text-gray-700 leading-7 whitespace-pre-wrap break-words">
            {session.original_input}
          </p>
        </div>
      </section>

      {/* Session error */}
      {session.error && (
        <section className="bg-red-50 border border-red-200 rounded-2xl p-5 mt-6">
          <div className="flex items-start gap-3">
            <AlertCircle
              size={20}
              className="text-red-600 shrink-0 mt-1"
            />

            <div>
              <h2 className="text-sm font-semibold text-red-800">
                Processing notice
              </h2>

              <p className="text-sm text-red-700 mt-2 leading-6 whitespace-pre-wrap">
                {session.error}
              </p>
            </div>
          </div>
        </section>
      )}

      {/* Evidence navigation */}
      <section className="bg-[#F5F7FA] border border-[#DCE5EF] rounded-2xl p-6 lg:p-8 mt-6">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 rounded-xl bg-white flex items-center justify-center shrink-0">
            <FileSearch size={24} className="text-[#557CA6]" />
          </div>

          <div className="flex-1">
            <h2 className="text-lg font-semibold text-[#142C4E]">
              Explore evidence & sources
            </h2>

            <p className="text-sm text-gray-600 mt-2 leading-7">
              Explore the evidence collected from different sources,
              review supporting and refuting information, and examine
              the sources behind the analysis.
            </p>

            <button
              onClick={() =>
                navigate(`/evidence?sessionId=${session.id}`)
              }
              disabled={status === "processing" || status === "failed"}
              className="mt-5 inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-[#557CA6] text-white text-sm font-medium hover:bg-[#41688F] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <FileSearch size={17} />
              View evidence and sources
            </button>

            {status === "processing" && (
              <p className="text-xs text-gray-500 mt-3">
                Evidence is not yet available while processing.
              </p>
            )}

            {status === "failed" && (
              <p className="text-xs text-gray-500 mt-3">
                Evidence is unavailable because the analysis failed.
              </p>
            )}
          </div>
        </div>
      </section>

      {/* Bottom actions */}
      <div className="mt-8 flex flex-col sm:flex-row justify-between gap-3">
        <button
          onClick={() => navigate("/")}
          className="flex items-center justify-center gap-2 px-5 py-3 rounded-xl border border-[#E5E5E0] text-sm text-gray-600 hover:bg-white transition-colors"
        >
          <RefreshCw size={17} />
          New verification
        </button>

        <button
          onClick={() => navigate("/history")}
          className="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-[#142C4E] text-white text-sm font-medium hover:bg-[#203E65] transition-colors"
        >
          <History size={17} />
          View history
        </button>
      </div>
    </div>
  );
}

export default ResultPage;
