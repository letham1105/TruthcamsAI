
import { useLocation, useNavigate, useParams } from "react-router-dom";
import {
  ArrowLeft,
  ExternalLink,
  FileSearch,
  ShieldCheck,
  Info,
  Link2,
} from "lucide-react";

interface EvidenceItem {
  id: string;
  title: string;
  source: string;
  url: string;
  summary: string;
  relevance: number;
  type: "supporting" | "contradicting" | "context";
}

function EvidenceDetailPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { id } = useParams();

  const item = location.state?.item as EvidenceItem | undefined;

  if (!item) {
    return (
      <div className="max-w-3xl mx-auto px-6 py-16">
        <div className="bg-white border border-[#E5E5E0] rounded-2xl p-8 text-center">
          <FileSearch size={36} className="mx-auto text-[#557CA6]" />

          <h1 className="text-xl font-bold text-[#142C4E] mt-4">
            Evidence details unavailable
          </h1>

          <p className="text-sm text-gray-500 mt-3 leading-6">
            This evidence item was not passed to the page. Return to the
            evidence collection to select an item.
          </p>

          <button
            onClick={() => navigate("/evidence")}
            className="mt-6 bg-[#142C4E] text-white px-5 py-3 rounded-xl"
          >
            Back to Evidence
          </button>
        </div>
      </div>
    );
  }

  const typeLabel =
    item.type === "supporting"
      ? "Supporting"
      : item.type === "contradicting"
        ? "Contradicting"
        : "Context";

  return (
    <div className="max-w-4xl mx-auto px-5 py-10 lg:px-10">
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-2 text-sm text-gray-500 hover:text-[#142C4E] mb-7"
      >
        <ArrowLeft size={17} />
        Back to sources
      </button>

      <div className="mb-8">
        <p className="text-sm font-medium text-[#557CA6]">
          Evidence collection · Item {id}
        </p>

        <h1 className="text-3xl font-bold text-[#142C4E] mt-3">
          Evidence detail
        </h1>

        <p className="text-gray-500 mt-3 leading-7">
          Review source information and examine the context of the
          retrieved content.
        </p>
      </div>

      <section className="bg-white border border-[#E5E5E0] rounded-2xl p-6">
        <div className="flex flex-wrap items-center gap-2">
          <span className="px-3 py-1 rounded-full bg-[#F0F2F5] text-gray-600 text-xs font-medium">
            {typeLabel}
          </span>

          <span className="px-3 py-1 rounded-full bg-[#EEF3F8] text-[#557CA6] text-xs font-medium">
            Relevance {item.relevance.toFixed(2)}
          </span>
        </div>

        <h2 className="text-xl md:text-2xl font-bold text-[#142C4E] mt-5 leading-8">
          {item.title}
        </h2>

        <p className="text-sm text-gray-500 mt-3">
          {item.source}
        </p>

        <div className="border-t border-[#E5E5E0] mt-6 pt-6">
          <div className="flex items-center gap-2 text-[#557CA6]">
            <Link2 size={17} />

            <span className="text-sm font-semibold">Source URL</span>
          </div>

          {item.url ? (
            <a
              href={item.url}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-3 text-sm text-[#557CA6] hover:underline break-all inline-flex items-start gap-2"
            >
              {item.url}
              <ExternalLink size={15} className="shrink-0 mt-0.5" />
            </a>
          ) : (
            <p className="text-sm text-gray-400 mt-3">
              No source URL available.
            </p>
          )}
        </div>
      </section>

      <section className="bg-white border border-[#E5E5E0] rounded-2xl p-6 mt-6">
        <h2 className="font-semibold text-[#142C4E]">
          Retrieved content
        </h2>

        <div className="mt-5 border-l-4 border-[#557CA6] bg-[#F5F7FA] rounded-r-xl p-5">
          <p className="text-sm text-gray-600 leading-7">
            {item.summary || "No retrieved text is available."}
          </p>
        </div>

        <p className="text-xs text-gray-400 mt-4 leading-6">
          This content represents the information returned by the
          retrieval pipeline. It should be reviewed in its original
          context before being used to assess a claim.
        </p>
      </section>

      <section className="bg-white border border-[#E5E5E0] rounded-2xl p-6 mt-6">
        <h2 className="font-semibold text-[#142C4E]">
          Relevance information
        </h2>

        <div className="mt-5">
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Retrieval relevance</span>
            <span className="font-semibold text-[#142C4E]">
              {item.relevance.toFixed(3)}
            </span>
          </div>

          <div className="w-full h-2 rounded-full bg-[#EEF1F4] mt-3 overflow-hidden">
            <div
              className="h-full bg-[#557CA6] rounded-full"
              style={{
                width: `${Math.max(0, Math.min(100, item.relevance * 100))}%`,
              }}
            />
          </div>

          <p className="text-xs text-gray-400 mt-3 leading-6">
            The relevance value is a retrieval metric, not a truth score.
            Its interpretation depends on the ranking method used by the
            backend.
          </p>
        </div>
      </section>

      <div className="mt-6 bg-[#F0F4F8] rounded-xl p-4 flex gap-3">
        <Info size={20} className="text-[#557CA6] shrink-0" />

        <p className="text-xs text-gray-500 leading-6">
          This page does not independently establish the credibility
          of the source. Check the original publication, date, author
          and supporting material.
        </p>
      </div>

      <div className="mt-6 flex gap-3 bg-white border border-[#E5E5E0] rounded-2xl p-5">
        <ShieldCheck size={20} className="text-[#557CA6] shrink-0" />

        <p className="text-xs text-gray-500 leading-6">
          TruthCams AI aims to provide transparent evidence retrieval
          and analysis rather than replacing independent verification.
        </p>
      </div>
    </div>
  );
}

export default EvidenceDetailPage;
