import type { Verdict } from "../utils/verdict";

export interface EvidenceCounts {
  supported: number;
  refuted: number;
  not_enough_information: number;
}

export interface AggregatedClaimResult {
  claim_id: string;
  claim_text: string;
  verdict: Verdict | string;
  evidence_counts?: EvidenceCounts;
  details?: unknown[];
}

export interface VerificationApiResponse {
  status: "success" | "partial" | "failed";
  message: string;
  data: Record<string, unknown>;
}