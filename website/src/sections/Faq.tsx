import { Accordion, AccordionItem } from "@/components/ui/Accordion";

const faqs = [
  {
    id: "1",
    q: "Do I need to change my application code?",
    a: "No. Laminar is fully compatible with OpenAI and Anthropic SDKs. You only need to change the base URL to point to your Laminar Gateway and provide your Laminar API key. Your application remains unaware of the complex routing happening behind the scenes."
  },
  {
    id: "2",
    q: "How does semantic caching work?",
    a: "We convert incoming prompts into vector embeddings using a fast, local embedding model, and store them in Redis. When a new request comes in, we calculate its embedding and perform a vector similarity search in Redis. If the similarity exceeds your configured threshold, we return the cached response in sub-milliseconds."
  },
  {
    id: "3",
    q: "What happens if my primary LLM provider goes down?",
    a: "Laminar monitors provider health in real-time. If a request times out or returns a 5xx error, Laminar automatically translates the request schema and routes it to your configured fallback provider (e.g., Anthropic Claude), returning the result to your client without dropping the connection."
  },
  {
    id: "4",
    q: "Does Laminar store my prompt data?",
    a: "By default, we log metadata (token counts, latency, cost) but do not store raw prompt text to ensure privacy. If you enable prompt logging or semantic caching, data is stored entirely within your own PostgreSQL/Redis instances."
  }
];

export const Faq = () => {
  return (
    <section className="py-24 bg-black border-t border-white/5">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="text-3xl font-bold tracking-tight mb-12 text-center">
          Frequently Asked Questions
        </h2>
        <Accordion>
          {faqs.map((faq) => (
            <AccordionItem key={faq.id} id={faq.id} title={faq.q}>
              {faq.a}
            </AccordionItem>
          ))}
        </Accordion>
      </div>
    </section>
  );
};
