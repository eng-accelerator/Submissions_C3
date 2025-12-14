# ai-researcher
New Features Overview
Feature         What It Does            Where to Find
RAG             Search uploaded PDFs    Sidebar → Upload PDFs
PDF Upload      Add documents           Sidebar → File uploader
Citations       Track all sources       Results → Citations section
Timeline        Agent performance       Results → Timeline expander
Visualization   Workflow diagram        Main page (before search)

Environment Variables
# Create .env file:
# Your .env file should have:
GROQ_API_KEY=gsk_your_key_here
TAVILY_API_KEY=tvly_your_key_here

Quick Usage Guide
Upload Documents (RAG)
1. Click sidebar → "Upload PDFs for RAG"
2. Select PDF files
3. Click "Process PDFs"
4. Wait for confirmation
5. Run your query - it will search both docs + web!
View Citations
1. Run any research query
2. Scroll to "Citations & Sources"
3. See citations grouped by agent
4. Click "Download Citations" for export
Check Performance
1. Run query
2. Click "Agent Execution Timeline"
3. See time per agent
4. Identify bottlenecks

Feature Comparison
Basic Version:

✅ 5 agents
✅ Web search
✅ LLM analysis
✅ Report generation

Advanced Version (ALL OF ABOVE +):

✅ 6 agents (added RAG agent)
✅ PDF upload & processing
✅ Vector database (ChromaDB)
✅ Citation tracking
✅ Performance timeline
✅ Visual workflow
✅ Multi-format export


Agent Pipeline
1. Research Planner → Creates strategy
2. RAG Search      → Searches YOUR documents 🆕
3. Web Search      → Searches internet
4. Analyzer        → Validates findings
5. Insights        → Generates recommendations
6. Reporter        → Builds final report

Export Options
Format          What It Includes                        Use Case
JSON            Complete state,all data                 Data analysis,archiving
TXT             Summary, findings, recommendations      Quickreference
Citations       All sources with URLs                   Bibliography, references

Performance Benchmarks
Metric                      Basic Version               Advanced Version
Query Time                  5-8 sec                     6-10 sec
Sources                     15 (web only)               20+ (web + docs)
Features                    5                           10+
Export Formats              2                           3
Citation Tracking           ❌                          ✅
PDF Support                 ❌                          ✅
RAG                         ❌                          ✅

Key Selling Points

"We integrated RAG" - Users can upload their own documents
"Full citation tracking" - Every source is traceable
"Performance monitoring" - See which agents are slow
"Multi-source intelligence" - Combines documents + web
"Production-ready" - Error handling, exports, caching

Cost Breakdown

Runtime Cost: $0.00
API Calls per Query: 4-5 (Groq) + 5-7 (Tavily)
Storage: Local (ChromaDB)
Scaling Cost: Minimal