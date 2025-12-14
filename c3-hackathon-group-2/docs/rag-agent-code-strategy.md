
Make it optional and opt-in. Emphasize privacy (data encrypted, local/ephemeral parsing if possible).

Allow users to mask account numbers before upload.

Show clear benefit for uploading (fewer prompts, automated tracking) so users see trade-off.

Store parsed transactions only if user explicitly allows — otherwise keep ephemeral and show result without persisting raw data.

8 — Scaling RAG/Agent complexity sensibly (engineering guidance)

Start with small retriever corpus (your playbooks, help docs, a few trusted external docs) so RAG returns high-quality, auditable sources.

Keep agent tools minimal: a single sandboxed Python runner (for backtests) and a parser tool (for statement CSV/PDF) for next-phase. Don’t let the LLM call arbitrary web APIs at first; control what it can access.

Record provenance for every recommendation: which docs were retrieved, retrieval scores, model version — this keeps legal risk low.

9 — Minimal tech map for this product (MVP)

Frontend: Streamlit (Python) or Google AI Studio app (lightweight, zero-cost hosting)

Backend: Python FastAPI or Streamlit server functions with deterministic rules engine + task workers

DB: SQLite for dev → Postgres (Supabase free tier) for persistence; local/Supabase storage for uploads

VectorDB (small): Chroma/FAISS (embedded, runs locally)

LLMs: Gemini via Google AI Studio free tier; fallback to small open models running locally

Agent orchestration: Lightweight Python tasks/LangGraph (open-source) — only enable specific tools
