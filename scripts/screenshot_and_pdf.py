import asyncio

from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("http://localhost:3000")
        await page.wait_for_timeout(2000)
        await page.screenshot(path="dashboard.png", full_page=True)

        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #333; }}
                h2 {{ color: #555; margin-top: 30px; }}
                p {{ line-height: 1.6; color: #666; }}
                img {{ max-width: 100%; height: auto; border: 1px solid #ddd; margin-top: 20px; }}
                .project {{ margin-bottom: 40px; }}
            </style>
        </head>
        <body>
            <h1>Portfolio / Projects Overview</h1>

            <div class="project">
                <h2>GovernOS, Agentic AI Planning & Orchestration System</h2>
                <p>Compiled natural-language goals into policy-gated DAG workflows across a multi-tenant agentic OS with schema validation, human approval gates, audit tracing, scoped runtime memory, and real-time replanning.</p>
            </div>

            <div class="project">
                <h2>Inference Control Plane, LLM Infrastructure & Routing System</h2>
                <p>Developed a production-grade FastAPI gateway for LLM traffic control with priority-based routing, fallback routing, token optimization, Redis semantic caching, per-key rate limiting, and PostgreSQL audit logging.</p>
                <h3>Dashboard Screenshot</h3>
                <img src="file://{__import__("os").path.abspath("dashboard.png")}" alt="Dashboard Screenshot" />
            </div>

            <div class="project">
                <h2>GuardrailX, Enterprise AI Governance Platform</h2>
                <p>Enforced runtime LLM governance across enterprise systems through prompt injection detection, jailbreak detection, PII redaction, content safety filtering, hallucination controls, and risk-based policy enforcement.</p>
            </div>

            <div class="project">
                <h2>EnterpriseIQ, Enterprise Knowledge Intelligence Platform</h2>
                <p>Orchestrated LangGraph-based Agentic RAG using hybrid retrieval, cross-encoder reranking, local LLM inference, RBAC enforcement, and citation grounding across PDF, SQL, CSV, and JSON knowledge sources.</p>
            </div>

            <div class="project">
                <h2>AI Infrastructure Hypervisor, GPU-Aware Virtualization Platform</h2>
                <p>Constructed a GPU-aware AI runtime using KVM/QEMU to provision isolated vLLM workloads with automated orchestration, Prometheus/Grafana observability, and workload scheduling across inference environments.</p>
            </div>
        </body>
        </html>
        """

        with open("portfolio.html", "w") as f:
            f.write(html_content)

        await page.goto(f"file://{__import__('os').path.abspath('portfolio.html')}")
        await page.pdf(path="portfolio.pdf", format="A4", print_background=True)
        await browser.close()


asyncio.run(main())
