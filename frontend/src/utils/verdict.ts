export type Verdict =
  | "supported"
  | "refuted"
  | "conflicting_evidence"
  | "not_enough_information"
  | "insufficient_evidence"
  | "unknown";

export const verdictConfig: Record<
  Verdict,
  { label: string; description: string }
> = {
  supported: {
    label: "Supported",
    description: "Evidence supports this claim.",
  },
  refuted: {
    label: "Refuted",
    description: "Evidence contradicts this claim.",
  },
  conflicting_evidence: {
    label: "Conflicting Evidence",
    description: "Evidence contains conflicting information.",
  },
  not_enough_information: {
    label: "Not Enough Information",
    description: "Available evidence is insufficient to determine this claim.",
  },
  insufficient_evidence: {
    label: "Insufficient Evidence",
    description: "There is not enough evidence to verify this claim.",
  },
  unknown: {
    label: "Unknown",
    description: "The verdict could not be recognized.",
  },
};

export function normalizeVerdict(value: unknown): Verdict {
  if (typeof value !== "string") return "unknown";

  const normalized = value.trim().toLowerCase();

  if (normalized in verdictConfig) {
    return normalized as Verdict;
  }

  return "unknown";
}