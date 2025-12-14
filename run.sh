#!/bin/bash
# Activate virtual environment
source venv/bin/activate

# Ensure dependencies are installed
pip install -q -r requirements.txt

# Start the API server in background
uvicorn src.api.server:app --reload &

# Start the Streamlit UI
streamlit run src/ui/app.py