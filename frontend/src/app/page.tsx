"use client";

import { FormEvent, useMemo, useState } from "react";

import {
  fetchUsageLogs,
  generateInference,
  GenerateResponse,
  isDemoMode,
  UsageLogEntry,
} from "@/lib/api";

const metrics = [
  { label: "P95 Latency", value: "218ms", delta: "-11%" },
  { label: "Cache Hit Ratio", value: "67.4%", delta: "+9%" },
  { label: "Requests (24h)", value: "1.4M", delta: "+23%" },
  { label: "Cost / 1K req", value: "$4.82", delta: "-6%" },
];

const activity = [
  "API key rotation policy enabled",
  "Rate limiting bumped for tenant enterprise-a",
  "Fallback route triggered 12 times in the last hour",
  "Prometheus scrape health is stable",
];

export default function Home() {
  const [apiKey, setApiKey] = useState("dev-inference-key");
  const [prompt, setPrompt] = useState("Summarize our top latency drivers this week.");
  const [userId, setUserId] = useState("product-analyst-1");
  const [priority, setPriority] = useState<"low" | "high">("low");
  const [isLoading, setIsLoading] = useState(false);
  const [isLogsLoading, setIsLogsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<GenerateResponse | null>(null);
  const [logsError, setLogsError] = useState<string | null>(null);
  const [recentLogs, setRecentLogs] = useState<UsageLogEntry[]>([]);

  const derivedModel = useMemo(() => {
    return priority === "high" ? "premium-model" : "smart-router";
  }, [priority]);

  async function loadRecentLogs() {
    setLogsError(null);
    setIsLogsLoading(true);

    try {
      const response = await fetchUsageLogs(userId, apiKey, 8);
      setRecentLogs(response.entries);
    } catch (loadError) {
      const message =
        loadError instanceof Error ? loadError.message : "Failed to load request logs.";
      setLogsError(message);
    } finally {
      setIsLogsLoading(false);
    }
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const response = await generateInference(
        {
          prompt,
          user_id: userId,
          priority,
        },
        apiKey,
      );
      setResult(response);
      await loadRecentLogs();
    } catch (submitError) {
      const message =
        submitError instanceof Error
          ? submitError.message
          : "Request failed unexpectedly.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="cp-shell">
      <header className="cp-card cp-card-strong mb-4 p-5 md:p-7 cp-animate cp-animate-delay-1">
        <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="cp-label text-[var(--accent-strong)]">Inference Platform</p>
            <h1 className="text-3xl font-bold tracking-tight md:text-4xl">
              Control Plane Dashboard
            </h1>
            <p className="mt-2 max-w-2xl text-sm/6 text-neutral-700 md:text-base/7">
              Production operator view for routing, usage, cache efficiency, and rapid
              prompt validation.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <span className="cp-pill">
              <span className="cp-dot bg-emerald-500" /> API healthy
            </span>
            <span className="cp-pill">
              <span className="cp-dot bg-cyan-600" /> Redis online
            </span>
            {isDemoMode && (
              <span className="cp-pill">
                <span className="cp-dot bg-fuchsia-500" /> Demo mode
              </span>
            )}
            <span className="cp-pill">
              <span className="cp-dot bg-amber-500" /> Routing: {derivedModel}
            </span>
          </div>
        </div>
      </header>

      <section className="cp-grid mb-4 grid-cols-1 md:grid-cols-2 xl:grid-cols-4">
        {metrics.map((metric, index) => {
          const delayClass = `cp-animate-delay-${index + 2}`;
          return (
            <article
              key={metric.label}
              className={`cp-card p-4 cp-animate ${delayClass}`}
            >
            <p className="cp-label text-neutral-600">{metric.label}</p>
            <p className="mt-1 text-2xl font-bold">{metric.value}</p>
            <p className="mt-1 text-sm text-emerald-700">{metric.delta} vs baseline</p>
            </article>
          );
        })}
      </section>

      <section className="cp-grid grid-cols-1 xl:grid-cols-[1.4fr_1fr]">
        <article className="cp-card p-5 md:p-6 cp-animate cp-animate-delay-2">
          <div className="mb-4 flex items-end justify-between">
            <div>
              <p className="cp-label text-neutral-600">Live Playground</p>
              <h2 className="text-xl font-semibold">Generate With Backend API</h2>
            </div>
            <p className="cp-label text-neutral-500">POST /api/v1/generate</p>
          </div>

          <form className="space-y-3" onSubmit={onSubmit}>
            <div className="grid gap-3 md:grid-cols-2">
              <div className="space-y-1">
                <label htmlFor="userId" className="cp-label block text-neutral-600">
                  User ID <span className="text-red-500" aria-hidden="true">*</span>
                </label>
                <input
                  id="userId"
                  className="cp-input"
                  value={userId}
                  onChange={(event) => setUserId(event.target.value)}
                  required
                />
              </div>
              <div className="space-y-1">
                <label htmlFor="apiKey" className="cp-label block text-neutral-600">
                  API Key <span className="text-red-500" aria-hidden="true">*</span>
                </label>
                <input
                  id="apiKey"
                  className="cp-input"
                  value={apiKey}
                  onChange={(event) => setApiKey(event.target.value)}
                  required
                />
              </div>
            </div>

            <div className="space-y-1">
              <label htmlFor="prompt" className="cp-label block text-neutral-600">
                Prompt <span className="text-red-500" aria-hidden="true">*</span>
              </label>
              <textarea
                id="prompt"
                className="cp-input min-h-32"
                value={prompt}
                onChange={(event) => setPrompt(event.target.value)}
                required
              />
            </div>

            <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <div className="space-y-1">
                <label htmlFor="priority" className="cp-label block text-neutral-600">Priority</label>
                <select
                  id="priority"
                  className="cp-input"
                  value={priority}
                  onChange={(event) => setPriority(event.target.value as "low" | "high")}
                >
                  <option value="low">Low</option>
                  <option value="high">High</option>
                </select>
              </div>

              <button
                className="cp-button md:min-w-56"
                disabled={isLoading}
                aria-busy={isLoading}
                aria-label={isLoading ? "Generating..." : "Run Inference"}
                type="submit"
              >
                {isLoading && (
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                )}
                {isLoading ? "Generating..." : "Run Inference"}
              </button>
            </div>
          </form>

          {isDemoMode && (
            <p className="mt-3 text-xs text-neutral-600">
              Demo mode is enabled. Responses and logs are simulated for preview.
            </p>
          )}

          {error && (
            <p className="mt-4 rounded-xl border border-red-300 bg-red-50 px-3 py-2 text-sm text-[var(--danger)]">
              {error}
            </p>
          )}

          {result && (
            <div className="mt-5 space-y-3 rounded-2xl border border-[var(--border)] bg-[#fffdf8] p-4">
              <div className="flex flex-wrap gap-x-5 gap-y-2 text-sm">
                <span>
                  <strong>Model:</strong> {result.model_used}
                </span>
                <span>
                  <strong>Latency:</strong> {result.latency_ms.toFixed(1)} ms
                </span>
                <span>
                  <strong>Tokens:</strong> {result.tokens}
                </span>
                <span>
                  <strong>Cost:</strong> ${result.cost.toFixed(4)}
                </span>
                <span>
                  <strong>Cache:</strong> {result.cached ? "hit" : "miss"}
                </span>
              </div>
              <p className="whitespace-pre-wrap text-sm leading-7 text-neutral-800">
                {result.response}
              </p>
            </div>
          )}
        </article>

        <div className="cp-grid grid-cols-1 gap-4">
          <article className="cp-card p-5 cp-animate cp-animate-delay-3">
            <p className="cp-label text-neutral-600">Usage Trend</p>
            <h3 className="text-lg font-semibold">24h Request Volume</h3>
            <div className="cp-chart mt-3" />
          </article>

          <article className="cp-card p-5 cp-animate cp-animate-delay-4">
            <p className="cp-label text-neutral-600">Operational Activity</p>
            <ul className="mt-3 space-y-2 text-sm text-neutral-700">
              {activity.map((item) => (
                <li key={item} className="rounded-lg border border-[var(--border)] bg-[#fffdf8] p-2">
                  {item}
                </li>
              ))}
            </ul>
          </article>

          <article className="cp-card p-5 cp-animate cp-animate-delay-5">
            <div className="flex items-center justify-between gap-2">
              <div>
                <p className="cp-label text-neutral-600">Request Logs</p>
                <h3 className="text-lg font-semibold">Recent Requests</h3>
              </div>
              <button
                className="cp-button px-3 py-2 text-sm"
                disabled={isLogsLoading}
                aria-busy={isLogsLoading}
                aria-label={isLogsLoading ? "Loading logs..." : "Refresh request logs"}
                onClick={loadRecentLogs}
                type="button"
              >
                {isLogsLoading && (
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                )}
                {isLogsLoading ? "Loading..." : "Refresh"}
              </button>
            </div>

            {logsError && (
              <p className="mt-3 rounded-xl border border-red-300 bg-red-50 px-3 py-2 text-sm text-[var(--danger)]">
                {logsError}
              </p>
            )}

            <div className="mt-3 space-y-2 text-sm">
              {recentLogs.length === 0 && !isLogsLoading && (
                <p className="rounded-lg border border-[var(--border)] bg-[#fffdf8] p-3 text-neutral-600">
                  No request logs yet for this user.
                </p>
              )}

              {recentLogs.map((entry) => (
                <div
                  key={entry.request_id}
                  className="rounded-lg border border-[var(--border)] bg-[#fffdf8] p-3"
                >
                  <div className="flex flex-wrap gap-x-3 gap-y-1 text-xs text-neutral-600">
                    <span>{entry.model_used}</span>
                    <span>{entry.latency_ms.toFixed(1)} ms</span>
                    <span>{entry.tokens} tokens</span>
                    <span>${entry.cost.toFixed(4)}</span>
                    <span>{entry.cache_hit ? "cache hit" : "cache miss"}</span>
                    <span>{new Date(entry.created_at).toLocaleString()}</span>
                  </div>
                  <p className="mt-1 text-xs text-neutral-500">Status: {entry.status}</p>
                  {entry.error_message && (
                    <p className="mt-1 text-xs text-[var(--danger)]">{entry.error_message}</p>
                  )}
                </div>
              ))}
            </div>
          </article>
        </div>
      </section>
    </main>
  );
}
