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

## Design Comparison Module (`components/design_comparison.py`)
- **compare_multiple_designs(designs_data, faiss_index, metadata, platform)**: Calls the vision model with multiple images + RAG context to rank 2–5 designs, returning overall ranking, relative scores (visual/ux/market/brand/conversion), key differences, strengths/weaknesses, synthesis recommendations, and an A/B test plan. Expects `designs_data` entries with `name`, `image_base64`, and `embedding`.
- **generate_side_by_side_comparison_image(designs_data, comparison_result)**: Builds a labeled side-by-side image showing each design with its rank and score.
- **generate_similarity_matrix(designs_data)**: Computes CLIP cosine similarity across designs and reports the most similar/different pairs plus average similarity.
- Uses the current `VISION_MODEL` (default `openai/gpt-4o`) and UI-selected `top_k` for RAG context.

### Comparison Flow (UI)
1) Select **Compare Designs (2–5)** in the sidebar and upload 2–5 images.
2) Click **Compare Designs**; the app runs `compare_multiple_designs`, renders ranking, scores table, bar chart, and the side-by-side comparison image (downloadable).
3) Similarity matrix and A/B test recommendations come from the model output; all use the current `VISION_MODEL` and `top_k` RAG setting.

## Agent Workflow & Selection
- Agents: Visual, UX, Market, Conversion/CTA, Brand (all toggleable via sidebar multiselect).
- Each agent: vision + RAG prompt (respects `creative_type`, `platform`, `top_k`), retries on API/parse failures, returns structured JSON scores/recs.
- Skipping: Disabled agents are marked `skipped_by_user`; their charts are hidden.
- Errors: Per-agent errors surface in the UI expander; also captured in `final_report.agent_errors`.

## Visual Feedback Module (`components/visual_feedback.py`)
- Annotated designs highlighting issues (overlay markers + text), with download.
- Before/after mockups (simulated improvements) and downloads.
- Heatmaps (attention/problem) and color palette swatches.
- Driven by aggregated recommendations; works for any enabled agents.

## RAG & Embeddings
- **components/rag_system.py**: OpenRouter text embeddings + FAISS index over `data/design_patterns.json`; `retrieve_relevant_patterns` filters by platform and `top_k`; `augment_prompt_with_rag` injects retrieved patterns into prompts.
- **components/image_processing.py**: PIL preprocess (RGB, max 1024px), base64 conversion, CLIP embeddings, and metadata extraction.

## Module Guide

- **app.py**: Streamlit UI (single vs compare), agent toggles, RAG `top_k` slider, creative type selector, upload handling, workflow execution, results dashboard with charts, per-agent highlights, error surfacing, and downloads.
- **components/agents.py**: Calls OpenRouter vision model with RAG prompts for Visual, UX, Market, Conversion/CTA, and Brand agents; configurable `top_k` (from UI); retries on API/parse errors; uses shared `call_openrouter_vision`.
  - `call_openrouter_vision(image_base64, prompt, temperature=0.7, max_tokens=2000, retries=2, backoff=1.5)`: Vision API wrapper with retry/backoff and JSON parsing safeguards.
  - `visual_analysis_agent(...)`: Color/layout/typography scoring.
  - `ux_critique_agent(...)`: Usability, accessibility, interaction patterns.
  - `market_research_agent(...)`: Platform optimization, trends, audience fit, engagement.
  - `conversion_optimization_agent(...)`: CTA visibility, copy strength, funnel fit.
  - `brand_consistency_agent(...)`: Logo use, palette, typography, tone, component style.
- **components/orchestration.py**: LangGraph workflow/state schema, agent sequencing (with skip logic based on UI selection), aggregation into final report, score blending, and recommendation collation; captures per-agent errors.
- **components/image_processing.py**: PIL image preprocessing (RGB, max 1024px), base64 conversion, CLIP embedding generation, and metadata extraction.
- **components/rag_system.py**: FAISS index load/build from `data/design_patterns.json`, OpenRouter text embeddings, prompt augmentation with retrieved design patterns.
- **components/enhanced_output.py**: Plotly visualizations (gauges, radar, priority matrix, timelines, impact projections, accessibility chart) and recommendation shaping helpers.
- **components/visual_feedback.py**: Annotated design overlays, before/after mockups, heatmaps, and color palette visuals.
- **components/design_comparison.py**: Vision + RAG comparison for 2–5 designs; ranking, relative scores, differences, strengths/weaknesses, synthesis recs, A/B plan; side-by-side composite and similarity matrix helpers.

## Architecture & Flow
- **Inputs**: Uploaded image(s) → preprocess (RGB, resize) → base64 + CLIP embeddings + metadata.
- **RAG**: Query FAISS (design patterns) with adjustable `top_k`; inject patterns into each agent prompt.
- **Agents**: Visual, UX, Market, Conversion, Brand (toggleable). Each calls the vision model with retries and returns structured JSON.
- **Orchestration**: LangGraph executes enabled agents in sequence, aggregates scores/recs, captures per-agent errors, and produces `final_report`.
- **UI**: Streams progress, renders charts/visuals, shows per-agent highlights, and surfaces errors. Comparison mode uses the comparison module for 2–5 designs.

## Error Handling & Controls
- Agent calls retry on API/parse failures; invalid or empty responses are surfaced in the UI (per-agent error expander).
- Agents can be skipped via sidebar toggles; skipped agents are marked `skipped_by_user` and omitted from charts.
- RAG depth (`top_k`) is user-controlled; smaller values speed up calls.
- Model and base URL are configurable via `.env`.

## Visual Outputs
- Performance gauges (only for enabled agents), radar chart, category breakdown.
- Recommendations tab with overall list plus per-agent highlight expanders.
- Impact: Priority matrix, timeline, projections (driven by recommendations).
- Visual feedback: Annotated image and before/after mockups; color palette and heatmaps.
- Comparison: Rankings, tables/charts, side-by-side image, similarity matrix.
