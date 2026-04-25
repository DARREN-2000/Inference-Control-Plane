export type GenerateRequest = {
  prompt: string;
  user_id: string;
  priority: "low" | "high";
  model_override?: string;
};

export type GenerateResponse = {
  request_id: string;
  model_used: string;
  response: string;
  cached: boolean;
  latency_ms: number;
  tokens: number;
  cost: number;
  timestamp: string;
};

type ErrorResponse = {
  error?: {
    code?: string;
    message?: string;
    request_id?: string;
  };
};

const BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export async function generateInference(
  payload: GenerateRequest,
  apiKey: string,
): Promise<GenerateResponse> {
  const response = await fetch(`${BASE_URL}/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": apiKey,
    },
    body: JSON.stringify(payload),
    cache: "no-store",
  });

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    try {
      const body = (await response.json()) as ErrorResponse;
      if (body.error?.message) {
        message = body.error.message;
      }
    } catch {
      // Ignore JSON parsing failures and keep the generic message.
    }

    throw new Error(message);
  }

  return (await response.json()) as GenerateResponse;
}
