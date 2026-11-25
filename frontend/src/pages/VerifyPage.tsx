
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  FileText,
  Image as ImageIcon,
  Link2,
  ArrowRight,
  ShieldCheck,
  Search,
  Scale,
  Sparkles,
} from "lucide-react";

type InputMode = "text" | "image" | "url";

function VerifyPage() {
  const [mode, setMode] = useState<InputMode>("text");
  const [claim, setClaim] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [url, setUrl] = useState("");

  const navigate = useNavigate();

  const handleContinue = () => {
    if (mode === "text" && claim.trim()) {
      navigate("/progress", {
        state: { claim: claim.trim() },
      });
    }

    if (mode === "url" && url.trim()) {
      navigate("/progress", {
        state: { claim: url.trim() },
      });
    }

    if (mode === "image" && file) {
      navigate("/ocr-review", {
        state: { file },
      });
    }
  };

  const handleClear = () => {
    setClaim("");
    setUrl("");
    setFile(null);
  };

  const isDisabled =
    (mode === "text" && !claim.trim()) ||
    (mode === "image" && !file) ||
    (mode === "url" && !url.trim());

  return (
    <div className="max-w-5xl mx-auto px-5 py-10 lg:px-10">
      <div className="mb-10">
        <span className="text-sm text-[#557CA6] font-medium">
          AI-powered fact checking
        </span>

        <h1 className="text-3xl md:text-4xl font-bold text-[#142C4E] mt-3">
          Verify information
        </h1>

        <p className="text-gray-500 mt-3 max-w-2xl leading-7">
          Analyze claims, retrieve supporting and contradicting evidence,
          and explore the sources behind online information.
        </p>
      </div>

      <div className="bg-white border border-[#E5E5E0] rounded-2xl shadow-sm p-5 md:p-7">
        {/* Input modes */}
        <div className="flex flex-wrap gap-2 mb-6">
          <button
            onClick={() => setMode("text")}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium ${
              mode === "text"
                ? "bg-[#142C4E] text-white"
                : "bg-gray-50 text-gray-600 hover:bg-gray-100"
            }`}
          >
            <FileText size={17} />
            Text
          </button>

          <button
            onClick={() => setMode("image")}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium ${
              mode === "image"
                ? "bg-[#142C4E] text-white"
                : "bg-gray-50 text-gray-600 hover:bg-gray-100"
            }`}
          >
            <ImageIcon size={17} />
            Screenshot
          </button>

          <button
            onClick={() => setMode("url")}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium ${
              mode === "url"
                ? "bg-[#142C4E] text-white"
                : "bg-gray-50 text-gray-600 hover:bg-gray-100"
            }`}
          >
            <Link2 size={17} />
            URL
          </button>
        </div>

        {/* Text input */}
        {mode === "text" && (
          <div>
            <label className="text-sm font-semibold text-[#202A35]">
              Claim or information
            </label>

            <textarea
              value={claim}
              onChange={(e) => setClaim(e.target.value)}
              placeholder="Paste the information, news, social media post or claim you want to verify..."
              rows={7}
              className="w-full mt-3 p-4 border border-[#E5E5E0] rounded-xl resize-y outline-none focus:border-[#557CA6] focus:ring-2 focus:ring-[#557CA6]/10 text-sm leading-7"
            />

            <p className="text-xs text-gray-400 mt-2">
              Provide the original context whenever possible.
            </p>
          </div>
        )}

        {/* Image input */}
        {mode === "image" && (
          <div>
            <label className="text-sm font-semibold text-[#202A35]">
              Upload screenshot
            </label>

            <label className="mt-3 border-2 border-dashed border-[#D9DEE5] rounded-2xl min-h-[220px] flex flex-col items-center justify-center cursor-pointer hover:bg-[#F8FAFC] transition p-6">
              <div className="w-12 h-12 bg-[#EEF3F8] rounded-full flex items-center justify-center mb-4">
                <ImageIcon size={22} className="text-[#557CA6]" />
              </div>

              <p className="text-sm font-semibold text-[#142C4E]">
                {file ? file.name : "Choose an image"}
              </p>

              <p className="text-xs text-gray-400 mt-2 text-center">
                PNG, JPG or JPEG
              </p>

              <input
                type="file"
                accept="image/png,image/jpeg,image/jpg"
                className="hidden"
                onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              />
            </label>

            {file && (
              <button
                onClick={() => setFile(null)}
                className="text-sm text-red-500 mt-3"
              >
                Remove image
              </button>
            )}
          </div>
        )}

        {/* URL input */}
        {mode === "url" && (
          <div>
            <label className="text-sm font-semibold text-[#202A35]">
              Article or post URL
            </label>

            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://www.facebook.com/..."
              className="w-full mt-3 p-4 border border-[#E5E5E0] rounded-xl outline-none focus:border-[#557CA6] focus:ring-2 focus:ring-[#557CA6]/10 text-sm"
            />

            <p className="text-xs text-gray-400 mt-2">
              Paste a public article or social media post link.
            </p>
          </div>
        )}

        {/* Actions */}
        <div className="flex flex-col sm:flex-row justify-between gap-4 mt-7">
          <button
            onClick={handleClear}
            className="text-sm text-gray-500 hover:text-gray-800 px-3 py-2"
          >
            Clear input
          </button>

          <button
            onClick={handleContinue}
            disabled={isDisabled}
            className="flex items-center justify-center gap-2 bg-[#142C4E] text-white px-6 py-3 rounded-xl text-sm font-medium hover:bg-[#203D63] disabled:opacity-40 disabled:cursor-not-allowed transition"
          >
            Continue verification
            <ArrowRight size={17} />
          </button>
        </div>
      </div>

      {/* How verification works */}
      <div className="mt-10">
        <h2 className="font-semibold text-[#142C4E] text-lg">
          How verification works
        </h2>

        <p className="text-sm text-gray-500 mt-2">
          A multi-step process to help examine claims through evidence.
        </p>

        <div className="grid md:grid-cols-3 gap-4 mt-5">
          {/* Step 1 */}
          <div className="bg-white border border-[#E5E5E0] rounded-2xl p-5">
            <div className="w-10 h-10 rounded-xl bg-[#EEF3F8] flex items-center justify-center">
              <Sparkles size={20} className="text-[#557CA6]" />
            </div>

            <h3 className="font-semibold text-[#142C4E] mt-4">
              01. Claim extraction
            </h3>

            <p className="text-sm text-gray-500 leading-6 mt-2">
              Identify the key information and claims that can be examined.
            </p>
          </div>

          {/* Step 2 */}
          <div className="bg-white border border-[#E5E5E0] rounded-2xl p-5">
            <div className="w-10 h-10 rounded-xl bg-[#EEF3F8] flex items-center justify-center">
              <Search size={20} className="text-[#557CA6]" />
            </div>

            <h3 className="font-semibold text-[#142C4E] mt-4">
              02. Evidence retrieval
            </h3>

            <p className="text-sm text-gray-500 leading-6 mt-2">
              Search, retrieve and rank relevant information from available sources.
            </p>
          </div>

          {/* Step 3 */}
          <div className="bg-white border border-[#E5E5E0] rounded-2xl p-5">
            <div className="w-10 h-10 rounded-xl bg-[#EEF3F8] flex items-center justify-center">
              <Scale size={20} className="text-[#557CA6]" />
            </div>

            <h3 className="font-semibold text-[#142C4E] mt-4">
              03. Evidence analysis
            </h3>

            <p className="text-sm text-gray-500 leading-6 mt-2">
              Examine evidence and explain what the retrieved sources indicate.
            </p>
          </div>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="mt-8 flex items-start gap-3 bg-[#F0F4F8] rounded-xl p-4">
        <ShieldCheck
          size={20}
          className="text-[#557CA6] mt-0.5 shrink-0"
        />

        <p className="text-xs text-gray-500 leading-6">
          TruthCams AI is an AI-assisted analysis tool. Retrieved evidence
          may be incomplete or inaccurate, and results should not be treated
          as definitive truth without independent review.
        </p>
      </div>
    </div>
  );
}

export default VerifyPage;
