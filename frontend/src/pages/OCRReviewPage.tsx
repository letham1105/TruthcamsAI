import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  ArrowRight,
  FileImage,
  RefreshCw,
  ScanText,
  ShieldCheck,
  AlertCircle,
  Loader2,
  CheckCircle2,
} from "lucide-react";

import { extractImageText } from "../services/verification";

function OCRReviewPage() {
  const location = useLocation();
  const navigate = useNavigate();

  const file = location.state?.file as File | undefined;

  const [preview, setPreview] = useState("");
  const [ocrText, setOcrText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [ocrError, setOcrError] = useState("");
  const [ocrCompleted, setOcrCompleted] = useState(false);

  // Create image preview
  useEffect(() => {
    if (!file) {
      setPreview("");
      return;
    }

    const objectUrl = URL.createObjectURL(file);
    setPreview(objectUrl);

    return () => URL.revokeObjectURL(objectUrl);
  }, [file]);

  // Automatically run OCR when the page opens
  useEffect(() => {
    if (!file) return;

    let cancelled = false;

    const runOCR = async () => {
      setIsLoading(true);
      setOcrError("");
      setOcrCompleted(false);

      try {
        const result = await extractImageText(file);

        if (cancelled) return;

        setOcrText(result.text || "");
        setOcrCompleted(true);

        if (!result.text?.trim()) {
          setOcrError(
            "No text was detected. You can manually enter the content below.",
          );
        }
      } catch (error) {
        if (cancelled) return;

        console.error("OCR failed:", error);

        setOcrError(
          "Unable to extract text from this image. You can manually enter or paste the content below.",
        );
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    };

    runOCR();

    return () => {
      cancelled = true;
    };
  }, [file]);

  const handleRetryOCR = async () => {
    if (!file) return;

    setIsLoading(true);
    setOcrError("");
    setOcrCompleted(false);

    try {
      const result = await extractImageText(file);

      setOcrText(result.text || "");
      setOcrCompleted(true);

      if (!result.text?.trim()) {
        setOcrError("No text was detected in this image.");
      }
    } catch (error) {
      console.error("OCR retry failed:", error);

      setOcrError(
        "OCR failed again. You can continue by entering text manually.",
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleContinue = () => {
    if (!ocrText.trim()) return;

    navigate("/claims", {
      state: {
        originalText: ocrText.trim(),
        file,
      },
    });
  };

  if (!file) {
    return (
      <div className="max-w-3xl mx-auto px-6 py-16">
        <div className="bg-white border border-[#E5E5E0] rounded-2xl p-8 text-center">
          <FileImage size={36} className="mx-auto text-[#557CA6]" />

          <h1 className="text-xl font-bold text-[#142C4E] mt-4">
            No screenshot found
          </h1>

          <p className="text-sm text-gray-500 mt-2">
            Please upload a screenshot from the verification page.
          </p>

          <button
            onClick={() => navigate("/")}
            className="mt-6 bg-[#142C4E] text-white px-5 py-3 rounded-xl"
          >
            Back to Verify
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-5 py-10 lg:px-10">
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-2 text-sm text-gray-500 hover:text-[#142C4E] mb-7"
      >
        <ArrowLeft size={17} />
        Back
      </button>

      <div className="mb-8">
        <p className="text-sm font-medium text-[#557CA6]">
          Verification · Step 1
        </p>

        <h1 className="text-3xl font-bold text-[#142C4E] mt-3">
          Review extracted text
        </h1>

        <p className="text-gray-500 mt-3 leading-7">
          Review the screenshot and extracted content. Correct the text if
          needed before identifying claims.
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6 items-start">
        {/* Original screenshot */}
        <section className="bg-white border border-[#E5E5E0] rounded-2xl p-5">
          <div className="flex items-center gap-2 mb-5">
            <FileImage size={18} className="text-[#557CA6]" />

            <h2 className="font-semibold text-[#142C4E]">
              Original screenshot
            </h2>
          </div>

          <div className="bg-[#F5F5F3] rounded-xl overflow-hidden min-h-[300px] flex items-center justify-center">
            {preview ? (
              <img
                src={preview}
                alt="Uploaded screenshot"
                className="max-h-[600px] w-full object-contain"
              />
            ) : (
              <p className="text-sm text-gray-400">
                Image preview unavailable
              </p>
            )}
          </div>

          <p className="text-xs text-gray-400 mt-4 break-all">
            {file.name}
          </p>

          <button
            onClick={() => navigate("/")}
            className="text-sm text-[#557CA6] mt-4 hover:underline"
          >
            Upload another image
          </button>
        </section>

        {/* OCR content */}
        <section className="bg-white border border-[#E5E5E0] rounded-2xl p-5">
          <div className="flex items-center gap-2 mb-5">
            <ScanText size={18} className="text-[#557CA6]" />

            <h2 className="font-semibold text-[#142C4E]">
              Extracted content
            </h2>
          </div>

          {/* OCR status */}
          {isLoading && (
            <div className="bg-[#F0F4F8] rounded-xl p-4 mb-5">
              <div className="flex items-center gap-2 text-[#557CA6]">
                <Loader2 size={18} className="animate-spin" />

                <span className="text-sm font-medium">
                  Extracting text from image...
                </span>
              </div>

              <p className="text-xs text-gray-500 mt-2 leading-5">
                Please wait while we process your screenshot.
              </p>
            </div>
          )}

          {!isLoading && ocrCompleted && !ocrError && (
            <div className="bg-green-50 rounded-xl p-4 mb-5">
              <div className="flex items-center gap-2 text-green-700">
                <CheckCircle2 size={18} />

                <span className="text-sm font-medium">
                  OCR completed
                </span>
              </div>

              <p className="text-xs text-gray-500 mt-2 leading-5">
                Text was extracted successfully. Review and edit it
                before continuing.
              </p>
            </div>
          )}

          {!isLoading && ocrError && (
            <div className="bg-amber-50 rounded-xl p-4 mb-5">
              <div className="flex items-center gap-2 text-amber-700">
                <AlertCircle size={18} />

                <span className="text-sm font-medium">
                  OCR notice
                </span>
              </div>

              <p className="text-xs text-gray-600 mt-2 leading-5">
                {ocrError}
              </p>

              <button
                onClick={handleRetryOCR}
                disabled={isLoading}
                className="mt-3 flex items-center gap-2 text-sm text-[#557CA6] font-medium hover:underline disabled:opacity-50"
              >
                <RefreshCw size={15} />
                Retry OCR
              </button>
            </div>
          )}

          <label className="text-sm font-semibold text-[#202A35]">
            Text to analyze
          </label>

          <textarea
            value={ocrText}
            onChange={(e) => setOcrText(e.target.value)}
            placeholder="Extracted text will appear here. You can also type or paste content manually..."
            rows={12}
            className="w-full mt-3 border border-[#E5E5E0] rounded-xl p-4 text-sm leading-7 outline-none focus:border-[#557CA6] resize-y"
          />

          <div className="flex justify-between mt-3">
            <span className="text-xs text-gray-400">
              {ocrText.length} characters
            </span>

            <button
              onClick={() => setOcrText("")}
              className="text-xs text-gray-500 hover:text-red-500"
            >
              Clear text
            </button>
          </div>
        </section>
      </div>

      {/* Navigation */}
      <div className="flex flex-col sm:flex-row justify-between gap-4 mt-8">
        <button
          onClick={() => navigate("/")}
          className="flex items-center gap-2 px-5 py-3 rounded-xl border border-[#E5E5E0] text-sm text-gray-600 hover:bg-white"
        >
          <ArrowLeft size={17} />
          Back to Verify
        </button>

        <button
          onClick={handleContinue}
          disabled={!ocrText.trim() || isLoading}
          className="flex items-center gap-2 px-6 py-3 rounded-xl bg-[#142C4E] text-white text-sm font-medium hover:bg-[#203D63] disabled:opacity-40 disabled:cursor-not-allowed"
        >
          Continue to claims
          <ArrowRight size={17} />
        </button>
      </div>

      {/* Disclaimer */}
      <div className="mt-8 bg-[#F0F4F8] rounded-xl p-4 flex gap-3">
        <ShieldCheck size={20} className="text-[#557CA6] shrink-0" />

        <p className="text-xs text-gray-500 leading-6">
          The extracted text may contain errors. Review names, dates,
          numbers and other details before proceeding.
        </p>
      </div>
    </div>
  );
}

export default OCRReviewPage;