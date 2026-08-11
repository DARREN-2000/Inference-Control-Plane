"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

import {
  fetchUsageLogs,
  generateInference,
  GenerateResponse,
  isDemoMode,
  UsageLogEntry,
  DashboardMetric,
  fetchDashboardMetrics,
  fetchDashboardActivity,
} from "@/lib/api";

export default function Home() {
  const [apiKey, setApiKey] = useState("dev-inference-key");
  const [prompt, setPrompt] = useState(
    "Summarize our top latency drivers this week.",
  );
  const [userId, setUserId] = useState("product-analyst-1");
  const [priority, setPriority] = useState<"low" | "high">("low");
  const [isLoading, setIsLoading] = useState(false);
  const [isLogsLoading, setIsLogsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<GenerateResponse | null>(null);
  const [logsError, setLogsError] = useState<string | null>(null);
  const [recentLogs, setRecentLogs] = useState<UsageLogEntry[]>([]);
  const [metrics, setMetrics] = useState<DashboardMetric[]>([]);
  const [activity, setActivity] = useState<string[]>([]);

  useEffect(() => {
    fetchDashboardMetrics(apiKey)
      .then((res) => setMetrics(res.metrics))
      .catch(console.error);
    fetchDashboardActivity(apiKey)
      .then((res) => setActivity(res.activity))
      .catch(console.error);
  }, [apiKey]);

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
        loadError instanceof Error
          ? loadError.message
          : "Failed to load request logs.";
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
      <header className="cp-card cp-card-strong mb-6 p-6 md:p-8 cp-animate cp-animate-delay-1">
        <div className="flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="cp-label mb-2 text-zinc-400">
              Inference Platform
            </p>
            <h1 className="text-3xl font-semibold tracking-tight text-zinc-50 md:text-4xl">
              Control Plane Dashboard
            </h1>
            <p className="mt-3 max-w-2xl text-sm/6 text-zinc-400 md:text-base/7">
              Production operator view for routing, usage, cache efficiency, and
              rapid prompt validation.
            </p>
            <a
              href={
                process.env.NEXT_PUBLIC_DEMO_MODE === "true"
                  ? "/Inference-Control-Plane/"
                  : "/"
              }
              className="mt-5 inline-block text-sm font-medium text-zinc-300 hover:text-white transition-colors"
            >
              &larr; Back to Website
            </a>
          </div>
          <div className="flex flex-wrap gap-3">
            <span className="cp-pill">
              <span className="cp-dot bg-emerald-500" /> API healthy
            </span>
            <span className="cp-pill">
              <span className="cp-dot bg-sky-500" /> Redis online
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

      <section className="cp-grid mb-6 grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        {metrics.map((metric, index) => {
          const delayClass = `cp-animate-delay-${index + 2}`;
          return (
            <article
              key={metric.label}
              className={`cp-card p-5 cp-animate ${delayClass}`}
            >
              <p className="cp-label">{metric.label}</p>
              <p className="mt-2 text-3xl font-semibold text-zinc-50">{metric.value}</p>
              <p className="mt-2 text-xs font-medium text-emerald-500 bg-emerald-500/10 inline-block px-2 py-1 rounded-md">
                {metric.delta} vs baseline
              </p>
            </article>
          );
        })}
      </section>

      <section className="cp-grid grid-cols-1 xl:grid-cols-[1.5fr_1fr] gap-6">
        <article className="cp-card p-6 md:p-8 cp-animate cp-animate-delay-2">
          <div className="mb-6 flex items-end justify-between border-b border-zinc-800 pb-4">
            <div>
              <p className="cp-label mb-1">Live Playground</p>
              <h2 className="text-xl font-medium text-zinc-100">
                Generate With Backend API
              </h2>
            </div>
            <p className="cp-label">POST /api/v1/generate</p>
          </div>

          <form onSubmit={onSubmit}>
            <fieldset disabled={isLoading} className="space-y-5">
              <div className="grid gap-5 md:grid-cols-2">
                <div className="space-y-2">
                  <label
                    htmlFor="userId"
                    className="cp-label block"
                  >
                    User ID{" "}
                    <span className="text-red-500" aria-hidden="true">
                      *
                    </span>
                  </label>
                  <input
                    id="userId"
                    className="cp-input"
                    value={userId}
                    onChange={(event) => setUserId(event.target.value)}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <label
                    htmlFor="apiKey"
                    className="cp-label block"
                  >
                    API Key{" "}
                    <span className="text-red-500" aria-hidden="true">
                      *
                    </span>
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

              <div className="space-y-2">
                <label
                  htmlFor="prompt"
                  className="cp-label flex items-center"
                >
                  Prompt{" "}
                  <span className="text-red-500 ml-1" aria-hidden="true">
                    *
                  </span>
                  <span className="ml-auto text-xs font-normal normal-case tracking-normal text-zinc-500">
                    Cmd/Ctrl + Enter to run
                  </span>
                </label>
                <textarea
                  id="prompt"
                  className="cp-input min-h-36 resize-y"
                  value={prompt}
                  onChange={(event) => setPrompt(event.target.value)}
                  onKeyDown={(event) => {
                    if (
                      (event.metaKey || event.ctrlKey) &&
                      event.key === "Enter"
                    ) {
                      event.preventDefault();
                      if (!isLoading) {
                        event.currentTarget.form?.requestSubmit();
                      }
                    }
                  }}
                  required
                />
              </div>

              <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between pt-2">
                <div className="space-y-2 md:w-1/3">
                  <label
                    htmlFor="priority"
                    className="cp-label block"
                  >
                    Priority
                  </label>
                  <select
                    id="priority"
                    className="cp-input"
                    value={priority}
                    onChange={(event) =>
                      setPriority(event.target.value as "low" | "high")
                    }
                  >
                    <option value="low">Low Priority</option>
                    <option value="high">High Priority</option>
                  </select>
                </div>

                <button
                  className="cp-button md:min-w-48"
                  aria-busy={isLoading}
                  type="submit"
                >
                  {isLoading && (
                    <svg
                      aria-hidden="true"
                      className="animate-spin -ml-1 mr-2 h-4 w-4 text-zinc-900"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      ></circle>
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                  )}
                  {isLoading ? "Generating..." : "Run Inference"}
                </button>
              </div>
            </fieldset>
          </form>

          {isDemoMode && (
            <p className="mt-4 text-xs text-zinc-500 bg-zinc-900/50 rounded-lg p-3 border border-zinc-800/50">
              <span className="font-semibold text-zinc-400">Demo Mode:</span> Responses and logs are simulated for preview.
            </p>
          )}

          {error && (
            <div
              role="alert"
              className="mt-5 rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-400"
            >
              {error}
            </div>
          )}

          {result && (
            <div
              aria-live="polite"
              className="mt-6 space-y-4 rounded-xl border border-zinc-800 bg-zinc-900/50 p-5 backdrop-blur-sm"
            >
              <div className="flex flex-wrap gap-x-6 gap-y-3 text-xs text-zinc-400 border-b border-zinc-800 pb-4">
                <span className="flex flex-col gap-1">
                  <span className="uppercase tracking-wider text-[10px] font-semibold text-zinc-500">Model</span>
                  <span className="text-zinc-200">{result.model_used}</span>
                </span>
                <span className="flex flex-col gap-1">
                  <span className="uppercase tracking-wider text-[10px] font-semibold text-zinc-500">Latency</span>
                  <span className="text-zinc-200">{result.latency_ms.toFixed(1)} ms</span>
                </span>
                <span className="flex flex-col gap-1">
                  <span className="uppercase tracking-wider text-[10px] font-semibold text-zinc-500">Tokens</span>
                  <span className="text-zinc-200">{result.tokens}</span>
                </span>
                <span className="flex flex-col gap-1">
                  <span className="uppercase tracking-wider text-[10px] font-semibold text-zinc-500">Cost</span>
                  <span className="text-zinc-200">${result.cost.toFixed(4)}</span>
                </span>
                <span className="flex flex-col gap-1">
                  <span className="uppercase tracking-wider text-[10px] font-semibold text-zinc-500">Cache</span>
                  <span className={result.cached ? "text-emerald-400" : "text-amber-400"}>
                    {result.cached ? "HIT" : "MISS"}
                  </span>
                </span>
              </div>
              <p className="whitespace-pre-wrap text-sm leading-relaxed text-zinc-300">
                {result.response}
              </p>
            </div>
          )}
        </article>

        <div className="flex flex-col gap-6">
          <article className="cp-card p-6 cp-animate cp-animate-delay-3">
            <div className="mb-4">
              <p className="cp-label mb-1">Usage Trend</p>
              <h3 className="text-lg font-medium text-zinc-100">24h Request Volume</h3>
            </div>
            <div className="cp-chart" />
          </article>

          <article className="cp-card p-6 cp-animate cp-animate-delay-4">
            <div className="mb-4">
              <p className="cp-label mb-1">Operational Activity</p>
              <h3 className="text-lg font-medium text-zinc-100">Live Events</h3>
            </div>
            <ul className="space-y-2.5 text-sm text-zinc-400">
              {activity.map((item) => (
                <li
                  key={item}
                  className="rounded-lg border border-zinc-800 bg-zinc-900/40 px-3 py-2.5 flex items-start gap-3"
                >
                  <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-zinc-600 shrink-0"></span>
                  <span className="leading-snug">{item}</span>
                </li>
              ))}
            </ul>
          </article>

          <article className="cp-card p-6 cp-animate cp-animate-delay-5 flex-1 flex flex-col">
            <div className="flex items-center justify-between gap-4 mb-4">
              <div>
                <p className="cp-label mb-1">Request Logs</p>
                <h3 className="text-lg font-medium text-zinc-100">Recent Requests</h3>
              </div>
              <button
                className="cp-button !bg-zinc-800 !text-zinc-300 hover:!bg-zinc-700 hover:!text-white px-3 py-1.5 text-xs font-medium border border-zinc-700 h-auto"
                disabled={isLogsLoading}
                aria-busy={isLogsLoading}
                onClick={loadRecentLogs}
                type="button"
              >
                {isLogsLoading && (
                  <svg
                    aria-hidden="true"
                    className="animate-spin -ml-1 mr-2 h-3 w-3"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                )}
                {isLogsLoading ? "Loading..." : "Refresh Logs"}
              </button>
            </div>

            {logsError && (
              <div
                role="alert"
                className="mb-4 rounded-xl border border-red-500/20 bg-red-500/10 px-3 py-2 text-sm text-red-400"
              >
                {logsError}
              </div>
            )}

            <div className="space-y-3 flex-1 overflow-y-auto">
              {recentLogs.length === 0 && !isLogsLoading && (
                <div className="rounded-xl border border-zinc-800 border-dashed bg-zinc-900/20 p-6 text-center text-sm text-zinc-500">
                  No request logs available.
                </div>
              )}

              {recentLogs.map((entry) => (
                <div
                  key={entry.request_id}
                  className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-4 transition-colors hover:bg-zinc-900/60"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-sm text-zinc-200">{entry.model_used}</span>
                    <span className="text-xs text-zinc-500">
                      {new Date(entry.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                    </span>
                  </div>
                  
                  <div className="flex flex-wrap gap-x-4 gap-y-1.5 text-[11px] text-zinc-400 font-mono">
                    <span className="flex items-center gap-1">
                      <span className="text-zinc-600">Lat:</span> {entry.latency_ms.toFixed(0)}ms
                    </span>
                    <span className="flex items-center gap-1">
                      <span className="text-zinc-600">Tok:</span> {entry.tokens}
                    </span>
                    <span className="flex items-center gap-1">
                      <span className="text-zinc-600">Cost:</span> ${entry.cost.toFixed(4)}
                    </span>
                    <span className={`flex items-center gap-1 ${entry.cache_hit ? 'text-emerald-500' : ''}`}>
                      <span className="text-zinc-600">Cache:</span> {entry.cache_hit ? "HIT" : "MISS"}
                    </span>
                  </div>
                  
                  <div className="mt-2.5 pt-2.5 border-t border-zinc-800/50 flex items-center justify-between text-xs">
                    <span className="text-zinc-500">
                      Status: <span className={entry.status === 'success' ? 'text-emerald-400' : 'text-zinc-300'}>{entry.status}</span>
                    </span>
                    {entry.error_message && (
                      <span className="text-red-400 font-medium truncate max-w-[150px]" title={entry.error_message}>
                        {entry.error_message}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </article>
        </div>
      </section>
    </main>
  );
}
