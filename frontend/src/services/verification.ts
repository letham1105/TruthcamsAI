import api from "./api";

export type VerificationStatus =
  | "processing"
  | "success"
  | "partial"
  | "failed";

export interface VerificationSession {
  id: number;
  user_id: number | null;
  input_type: string;
  original_input: string;
  status: VerificationStatus;
  result: Record<string, unknown> | null;
  error: string | null;
  created_at: string;
  updated_at: string;
}

export interface VerificationHistoryItem {
  id: number;
  input_type: string;
  original_input: string;
  status: VerificationStatus;
  created_at: string;
}

export interface VerificationHistoryResponse {
  items: VerificationHistoryItem[];
  total: number;
  limit: number;
  offset: number;
}

export interface DeleteVerificationResponse {
  message: string;
}

export async function analyzeText(text: string) {
  const response = await api.post<VerificationSession>(
    "/verification/analyze",
    { text },
  );

  return response.data;
}

export async function getVerification(sessionId: number) {
  const response = await api.get<VerificationSession>(
    `/verification/${sessionId}`,
  );

  return response.data;
}

export async function getVerificationHistory(
  limit = 20,
  offset = 0,
) {
  const response = await api.get<VerificationHistoryResponse>(
    "/verification/history",
    {
      params: { limit, offset },
    },
  );

  return response.data;
}

export async function deleteVerification(sessionId: number) {
  const response = await api.delete<DeleteVerificationResponse>(
    `/verification/${sessionId}`,
  );

  return response.data;
}
export interface OCRResponse {
  filename: string | null;
  text: string;
  character_count: number;
  status: "success" | "empty";
}

export async function extractImageText(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post<OCRResponse>(
    "/verification/ocr",
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    },
  );

  return response.data;
}