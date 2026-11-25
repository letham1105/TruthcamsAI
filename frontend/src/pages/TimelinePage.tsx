
import { useLocation, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  Clock3,
  FileText,
  Search,
  ListFilter,
  Database,
  BrainCircuit,
  Circle,
} from "lucide-react";

const events = [
  {
    title: "Content submitted",
    description: "The input content was submitted for examination.",
    icon: FileText,
  },
  {
    title: "Claim identification",
    description: "Claims were identified or selected for examination.",
    icon: ListFilter,
  },
  {
    title: "Evidence retrieval",
    description: "Relevant documents and sources were retrieved.",
    icon: Search,
  },
  {
    title: "Evidence ranking",
    description: "Retrieved documents were ranked by relevance.",
    icon: Database,
  },
  {
    title: "Evidence analysis",
    description: "Evidence and source context were examined.",
    icon: BrainCircuit,
  },
];

function TimelinePage() {
  const location = useLocation();
  const navigate = useNavigate();

  const claims = (location.state?.claims as string[]) || [];
  const originalText = (location.state?.originalText as string) || "";

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
          Verification history
        </p>

        <h1 className="text-3xl font-bold text-[#142C4E] mt-3">
          Analysis timeline
        </h1>

        <p className="text-gray-500 mt-3 leading-7">
          Review the stages involved in examining the submitted
          information.
        </p>
      </div>

      {(claims.length > 0 || originalText) && (
        <section className="bg-white border border-[#E5E5E0] rounded-2xl p-5 mb-6">
          <h2 className="font-semibold text-[#142C4E]">
            Session context
          </h2>

          {claims.length > 0 ? (
            <div className="space-y-3 mt-4">
              {claims.map((claim, index) => (
                <div key={index} className="flex gap-3">
                  <span className="text-xs text-[#557CA6] mt-1">
                    {index + 1}
                  </span>

                  <p className="text-sm text-gray-600 leading-7">
                    {claim}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-600 leading-7 mt-4">
              {originalText}
            </p>
          )}
        </section>
      )}

      <section className="bg-white border border-[#E5E5E0] rounded-2xl p-6 md:p-8">
        <div className="flex items-center gap-3 mb-8">
          <Clock3 size={21} className="text-[#557CA6]" />

          <div>
            <h2 className="font-semibold text-[#142C4E]">
              Verification stages
            </h2>

            <p className="text-xs text-gray-400 mt-1">
              Workflow overview
            </p>
          </div>
        </div>

        <div className="space-y-0">
          {events.map((event, index) => {
            const Icon = event.icon;
            const last = index === events.length - 1;

            return (
              <div key={index} className="flex gap-4">
                <div className="flex flex-col items-center">
                  <div className="w-11 h-11 rounded-full bg-[#F0F4F8] flex items-center justify-center">
                    <Icon size={20} className="text-[#557CA6]" />
                  </div>

                  {!last && (
                    <div className="w-px h-16 bg-[#E5E5E0]" />
                  )}
                </div>

                <div className="pb-10 pt-1 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="text-sm font-semibold text-[#142C4E]">
                      {event.title}
                    </h3>

                    <span className="text-xs text-gray-400">
                      Pending
                    </span>
                  </div>

                  <p className="text-sm text-gray-500 leading-7 mt-2">
                    {event.description}
                  </p>

                  <p className="text-xs text-gray-400 mt-2">
                    No execution timestamp available
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      <div className="mt-6 flex gap-3 bg-[#F0F4F8] rounded-xl p-4">
        <Circle size={20} className="text-[#557CA6] shrink-0" />

        <p className="text-xs text-gray-500 leading-6">
          Timeline events are currently static workflow descriptions.
          Actual timestamps, execution status and errors will be
          populated from the backend when processing events are
          implemented.
        </p>
      </div>

      <div className="mt-6 flex flex-wrap justify-between gap-4">
        <button
          onClick={() => navigate("/result", { state: location.state })}
          className="flex items-center gap-2 px-5 py-3 rounded-xl border border-[#E5E5E0] text-sm text-gray-600 hover:bg-white"
        >
          <ArrowLeft size={17} />
          Back to report
        </button>

        <button
          onClick={() =>
            navigate("/evidence", {
              state: { claims, originalText },
            })
          }
          className="flex items-center gap-2 px-6 py-3 rounded-xl bg-[#142C4E] text-white text-sm font-medium hover:bg-[#203D63]"
        >
          Explore evidence
        </button>
      </div>
    </div>
  );
}

export default TimelinePage;
