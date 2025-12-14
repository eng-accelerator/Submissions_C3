---
title: Cybersecurity Multi-Agent System
emoji: 🔒
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
license: apache-2.0
---

# 🚀 Cybersecurity Multi-Agent System

This directory contains **ONLY** the files required for deploying to Hugging Face Spaces.

## 📦 Contents

### Core Files (5)
- `Dockerfile` - Docker configuration
- `requirements.txt` - Python dependencies
- `app.py` - Main Streamlit application
- `coordinator_langgraph.py` - LangGraph coordinator
- `config.json` - System configuration

### Configuration (1)
- `.streamlit/config.toml` - Streamlit theme configuration

### Agents (10)
- `agents/__init__.py`
- `agents/base_agent.py`
- `agents/log_monitor_agent.py`
- `agents/threat_intelligence_agent.py`
- `agents/vulnerability_scanner_agent.py`
- `agents/incident_response_agent.py`
- `agents/policy_checker_agent.py`
- `agents/external_api_agent.py`
- `agents/cve_rag_agent.py`
- `agents/cve_rag_agent_simple.py`

### Test Logs (Optional)
- `test_logs/` - Sample log files for testing

---

## 📤 How to Upload

1. **Go to your Hugging Face Space**
2. **Upload all files from this `deploy_hf/` directory**
3. **Make sure the directory structure is preserved**
4. **Wait for the build to complete**

---

## ✅ Total Files

- **16 required files** (minimum)
- **+ test_logs/** (optional, for testing)

---

## 🎯 Ready to Deploy!

All files in this directory are ready for Hugging Face Spaces deployment.
