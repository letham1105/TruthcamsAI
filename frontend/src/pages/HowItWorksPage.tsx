
import {
    ArrowRight,
    FileText,
    Search,
    ListFilter,
    BrainCircuit,
    BookOpen,
    ShieldCheck,
    Image,
    Database,
  } from "lucide-react";
  import { useNavigate } from "react-router-dom";
  
  const processSteps = [
    {
      number: "01",
      title: "Input information",
      description:
        "Submit text, a screenshot or supported content for examination.",
      icon: FileText,
    },
    {
      number: "02",
      title: "Claim identification",
      description:
        "Identify statements that can be examined and review them before proceeding.",
      icon: ListFilter,
    },
    {
      number: "03",
      title: "Evidence retrieval",
      description:
        "Retrieve relevant documents and information from available sources.",
      icon: Search,
    },
    {
      number: "04",
      title: "Evidence ranking",
      description:
        "Organize retrieved information by relevance to the selected claim.",
      icon: Database,
    },
    {
      number: "05",
      title: "Evidence analysis",
      description:
        "Examine source content, context and information that may support or contradict a claim.",
      icon: BrainCircuit,
    },
    {
      number: "06",
      title: "Explanation",
      description:
        "Present the retrieved evidence and analysis so users can evaluate the information.",
      icon: BookOpen,
    },
  ];
  
  function HowItWorksPage() {
    const navigate = useNavigate();
  
    return (
      <div className="max-w-5xl mx-auto px-5 py-10 lg:px-10">
        <div className="mb-10">
          <p className="text-sm font-medium text-[#557CA6]">
            About the platform
          </p>
  
          <h1 className="text-3xl md:text-4xl font-bold text-[#142C4E] mt-3">
            How TruthCams AI works
          </h1>
  
          <p className="text-gray-500 mt-4 leading-7 max-w-2xl">
            A structured approach to examining online information through
            claim identification, evidence retrieval, source analysis and
            transparent explanations.
          </p>
        </div>
  
        <section className="bg-[#142C4E] rounded-2xl p-7 md:p-9 text-white">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-white/10 flex items-center justify-center shrink-0">
              <ShieldCheck size={25} />
            </div>
  
            <div>
              <h2 className="text-xl font-bold">
                Evidence-first information analysis
              </h2>
  
              <p className="text-sm text-white/70 leading-7 mt-3">
                TruthCams AI is designed to help users examine claims
                using retrieved evidence and contextual explanations.
                It does not assume that a model prediction is
                automatically correct.
              </p>
            </div>
          </div>
        </section>
  
        <section className="mt-10">
          <h2 className="text-xl font-bold text-[#142C4E]">
            Verification workflow
          </h2>
  
          <p className="text-sm text-gray-500 mt-2 leading-6">
            Each step contributes to a transparent examination process.
          </p>
  
          <div className="mt-6 space-y-5">
            {processSteps.map((step, index) => {
              const Icon = step.icon;
  
              return (
                <div
                  key={step.number}
                  className="bg-white border border-[#E5E5E0] rounded-2xl p-5 md:p-6 flex gap-5"
                >
                  <div className="shrink-0">
                    <div className="w-12 h-12 rounded-xl bg-[#EEF3F8] flex items-center justify-center">
                      <Icon size={21} className="text-[#557CA6]" />
                    </div>
                  </div>
  
                  <div className="flex-1">
                    <span className="text-xs font-semibold text-[#557CA6]">
                      STEP {step.number}
                    </span>
  
                    <h3 className="font-semibold text-[#142C4E] mt-2">
                      {step.title}
                    </h3>
  
                    <p className="text-sm text-gray-500 leading-7 mt-2">
                      {step.description}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </section>
  
        <section className="mt-10">
          <h2 className="text-xl font-bold text-[#142C4E]">
            Supported input types
          </h2>
  
          <div className="grid md:grid-cols-2 gap-4 mt-5">
            <div className="bg-white border border-[#E5E5E0] rounded-2xl p-6">
              <FileText size={22} className="text-[#557CA6]" />
  
              <h3 className="font-semibold text-[#142C4E] mt-4">
                Text
              </h3>
  
              <p className="text-sm text-gray-500 leading-7 mt-2">
                Paste text or a statement to examine its content and
                identify relevant evidence.
              </p>
            </div>
  
            <div className="bg-white border border-[#E5E5E0] rounded-2xl p-6">
              <Image size={22} className="text-[#557CA6]" />
  
              <h3 className="font-semibold text-[#142C4E] mt-4">
                Screenshot
              </h3>
  
              <p className="text-sm text-gray-500 leading-7 mt-2">
                Submit an image containing text. OCR integration will
                extract the text for review before examination.
              </p>
            </div>
          </div>
        </section>
  
        <section className="mt-10 bg-white border border-[#E5E5E0] rounded-2xl p-6">
          <h2 className="font-semibold text-[#142C4E]">
            Our principles
          </h2>
  
          <div className="space-y-4 mt-5">
            <div>
              <h3 className="text-sm font-medium text-[#142C4E]">
                Transparency
              </h3>
  
              <p className="text-sm text-gray-500 leading-6 mt-2">
                Make sources and evidence available for examination.
              </p>
            </div>
  
            <div>
              <h3 className="text-sm font-medium text-[#142C4E]">
                Context
              </h3>
  
              <p className="text-sm text-gray-500 leading-6 mt-2">
                Consider the original source and surrounding information
                rather than isolated statements.
              </p>
            </div>
  
            <div>
              <h3 className="text-sm font-medium text-[#142C4E]">
                Responsible AI
              </h3>
  
              <p className="text-sm text-gray-500 leading-6 mt-2">
                AI output is an aid to analysis, not a replacement for
                independent judgment.
              </p>
            </div>
          </div>
        </section>
  
        <div className="mt-10">
          <button
            onClick={() => navigate("/")}
            className="flex items-center gap-2 px-6 py-3 bg-[#142C4E] text-white rounded-xl text-sm font-medium hover:bg-[#203D63]"
          >
            Start examining a claim
            <ArrowRight size={17} />
          </button>
        </div>
      </div>
    );
  }
  
  export default HowItWorksPage;
  