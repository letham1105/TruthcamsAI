
import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  ArrowRight,
  Check,
  Plus,
  Trash2,
  FileText,
  Info,
} from "lucide-react";

interface ClaimItem {
  id: number;
  text: string;
  selected: boolean;
}

function ClaimSelectionPage() {
  const location = useLocation();
  const navigate = useNavigate();

  const originalText = (location.state?.originalText as string) || "";
  const file = location.state?.file as File | undefined;

  const [claims, setClaims] = useState<ClaimItem[]>(() => {
    const initial = originalText
      .split(/(?<=[.!?。！？])\s+/)
      .map((sentence) => sentence.trim())
      .filter(Boolean);

    return initial.map((text, index) => ({
      id: index + 1,
      text,
      selected: true,
    }));
  });

  const [newClaim, setNewClaim] = useState("");

  const selectedCount = claims.filter((claim) => claim.selected).length;

  const toggleClaim = (id: number) => {
    setClaims((prev) =>
      prev.map((claim) =>
        claim.id === id ? { ...claim, selected: !claim.selected } : claim,
      ),
    );
  };

  const updateClaim = (id: number, text: string) => {
    setClaims((prev) =>
      prev.map((claim) =>
        claim.id === id ? { ...claim, text } : claim,
      ),
    );
  };

  const removeClaim = (id: number) => {
    setClaims((prev) => prev.filter((claim) => claim.id !== id));
  };

  const addClaim = () => {
    if (!newClaim.trim()) return;

    setClaims((prev) => [
      ...prev,
      {
        id: Date.now(),
        text: newClaim.trim(),
        selected: true,
      },
    ]);

    setNewClaim("");
  };

  const handleContinue = () => {
    const selectedClaims = claims
      .filter((claim) => claim.selected && claim.text.trim())
      .map((claim) => claim.text.trim());

    if (!selectedClaims.length) return;

    navigate("/progress", {
      state: {
        claims: selectedClaims,
        originalText,
        file,
      },
    });
  };

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
          Verification · Step 2
        </p>

        <h1 className="text-3xl font-bold text-[#142C4E] mt-3">
          Select claims to examine
        </h1>

        <p className="text-gray-500 mt-3 leading-7">
          Review the text below. Select the statements you want to examine
          and edit them if necessary.
        </p>
      </div>

      <div className="bg-white border border-[#E5E5E0] rounded-2xl p-5 md:p-6">
        <div className="flex items-center justify-between gap-3 mb-5">
          <div className="flex items-center gap-2">
            <FileText size={18} className="text-[#557CA6]" />

            <h2 className="font-semibold text-[#142C4E]">
              Claim candidates
            </h2>
          </div>

          <span className="text-xs text-gray-500">
            {selectedCount} selected
          </span>
        </div>

        {claims.length === 0 && (
          <div className="text-center py-10">
            <p className="text-sm text-gray-500">
              No claim candidates yet. Add a statement below.
            </p>
          </div>
        )}

        <div className="space-y-4">
          {claims.map((claim, index) => (
            <div
              key={claim.id}
              className={`border rounded-xl p-4 transition ${
                claim.selected
                  ? "border-[#557CA6] bg-[#F8FAFC]"
                  : "border-[#E5E5E0] bg-white"
              }`}
            >
              <div className="flex items-start gap-3">
                <button
                  onClick={() => toggleClaim(claim.id)}
                  className={`w-6 h-6 rounded-md shrink-0 flex items-center justify-center border mt-1 ${
                    claim.selected
                      ? "bg-[#142C4E] border-[#142C4E] text-white"
                      : "border-gray-300 bg-white"
                  }`}
                  aria-label={`Toggle claim ${index + 1}`}
                >
                  {claim.selected && <Check size={15} />}
                </button>

                <div className="flex-1 min-w-0">
                  <div className="flex justify-between gap-3 mb-3">
                    <span className="text-xs text-gray-400">
                      Claim {index + 1}
                    </span>

                    <button
                      onClick={() => removeClaim(claim.id)}
                      className="text-gray-400 hover:text-red-500"
                      title="Remove claim"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>

                  <textarea
                    value={claim.text}
                    onChange={(e) => updateClaim(claim.id, e.target.value)}
                    rows={Math.max(2, Math.ceil(claim.text.length / 90))}
                    className="w-full bg-transparent resize-y outline-none text-sm text-[#202A35] leading-7"
                  />
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="border-t border-[#E5E5E0] mt-6 pt-6">
          <label className="text-sm font-semibold text-[#142C4E]">
            Add a claim manually
          </label>

          <textarea
            value={newClaim}
            onChange={(e) => setNewClaim(e.target.value)}
            rows={3}
            placeholder="Enter another statement you want to examine..."
            className="w-full mt-3 p-4 border border-[#E5E5E0] rounded-xl outline-none focus:border-[#557CA6] text-sm leading-6"
          />

          <button
            onClick={addClaim}
            disabled={!newClaim.trim()}
            className="mt-3 flex items-center gap-2 px-4 py-2.5 border border-[#E5E5E0] rounded-xl text-sm text-[#142C4E] hover:bg-gray-50 disabled:opacity-40"
          >
            <Plus size={17} />
            Add claim
          </button>
        </div>
      </div>

      <div className="mt-6 bg-[#F0F4F8] rounded-xl p-4 flex gap-3">
        <Info size={20} className="text-[#557CA6] shrink-0" />

        <p className="text-xs text-gray-500 leading-6">
          Statements are currently separated using basic text rules.
          This is not automatic AI claim extraction. Selecting a statement
          does not mean the statement is true or false.
        </p>
      </div>

      <div className="flex justify-between gap-4 mt-8">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 px-5 py-3 rounded-xl border border-[#E5E5E0] text-sm text-gray-600 hover:bg-white"
        >
          <ArrowLeft size={17} />
          Back
        </button>

        <button
          onClick={handleContinue}
          disabled={selectedCount === 0}
          className="flex items-center gap-2 px-6 py-3 rounded-xl bg-[#142C4E] text-white text-sm font-medium hover:bg-[#203D63] disabled:opacity-40"
        >
          Examine selected claims
          <ArrowRight size={17} />
        </button>
      </div>
    </div>
  );
}

export default ClaimSelectionPage;
