import { useState } from "react";
import { CodeBlock } from "@/components/ui/CodeBlock";

export const ApiSection = () => {
  const [lang, setLang] = useState<"curl" | "node" | "python">("curl");

  const snippets = {
    curl: `curl -X POST https://api.inference-control-plane.ai/v1/chat/completions \\
  -H "Authorization: Bearer tg_live_xxxxxx" \\
  -H "Content-Type: application/json" \\
  -H "X-Inference-Control-Plane-Route-To: cheapest" \\
  -H "X-Inference-Control-Plane-Cache: true" \\
  -d '{
    "model": "gpt-4-turbo",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'`,
    node: `import OpenAI from 'openai';

const client = new OpenAI({
  baseURL: 'https://api.inference-control-plane.ai/v1',
  apiKey: 'tg_live_xxxxxx'
});

const response = await client.chat.completions.create({
  model: 'gpt-4-turbo',
  messages: [{ role: 'user', content: 'Hello!' }],
}, {
  headers: {
    'X-Inference-Control-Plane-Route-To': 'cheapest',
    'X-Inference-Control-Plane-Cache': 'true'
  }
});`,
    python: `import openai

client = openai.Client(
    base_url="https://api.inference-control-plane.ai/v1",
    api_key="tg_live_xxxxxx"
)

response = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[{"role": "user", "content": "Hello!"}],
    extra_headers={
        "X-Inference-Control-Plane-Route-To": "cheapest",
        "X-Inference-Control-Plane-Cache": "true"
    }
)`
  };

  return (
    <section className="py-24 bg-zinc-950 border-t border-white/5">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col lg:flex-row gap-12 items-center">

          <div className="lg:w-1/3">
            <h2 className="text-3xl font-bold tracking-tight mb-4">
              Integrate in seconds.
            </h2>
            <p className="text-zinc-400 mb-8">
              Because Inference Control Plane speaks standard OpenAI API protocols, you can use your favorite HTTP clients and libraries.
            </p>

            <div className="flex flex-col gap-2">
              {(["curl", "node", "python"] as const).map((l) => (
                <button
                  key={l}
                  onClick={() => setLang(l)}
                  className={`px-4 py-3 text-sm text-left rounded-lg transition-colors border ${
                    lang === l
                      ? "bg-white/10 text-white border-white/20 font-medium"
                      : "bg-transparent text-zinc-500 border-transparent hover:text-zinc-300 hover:bg-white/5"
                  }`}
                >
                  {l === "curl" ? "cURL" : l === "node" ? "Node.js" : "Python"}
                </button>
              ))}
            </div>
          </div>

          <div className="lg:w-2/3 w-full">
            <div className="p-1 rounded-xl bg-linear-to-br from-white/10 to-transparent">
              <CodeBlock
                language={lang === "curl" ? "bash" : lang === "node" ? "javascript" : "python"}
                code={snippets[lang]}
                className="bg-black text-sm"
              />
            </div>
          </div>

        </div>
      </div>
    </section>
  );
};
