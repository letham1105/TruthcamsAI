import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  ArrowRight,
  Clock3,
  FileText,
  Search,
  Trash2,
  Loader2,
  RefreshCw,
} from "lucide-react";
import {
  deleteVerification,
  getVerificationHistory,
  type VerificationHistoryItem,
} from "../services/verification";

function HistoryPage() {
  const navigate = useNavigate();

  const [items, setItems] = useState<VerificationHistoryItem[]>([]);
  const [total, setTotal] = useState(0);
  const [limit] = useState(20);
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const loadHistory = useCallback(async () => {
    try {
      setLoading(true);
      setError("");

      const response = await getVerificationHistory(limit, offset);

      setItems(response.items);
      setTotal(response.total);
    } catch (err) {
      console.error("Failed to load history:", err);
      setError("Unable to load verification history.");
    } finally {
      setLoading(false);
    }
  }, [limit, offset]);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const handleDelete = async (id: number) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this verification session?",
    );

    if (!confirmed) return;

    try {
      setDeletingId(id);
      await deleteVerification(id);

      // If deleting the last item on a page, move back one page.
      if (items.length === 1 && offset > 0) {
        setOffset(Math.max(0, offset - limit));
      } else {
        await loadHistory();
      }
    } catch (err) {
      console.error("Failed to delete session:", err);
      setError("Unable to delete this verification session.");
    } finally {
      setDeletingId(null);
    }
  };

  const filteredItems = items.filter((item) =>
    item.original_input.toLowerCase().includes(search.toLowerCase()),
  );

  const formatDate = (value: string) =>
    new Date(value).toLocaleString(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    });

  const getStatusClass = (status: string) => {
    switch (status) {
      case "success":
        return "bg-green-100 text-green-700";
      case "partial":
        return "bg-yellow-100 text-yellow-700";
      case "processing":
        return "bg-blue-100 text-blue-700";
      default:
        return "bg-red-100 text-red-700";
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-5 py-10 lg:px-10">
      <div className="mb-8">
        <p className="text-sm font-medium text-[#557CA6]">
          Workspace
        </p>

        <h1 className="text-3xl font-bold text-[#142C4E] mt-3">
          Verification history
        </h1>

        <p className="text-gray-500 mt-3 leading-7">
          Review previous verification sessions and revisit reports stored in the database.
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white border border-[#E5E5E0] rounded-2xl p-5">
          <div className="flex items-center gap-3">
            <Clock3 size={20} className="text-[#557CA6]" />
            <span className="text-sm text-gray-500">
              Total sessions
            </span>
          </div>

          <p className="text-3xl font-bold text-[#142C4E] mt-4">
            {total}
          </p>

          <p className="text-xs text-gray-400 mt-2">
            Stored in database
          </p>
        </div>

        <div className="bg-white border border-[#E5E5E0] rounded-2xl p-5">
          <div className="flex items-center gap-3">
            <FileText size={20} className="text-[#557CA6]" />
            <span className="text-sm text-gray-500">
              Sessions on this page
            </span>
          </div>

          <p className="text-3xl font-bold text-[#142C4E] mt-4">
            {items.length}
          </p>

          <p className="text-xs text-gray-400 mt-2">
            Current page
          </p>
        </div>

        <div className="bg-white border border-[#E5E5E0] rounded-2xl p-5">
          <div className="flex items-center gap-3">
            <Search size={20} className="text-[#557CA6]" />
            <span className="text-sm text-gray-500">
              Search results
            </span>
          </div>

          <p className="text-3xl font-bold text-[#142C4E] mt-4">
            {filteredItems.length}
          </p>

          <p className="text-xs text-gray-400 mt-2">
            On current page
          </p>
        </div>
      </div>

      <section className="bg-white border border-[#E5E5E0] rounded-2xl p-6">
        <div className="flex flex-col sm:flex-row justify-between gap-4 mb-6">
          <div>
            <h2 className="font-semibold text-[#142C4E]">
              Recent sessions
            </h2>

            <p className="text-sm text-gray-500 mt-2">
              Select a session to view its report.
            </p>
          </div>

          <button
            onClick={loadHistory}
            disabled={loading}
            className="flex items-center gap-2 px-3 py-2.5 border border-[#E5E5E0] rounded-xl text-sm text-gray-600 hover:bg-gray-50 disabled:opacity-50"
          >
            <RefreshCw
              size={16}
              className={loading ? "animate-spin" : ""}
            />
            Refresh
          </button>
        </div>

        <div className="flex items-center gap-2 px-3 py-3 border border-[#E5E5E0] rounded-xl mb-5">
          <Search size={17} className="text-gray-400" />

          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search submitted content..."
            className="w-full outline-none text-sm"
          />
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-5">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        {loading ? (
          <div className="py-16 flex flex-col items-center">
            <Loader2 size={30} className="animate-spin text-[#557CA6]" />
            <p className="text-sm text-gray-500 mt-4">
              Loading history...
            </p>
          </div>
        ) : filteredItems.length === 0 ? (
          <div className="border border-dashed border-[#D9DEE5] rounded-2xl py-16 px-6 text-center">
            <div className="w-14 h-14 rounded-full bg-[#F0F4F8] flex items-center justify-center mx-auto">
              <Clock3 size={25} className="text-[#557CA6]" />
            </div>

            <h3 className="font-semibold text-[#142C4E] mt-5">
              {search
                ? "No matching sessions"
                : "No verification history"}
            </h3>

            <p className="text-sm text-gray-500 max-w-md mx-auto mt-3 leading-7">
              {search
                ? "Try a different search term."
                : "Your verification sessions will appear here after analysis."}
            </p>

            {!search && (
              <button
                onClick={() => navigate("/")}
                className="mt-6 px-5 py-3 rounded-xl bg-[#142C4E] text-white text-sm font-medium hover:bg-[#203D63] inline-flex items-center gap-2"
              >
                Start verification
                <ArrowRight size={17} />
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            {filteredItems.map((item) => (
              <div
                key={item.id}
                className="border border-[#E5E5E0] rounded-2xl p-5 hover:border-[#B9C8D8] transition"
              >
                <div className="flex flex-col md:flex-row justify-between gap-4">
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-3 mb-3">
                      <span
                        className={`px-3 py-1 rounded-lg text-xs font-semibold ${getStatusClass(item.status)}`}
                      >
                        {item.status.toUpperCase()}
                      </span>

                      <span className="text-xs text-gray-400">
                        ID #{item.id}
                      </span>

                      <span className="text-xs text-gray-400">
                        {formatDate(item.created_at)}
                      </span>
                    </div>

                    <p className="text-sm text-[#202A35] leading-7 whitespace-pre-wrap break-words">
                      {item.original_input}
                    </p>
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    <button
                      onClick={() => navigate(`/result/${item.id}`)}
                      className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#142C4E] text-white text-sm hover:bg-[#203D63]"
                    >
                      View report
                      <ArrowRight size={16} />
                    </button>

                    <button
                      onClick={() => handleDelete(item.id)}
                      disabled={deletingId === item.id}
                      title="Delete session"
                      className="flex items-center justify-center w-10 h-10 rounded-xl border border-red-200 text-red-600 hover:bg-red-50 disabled:opacity-50"
                    >
                      {deletingId === item.id ? (
                        <Loader2 size={17} className="animate-spin" />
                      ) : (
                        <Trash2 size={17} />
                      )}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {!loading && total > limit && (
          <div className="flex justify-between items-center mt-6 pt-5 border-t border-[#E5E5E0]">
            <button
              disabled={offset === 0}
              onClick={() => setOffset(Math.max(0, offset - limit))}
              className="px-4 py-2 border border-[#E5E5E0] rounded-xl text-sm disabled:opacity-40"
            >
              Previous
            </button>

            <span className="text-sm text-gray-500">
              {offset + 1}–{Math.min(offset + limit, total)} of {total}
            </span>

            <button
              disabled={offset + limit >= total}
              onClick={() => setOffset(offset + limit)}
              className="px-4 py-2 border border-[#E5E5E0] rounded-xl text-sm disabled:opacity-40"
            >
              Next
            </button>
          </div>
        )}
      </section>

      <p className="text-xs text-gray-400 mt-5 flex items-center gap-2">
        <Trash2 size={14} />
        Deleted sessions are removed from the database.
      </p>
    </div>
  );
}

export default HistoryPage;