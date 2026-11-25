
import { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate, useSearchParams } from "react-router-dom";
import {
  ArrowLeft,
  Search,
  ExternalLink,
  FileSearch,
  SlidersHorizontal,
  ShieldCheck,
  Loader2,
  AlertCircle,
} from "lucide-react";
import {
  getVerification,
  type VerificationSession,
} from "../services/verification";

interface EvidenceItem {
  id: string;
  title: string;
  source: string;
  url: string;
  summary: string;
  relevance: number;
  type: "supporting" | "contradicting" | "context" | "excluded";
}

interface AggregatedClaim {
  claim_id?: number | string;
  claim_text?: string;
  verdict?: string;
  evidence_counts?: {
    supported?: number;
    refuted?: number;
    not_enough_information?: number;
  };
  total_evidence?: number;
  valid_verification_count?: number;
  excluded_evidence_count?: number;
  supporting_evidence?: Record<string, unknown>[];
  refuting_evidence?: Record<string, unknown>[];
  inconclusive_evidence?: Record<string, unknown>[];
  excluded_evidence?: Record<string, unknown>[];
}

function getText(value: unknown): string {
  if (typeof value === "string") return value;
  if (value === null || value === undefined) return "";
  return String(value);
}

function getNestedText(
  evidence: Record<string, unknown>,
  keys: string[],
): string {
  for (const key of keys) {
    const value = evidence[key];

    if (typeof value === "string" && value.trim()) {
      return value;
    }
  }

  return "";
}

function getEvidenceItem(
  evidence: Record<string, unknown>,
  index: number,
  type: EvidenceItem["type"],
): EvidenceItem {
  const verification =
    (evidence.verification as Record<string, unknown>) || {};

  const sourceInfo =
    (evidence.source as Record<string, unknown>) || {};

  const title =
    getNestedText(evidence, [
      "title",
      "article_title",
      "source_title",
    ]) ||
    getText(sourceInfo.title) ||
    "Untitled source";

  const source =
    getNestedText(evidence, [
      "source_name",
      "domain",
      "website",
      "publisher",
    ]) ||
    getText(sourceInfo.name) ||
    getText(sourceInfo.domain) ||
    "Unknown source";

  const url =
    getNestedText(evidence, [
      "url",
      "source_url",
      "article_url",
      "link",
    ]) ||
    getText(sourceInfo.url);

  const summary =
    getNestedText(evidence, [
      "verified_sentence",
      "paragraph_text",
      "original_paragraph_text",
      "snippet",
      "content",
      "text",
    ]) || "No evidence content available.";

  const relevanceValue =
    evidence.relevance_score ??
    evidence.sentence_relevance_score ??
    evidence.similarity_score ??
    evidence.tfidf_score;

  const relevance = Number(relevanceValue ?? 0);

  return {
    id: getText(
      evidence.id ??
      evidence.evidence_id ??
      `${type}-${index}`,
    ),
    title,
    source,
    url,
    summary,
    relevance: Number.isFinite(relevance) ? relevance : 0,
    type,
  };
}

function extractClaims(result: unknown): AggregatedClaim[] {
  if (Array.isArray(result)) {
    return result as AggregatedClaim[];
  }

  if (!result || typeof result !== "object") {
    return [];
  }

  const data = result as Record<string, unknown>;

  const possibleKeys = [
    "aggregated_results",
    "aggregated_claims",
    "claims",
    "results",
  ];

  for (const key of possibleKeys) {
    const value = data[key];

    if (Array.isArray(value)) {
      return value as AggregatedClaim[];
    }
  }

  return [];
}

function EvidencePage() {
  const location = useLocation();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const sessionId = Number(
    searchParams.get("sessionId") ||
    location.state?.sessionId ||
    localStorage.getItem("truthcams_last_session_id"),
  );

  const [session, setSession] =
    useState<VerificationSession | null>(null);

  const [claims, setClaims] = useState<AggregatedClaim[]>([]);
  const [selectedClaimIndex, setSelectedClaimIndex] = useState(0);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [searchTerm, setSearchTerm] = useState("");
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    if (!Number.isFinite(sessionId) || sessionId <= 0) {
      setError("Verification session ID is missing.");
      setLoading(false);
      return;
    }

    let cancelled = false;

    const fetchEvidence = async () => {
      try {
        setLoading(true);
        setError("");

        const response = await getVerification(sessionId);

        if (cancelled) return;

        setSession(response);

        const extractedClaims = extractClaims(response.result);

        setClaims(extractedClaims);
        setSelectedClaimIndex(0);

        if (extractedClaims.length === 0) {
          console.warn(
            "Unable to find aggregated claim results:",
            response.result,
          );
        }
      } catch (err) {
        console.error("Failed to load evidence:", err);

        if (!cancelled) {
          setError("Unable to load evidence from this verification session.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchEvidence();

    return () => {
      cancelled = true;
    };
  }, [sessionId]);

  const selectedClaim = claims[selectedClaimIndex];

  const evidence = useMemo(() => {
    if (!selectedClaim) return [];

    const items: EvidenceItem[] = [];

    const groups: {
      key: keyof AggregatedClaim;
      type: EvidenceItem["type"];
    }[] = [
      { key: "supporting_evidence", type: "supporting" },
      { key: "refuting_evidence", type: "contradicting" },
      { key: "inconclusive_evidence", type: "context" },
      { key: "excluded_evidence", type: "excluded" },
    ];

    groups.forEach(({ key, type }) => {
      const group = selectedClaim[key];

      if (!Array.isArray(group)) return;

      group.forEach((item, index) => {
        items.push(
          getEvidenceItem(
            item as Record<string, unknown>,
            index,
            type,
          ),
        );
      });
    });

    return items;
  }, [selectedClaim]);

  const counts = useMemo(() => {
    return {
      total: evidence.length,
      supporting: evidence.filter(
        (item) => item.type === "supporting",
      ).length,
      contradicting: evidence.filter(
        (item) => item.type === "contradicting",
      ).length,
      context: evidence.filter(
        (item) => item.type === "context",
      ).length,
      excluded: evidence.filter(
        (item) => item.type === "excluded",
      ).length,
    };
  }, [evidence]);

  const filteredEvidence = useMemo(() => {
    return evidence.filter((item) => {
      const term = searchTerm.toLowerCase();

      const matchesSearch =
        item.title.toLowerCase().includes(term) ||
        item.source.toLowerCase().includes(term) ||
        item.summary.toLowerCase().includes(term);

      const matchesFilter =
        filter === "all" || item.type === filter;

      return matchesSearch && matchesFilter;
    });
  }, [evidence, searchTerm, filter]);

  const getTypeLabel = (type: EvidenceItem["type"]) => {
    switch (type) {
      case "supporting":
        return "Supporting";
      case "contradicting":
        return "Refuting";
      case "context":
        return "Inconclusive";
      case "excluded":
        return "Excluded";
    }
  };

  const getTypeStyle = (type: EvidenceItem["type"]) => {
    switch (type) {
      case "supporting":
        return "bg-[#EDF3EE] text-[#52745A]";
      case "contradicting":
        return "bg-[#F5EEEE] text-[#956060]";
      case "context":
        return "bg-[#F5F2E9] text-[#8A7950]";
      case "excluded":
        return "bg-[#F0F0EF] text-[#777773]";
    }
  };

  const statCards = [
    {
      label: "Supporting",
      value: counts.supporting,
      type: "supporting" as const,
    },
    {
      label: "Refuting",
      value: counts.contradicting,
      type: "contradicting" as const,
    },
    {
      label: "Inconclusive",
      value: counts.context,
      type: "context" as const,
    },
    {
      label: "Excluded",
      value: counts.excluded,
      type: "excluded" as const,
    },
  ];

  if (loading) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center bg-[#FAF9F6] px-5">
        <Loader2
          size={32}
          className="animate-spin text-[#557CA6]"
        />
        <h2 className="text-base font-semibold text-[#142C4E] mt-5">
          Loading evidence
        </h2>
        <p className="text-sm text-gray-500 mt-2">
          Please wait while we retrieve the evidence and sources.
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-[70vh] bg-[#FAF9F6]">
        <div className="max-w-5xl mx-auto px-5 py-10 lg:px-10">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 text-sm text-gray-500 hover:text-[#142C4E] mb-8"
          >
            <ArrowLeft size={17} />
            Back
          </button>

          <div className="bg-white border border-[#E5E5E0] rounded-xl p-6">
            <div className="flex items-start gap-3">
              <AlertCircle
                size={21}
                className="text-[#A56B6B] shrink-0"
              />
              <div>
                <h2 className="font-semibold text-[#142C4E]">
                  Evidence unavailable
                </h2>
                <p className="text-sm text-gray-500 mt-2">
                  {error}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#FAF9F6]">
      <div className="max-w-5xl mx-auto px-5 py-10 lg:px-10">

        {/* Back */}
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 text-sm text-gray-500 hover:text-[#142C4E] transition-colors mb-8"
        >
          <ArrowLeft size={17} />
          Back
        </button>

        {/* Header */}
        <header className="mb-8">
          <p className="text-sm font-medium text-[#557CA6]">
            Research workspace
          </p>

          <h1 className="text-3xl font-bold text-[#142C4E] mt-2">
            Evidence & Sources
          </h1>

          <p className="text-sm text-gray-500 mt-3 leading-7 max-w-2xl">
            Explore retrieved sources and inspect evidence evaluated by the verification pipeline.
          </p>
        </header>

        {/* Claims */}
        <section className="bg-white border border-[#E5E5E0] rounded-xl p-6 lg:p-7 mb-6">
          <div className="flex items-center justify-between gap-3">
            <div>
              <h2 className="text-base font-semibold text-[#142C4E]">
                Claims under examination
              </h2>
              <p className="text-xs text-gray-400 mt-1">
                {claims.length} {claims.length === 1 ? "claim" : "claims"} analyzed
              </p>
            </div>
          </div>

          {claims.length > 0 ? (
            <div className="mt-5 space-y-2">
              {claims.map((claim, index) => (
                <button
                  key={claim.claim_id ?? index}
                  onClick={() => {
                    setSelectedClaimIndex(index);
                    setSearchTerm("");
                    setFilter("all");
                  }}
                  className={`w-full text-left rounded-lg border px-4 py-3.5 transition-colors ${
                    selectedClaimIndex === index
                      ? "border-[#AFC1D3] bg-[#F5F7F9]"
                      : "border-[#EAEAE6] bg-white hover:bg-[#FAFAF8]"
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <span className="text-xs font-semibold text-[#557CA6] mt-1 shrink-0">
                      C{index + 1}
                    </span>

                    <p className="text-sm text-[#454B53] leading-6 flex-1">
                      {claim.claim_text || `Claim ${index + 1}`}
                    </p>

                    <span className="text-xs text-[#557CA6] shrink-0 mt-1">
                      {selectedClaimIndex === index ? "Selected" : "View"}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-500 mt-4">
              No aggregated claims were found in this verification session.
            </p>
          )}
        </section>

        {/* Evidence overview */}
        <section className="mb-7">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-base font-semibold text-[#142C4E]">
              Evidence overview
            </h2>
            <span className="text-xs text-gray-500">
              {counts.total} records
            </span>
          </div>

          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            {statCards.map((stat) => (
              <div
                key={stat.type}
                className="bg-white border border-[#E5E5E0] rounded-xl p-4"
              >
                <div className="flex items-center justify-between gap-2">
                  <p className="text-xs text-gray-500">
                    {stat.label}
                  </p>
                  <span
                    className={`w-2 h-2 rounded-full ${
                      stat.type === "supporting"
                        ? "bg-[#78977D]"
                        : stat.type === "contradicting"
                          ? "bg-[#B98282]"
                          : stat.type === "context"
                            ? "bg-[#B9A879]"
                            : "bg-[#A5A5A0]"
                    }`}
                  />
                </div>

                <p className="text-2xl font-semibold text-[#142C4E] mt-3">
                  {stat.value}
                </p>
                <p className="text-xs text-gray-400 mt-1">
                  Evidence records
                </p>
              </div>
            ))}
          </div>
        </section>

        {/* Evidence collection */}
        <section className="bg-white border border-[#E5E5E0] rounded-xl p-6 lg:p-7">
          <div className="flex flex-col gap-4">
            <div>
              <h2 className="text-base font-semibold text-[#142C4E]">
                Evidence collection
              </h2>
              <p className="text-sm text-gray-500 mt-1">
                {counts.total} evidence records for the selected claim.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-3">
              <div className="relative flex-1">
                <Search
                  size={16}
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
                />
                <input
                  value={searchTerm}
                  onChange={(event) => setSearchTerm(event.target.value)}
                  placeholder="Search evidence..."
                  className="w-full pl-9 pr-3 py-2.5 bg-white border border-[#E5E5E0] rounded-lg text-sm text-[#454B53] placeholder:text-gray-400 outline-none focus:border-[#AFC1D3] transition-colors"
                />
              </div>

              <div className="relative sm:w-48">
                <SlidersHorizontal
                  size={15}
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"
                />
                <select
                  value={filter}
                  onChange={(event) => setFilter(event.target.value)}
                  className="w-full appearance-none pl-9 pr-3 py-2.5 bg-white border border-[#E5E5E0] rounded-lg text-sm text-[#454B53] outline-none focus:border-[#AFC1D3]"
                >
                  <option value="all">All evidence</option>
                  <option value="supporting">Supporting</option>
                  <option value="contradicting">Refuting</option>
                  <option value="context">Inconclusive</option>
                  <option value="excluded">Excluded</option>
                </select>
              </div>
            </div>
          </div>

          {/* Evidence list */}
          <div className="mt-5 border-t border-[#EEEEEA]">
            {filteredEvidence.length > 0 ? (
              <div className="divide-y divide-[#EEEEEA]">
                {filteredEvidence.map((item) => (
                  <article
                    key={item.id}
                    className="py-5"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <div className="flex flex-wrap items-center gap-2">
                        <span
                          className={`px-2.5 py-1 rounded-md text-xs font-medium ${getTypeStyle(item.type)}`}
                        >
                          {getTypeLabel(item.type)}
                        </span>

                        <span className="text-xs text-gray-400">
                          Relevance: {(item.relevance * 100).toFixed(1)}%
                        </span>
                      </div>

                      {item.url && (
                        <a
                          href={item.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 text-xs text-[#557CA6] hover:text-[#142C4E] transition-colors"
                        >
                          View source
                          <ExternalLink size={13} />
                        </a>
                      )}
                    </div>

                    <h3 className="text-sm font-semibold text-[#142C4E] mt-3 leading-6">
                      {item.title}
                    </h3>

                    <p className="text-xs text-gray-400 mt-1">
                      {item.source}
                    </p>

                    <p className="text-sm text-gray-600 mt-3 leading-7 whitespace-pre-wrap">
                      {item.summary}
                    </p>

                    <button
                      onClick={() =>
                        navigate(`/evidence/${item.id}`, {
                          state: {
                            item,
                            sessionId,
                            claim: selectedClaim,
                          },
                        })
                      }
                      className="mt-3 text-sm font-medium text-[#557CA6] hover:text-[#142C4E] transition-colors"
                    >
                      View details
                    </button>
                  </article>
                ))}
              </div>
            ) : (
              <div className="text-center py-14">
                <FileSearch
                  size={32}
                  className="mx-auto text-gray-300"
                  strokeWidth={1.5}
                />

                <h3 className="text-sm font-semibold text-[#142C4E] mt-4">
                  No evidence found
                </h3>

                <p className="text-sm text-gray-500 mt-2">
                  {evidence.length === 0
                    ? "There is no evidence available for this claim."
                    : "Try changing your search term or filter."}
                </p>
              </div>
            )}
          </div>
        </section>

        {/* Disclaimer */}
        <div className="flex items-start gap-3 mt-5 px-1 text-xs text-gray-500 leading-6">
          <ShieldCheck
            size={16}
            className="shrink-0 mt-0.5 text-[#557CA6]"
          />
          <p>
            Evidence labels represent automated model predictions.
            Relevance scores indicate similarity to the selected claim
            and should not be interpreted as probabilities of truth.
            Excluded evidence is not used in claim-level verdict aggregation.
          </p>
        </div>

      </div>
    </div>
  );
}

export default EvidencePage;
