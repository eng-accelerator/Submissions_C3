# Browser Automation AI Agent
A multi-agent AI system that performs:
- Flow discovery
- Script generation
- Browser automation execution
- Error diagnosis
- Self-healing script repair
- Visual regression testing


## Install

pip install -r requirements.txt playwright install

## Run Backend

uvicorn src.api.server:app --reload

## Run UI

streamlit run src/ui/app.py

## Run Tests

pytest -vv