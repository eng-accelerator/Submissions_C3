# Multimodal AI Design Analysis Suite

AI-powered Streamlit app that analyzes uploaded marketing creatives or product/app screens using multiple agents, RAG, and vision models. Supports single-design analysis and multi-design comparison, with rich visuals and downloadable reports.

## Features
- **Multi-agent analysis**: Visual, UX, Market, Conversion/CTA, and Brand agents (toggleable).
- **Vision + RAG**: Uses OpenRouter vision models with FAISS design-pattern retrieval; `top_k` slider to control context size.
- **Modes**: Single design analysis, or compare 2–5 designs with ranking, scores, and side-by-side image output.
- **Controls**: Creative type (Marketing vs Product UI), agent selectors, and adjustable RAG depth.
- **Visual outputs**: Gauges, radar, priority matrix, timelines, impact projections, annotated designs, before/after mockups.
- **Robustness**: Agent retries, error surfacing per agent, downloadable JSON report.

## Quickstart
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Configuration
Set these in `.env`:
- `OPENROUTER_API_KEY` (required)
- `VISION_MODEL` (default `openai/gpt-4o`)
- `OPENROUTER_BASE_URL` (default `https://openrouter.ai/api/v1`)
- `SITE_URL`, `APP_NAME` (optional metadata)

## Usage
1) Choose **Analysis Mode** (Single or Compare 2–5) in the sidebar.
2) Upload image(s); pick **Platform** and **Creative Type**.
3) Adjust **RAG top_k** and select/deselect agents as needed.
4) Click **Analyze** (or **Compare Designs**) to run the workflow.
5) View results: Performance scores, radar, recommendations (overall + per-agent highlights), impact charts, visual feedback, and detailed data tabs. Download the JSON report if needed.

## Notes
- Images are downscaled to max 1024px for efficiency.
- Each agent retries API calls and surfaces errors in the UI if a response is empty or invalid.
- Comparison mode uses the same vision model and RAG patterns across multiple uploaded designs.
