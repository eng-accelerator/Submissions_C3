from core.graph import build_graph
from core.schema import ResearchState
from core.api_registry import APIRegistry

def test_demo_flow():
    print("--- Starting End-to-End Demo Verification ---")
    
    # Ensure Demo Mode
    # In our impl, if no keys in APIRegistry, it defaults to demo behaviors in agents.
    APIRegistry.clear_all() 
    
    initial_state = ResearchState(
        question="What is the future of AI agents?",
        depth="Fast",
        template="Research Report",
        demo_mode=True
    )
    
    app = build_graph()
    result = app.invoke(initial_state)
    
    # Assertions
    print("\n[Assertions]")
    
    # 1. Plan
    if result['plan']:
        print("✅ Plan generated:", result['plan'])
    else:
        print("❌ Plan missing")

    # 2. Sources (Demo)
    if result['sources']:
        print(f"✅ Sources found: {len(result['sources'])}")
        print(f"   First source: {result['sources'][0].title}")
    else:
        print("❌ Sources missing")

    # 3. Claims
    if result['claims']:
        print(f"✅ Claims extracted: {len(result['claims'])}")
    else:
        print("❌ Claims missing")

    # 4. Report
    if result['report_md'] and "# Research Report" in result['report_md']:
        print("✅ Report generated successfully")
    else:
        print("❌ Report missing or empty")

    # 5. Logs
    if result['logs']:
        print(f"✅ Logs recorded: {len(result['logs'])}")
    else:
        print("❌ Logs missing")
        
    print("\n--- Verification Complete ---")

if __name__ == "__main__":
    test_demo_flow()
