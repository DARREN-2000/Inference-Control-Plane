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

export type UsageLogEntry = {
  request_id: string;
  model_used: string;
  latency_ms: number;
  tokens: number;
  cost: number;
  cache_hit: boolean;
  status: string;
  created_at: string;
  error_message: string | null;
};

export type UsageLogsResponse = {
  user_id: string;
  limit: number;
  entries: UsageLogEntry[];
};

type ErrorResponse = {
  error?: {
    code?: string;
    message?: string;
    request_id?: string;
  };
};

const BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  (process.env.NEXT_PUBLIC_API_HOST
    ? `https://${process.env.NEXT_PUBLIC_API_HOST}/api/v1`
    : "http://localhost:8000/api/v1");
const DEMO_MODE = process.env.NEXT_PUBLIC_DEMO_MODE === "true";
export const isDemoMode = DEMO_MODE;
const DEMO_COSTS = {
  low: 0.0008,
  high: 0.01,
} as const;

type DemoLogEntry = UsageLogEntry & { user_id: string };
const demoLogs: DemoLogEntry[] = [];

function demoDelay(ms: number): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

function demoRequestId(): string {
  return `demo-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
}

function demoTokens(prompt: string): number {
  return Math.max(1, Math.ceil(prompt.trim().length / 4));
}

function demoCost(tokens: number, priority: "low" | "high"): number {
  const cost = (tokens / 1000) * DEMO_COSTS[priority];
  return Number(cost.toFixed(4));
}

function demoSummary(prompt: string): string {
  const cleaned = prompt.trim().replace(/\s+/g, " ");
  return cleaned.length > 160 ? `${cleaned.slice(0, 160)}...` : cleaned;
}

function seedDemoLogs(userId: string): void {
  if (demoLogs.length > 0) {
    return;
  }

  const now = Date.now();
  const samplePrompts = [
    "Summarize cache hit trends for the last 24 hours.",
    "Explain top model latency drivers.",
    "Generate a weekly usage summary for enterprise tenants.",
  ];

  samplePrompts.forEach((prompt, index) => {
    const priority = index % 2 === 0 ? "low" : "high";
    const tokens = demoTokens(prompt);
    const modelUsed = priority === "high" ? "premium-model" : "cheap-model";
    const createdAt = new Date(now - index * 900_000).toISOString();
    demoLogs.push({
      user_id: userId,
      request_id: demoRequestId(),
      model_used: modelUsed,
      latency_ms: 180 + index * 40,
      tokens,
      cost: demoCost(tokens, priority),
      cache_hit: index % 3 === 0,
      status: "success",
      created_at: createdAt,
      error_message: null,
    });
  });
}

export async function generateInference(
  payload: GenerateRequest,
  apiKey: string,
): Promise<GenerateResponse> {
  if (DEMO_MODE) {
    const latency = 160 + Math.round(Math.random() * 320);
    const tokens = demoTokens(payload.prompt);
    const modelUsed =
      payload.priority === "high" ? "premium-model" : "cheap-model";
    const cached = Math.random() > 0.55;
    const response: GenerateResponse = {
      request_id: demoRequestId(),
      model_used: modelUsed,
      response: `Demo response: ${demoSummary(payload.prompt)}`,
      cached,
      latency_ms: latency,
      tokens,
      cost: demoCost(tokens, payload.priority),
      timestamp: new Date().toISOString(),
    };

    demoLogs.unshift({
      user_id: payload.user_id,
      request_id: response.request_id,
      model_used: response.model_used,
      latency_ms: response.latency_ms,
      tokens: response.tokens,
      cost: response.cost,
      cache_hit: response.cached,
      status: "success",
      created_at: response.timestamp,
      error_message: null,
    });
    demoLogs.splice(25);

    await demoDelay(latency);
    return response;
  }

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

export async function fetchUsageLogs(
  userId: string,
  apiKey: string,
  limit = 8,
): Promise<UsageLogsResponse> {
  if (DEMO_MODE) {
    seedDemoLogs(userId);
    const entries = demoLogs
      .filter((entry) => entry.user_id === userId)
      .slice(0, limit)
      .map((entry) => {
        const { user_id: ignoredUserId, ...rest } = entry;
        void ignoredUserId;
        return rest;
      });
    return {
      user_id: userId,
      limit,
      entries,
    };
  }

  const query = new URLSearchParams({
    user_id: userId,
    limit: String(limit),
  });

  const response = await fetch(`${BASE_URL}/usage/logs?${query.toString()}`, {
    method: "GET",
    headers: {
      "x-api-key": apiKey,
    },
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

  return (await response.json()) as UsageLogsResponse;
}

export type DashboardMetric = {
  label: string;
  value: string;
  delta: string;
};

export type DashboardMetricsResponse = {
  metrics: DashboardMetric[];
};

export type DashboardActivityResponse = {
  activity: string[];
};

export async function fetchDashboardMetrics(
  apiKey: string,
): Promise<DashboardMetricsResponse> {
  if (DEMO_MODE) {
    return {
      metrics: [
        { label: "P95 Latency", value: "218ms", delta: "-11%" },
        { label: "Cache Hit Ratio", value: "67.4%", delta: "+9%" },
        { label: "Requests (24h)", value: "1.4M", delta: "+23%" },
        { label: "Cost / 1K req", value: "$4.82", delta: "-6%" },
      ],
    };
  }

  const response = await fetch(`${BASE_URL}/dashboard/metrics`, {
    method: "GET",
    headers: {
      "x-api-key": apiKey,
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return (await response.json()) as DashboardMetricsResponse;
}

export async function fetchDashboardActivity(
  apiKey: string,
): Promise<DashboardActivityResponse> {
  if (DEMO_MODE) {
    return {
      activity: [
        "API key rotation policy enabled",
        "Rate limiting bumped for tenant enterprise-a",
        "Fallback route triggered 12 times in the last hour",
        "Prometheus scrape health is stable",
      ],
    };
  }

  const response = await fetch(`${BASE_URL}/dashboard/activity`, {
    method: "GET",
    headers: {
      "x-api-key": apiKey,
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return (await response.json()) as DashboardActivityResponse;
}
