---

### File: `app.py`
```python
"""
Main Streamlit Application
Component 6: Main Application Controller
"""

import streamlit as st
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Import components
from components.image_processing import (
    preprocess_image,
    image_to_base64,
    generate_clip_embedding,
    extract_image_metadata
)
from components.rag_system import load_design_patterns_to_faiss
from components.orchestration import (
    create_orchestration_graph,
    execute_analysis_workflow
)

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Design Analysis PoC",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_resource
def initialize_system():
    """
    Function 6.1: One-time initialization of all components
    
    Returns:
        tuple: (faiss_index, metadata, graph)
    """
    with st.spinner("🔄 Initializing AI system (this may take a minute)..."):
        try:
            # Load FAISS index with design patterns
            patterns_path = "data/design_patterns.json"
            
            if not os.path.exists(patterns_path):
                st.error(f"❌ Design patterns file not found: {patterns_path}")
                st.stop()
            
            faiss_index, metadata = load_design_patterns_to_faiss(patterns_path)
            
            # Create LangGraph workflow
            graph = create_orchestration_graph(faiss_index, metadata)
            
            st.success("✅ System initialized successfully!")
            return faiss_index, metadata, graph
        
        except Exception as e:
            st.error(f"❌ Initialization error: {str(e)}")
            st.stop()


def render_results_dashboard(final_report):
    """
    Function 1.3: Display analysis results
    
    Args:
        final_report: Dict containing analysis results
    """
    st.divider()
    st.header("📊 Analysis Results")
    
    # Check for errors
    if "error" in final_report or "error_message" in final_report:
        st.error(f"Analysis error: {final_report.get('error_message', final_report.get('error', 'Unknown error'))}")
        with st.expander("Raw Error Details"):
            st.json(final_report)
        return
    
    # Overall scores
    st.subheader("📈 Overall Scores")
    col1, col2, col3, col4 = st.columns(4)
    
    overall_score = final_report.get('overall_score', 0)
    agent_scores = final_report.get('agent_scores', {})
    
    with col1:
        st.metric("Overall Score", f"{overall_score}/100", 
                 delta=None,
                 delta_color="normal")
    with col2:
        visual_score = agent_scores.get('visual', 0)
        st.metric("Visual Design", f"{visual_score}/100")
    with col3:
        ux_score = agent_scores.get('ux', 0)
        st.metric("User Experience", f"{ux_score}/100")
    with col4:
        market_score = agent_scores.get('market', 0)
        st.metric("Market Fit", f"{market_score}/100")
    
    # Recommendations
    st.divider()
    st.subheader("🎯 Top Recommendations")
    
    recommendations = final_report.get('top_recommendations', [])
    
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            priority = rec.get('priority', 'medium')
            
            # Priority emoji
            priority_emoji = {
                'critical': '🔴',
                'high': '🟠',
                'medium': '🟡',
                'low': '🟢'
            }.get(priority.lower(), '⚪')
            
            with st.expander(f"{priority_emoji} {i}. [{rec.get('source', 'General')}] {rec.get('recommendation', 'No recommendation')[:100]}...", 
                           expanded=(i <= 3)):
                st.write(f"**Priority:** {priority.upper()}")
                st.write(f"**Source:** {rec.get('source', 'N/A')}")
                st.write(f"**Recommendation:** {rec.get('recommendation', 'N/A')}")
    else:
        st.info("No specific recommendations generated.")
    
    # Detailed findings tabs
    st.divider()
    st.subheader("🔍 Detailed Analysis")
    
    detailed = final_report.get('detailed_findings', {})
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎨 Visual Design",
        "👤 User Experience",
        "📈 Market Analysis",
        "📄 Raw Data"
    ])
    
    with tab1:
        visual_data = detailed.get('visual', {})
        if visual_data:
            st.json(visual_data)
        else:
            st.info("No visual analysis data available")
    
    with tab2:
        ux_data = detailed.get('ux', {})
        if ux_data:
            st.json(ux_data)
        else:
            st.info("No UX analysis data available")
    
    with tab3:
        market_data = detailed.get('market', {})
        if market_data:
            st.json(market_data)
        else:
            st.info("No market analysis data available")
    
    with tab4:
        st.json(final_report)


def main():
    """
    Function 6.2: Main application entry point
    """
    # Title
    st.title("🎨 Multimodal Design Analysis Suite")
    st.markdown("*Powered by OpenRouter API + LangGraph + FAISS RAG + CLIP*")
    st.markdown("---")
    
    # Check API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or api_key == "your_openrouter_api_key_here":
        st.error("❌ Please set your OPENROUTER_API_KEY in the .env file")
        st.info("Get your API key from: https://openrouter.ai/keys")
        st.stop()
    
    # Initialize system
    faiss_index, metadata, graph = initialize_system()
    
    # Sidebar
    with st.sidebar:
        st.header("📤 Upload Design")
        
        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=['png', 'jpg', 'jpeg'],
            help="Upload a social media design for AI analysis"
        )
        
        platform = st.selectbox(
            "Target Platform",
            ["Instagram", "Facebook", "LinkedIn", "Twitter", "Pinterest"],
            help="Select the platform this design is intended for"
        )
        
        st.divider()
        
        st.markdown("### 🤖 Model Info")
        vision_model = os.getenv("VISION_MODEL", "openai/gpt-4-vision-preview")
        st.code(vision_model, language="text")
        
        st.markdown("### ℹ️ About")
        st.markdown("""
        This tool uses:
        - **GPT-4 Vision** for image analysis
        - **LangGraph** for multi-agent orchestration
        - **FAISS** for design pattern retrieval
        - **CLIP** for image embeddings
        """)
    
    # Main content area
    if uploaded_file is not None:
        # Display uploaded image
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📸 Uploaded Design")
            image = st.image(uploaded_file, use_column_width=True)
        
        with col2:
            st.subheader("ℹ️ Image Information")
            
            try:
                # Process image to get metadata
                processed_img = preprocess_image(uploaded_file)
                metadata_info = extract_image_metadata(processed_img)
                
                st.write(f"**Dimensions:** {metadata_info['width']} x {metadata_info['height']}px")
                st.write(f"**Aspect Ratio:** {metadata_info['aspect_ratio']}:1")
                st.write(f"**Format:** {metadata_info['format']}")
                st.write(f"**Color Mode:** {metadata_info['mode']}")
                st.write(f"**Target Platform:** {platform}")
                
            except Exception as e:
                st.warning(f"Could not extract metadata: {e}")
        
        st.divider()
        
        # Analyze button
        analyze_button = st.button(
            "🚀 Analyze Design",
            type="primary",
            use_container_width=True,
            help="Start AI-powered design analysis"
        )
        
        if analyze_button:
            try:
                with st.spinner("🔄 Processing image..."):
                    # Reset file pointer
                    uploaded_file.seek(0)
                    
                    # Process image
                    processed_image = preprocess_image(uploaded_file)
                    img_base64 = image_to_base64(processed_image)
                    img_embedding = generate_clip_embedding(processed_image)
                    img_metadata = extract_image_metadata(processed_image)
                
                # Create initial state
                initial_state = {
                    "image_base64": img_base64,
                    "image_embedding": img_embedding.tolist(),
                    "platform": platform,
                    "image_metadata": img_metadata,
                    "visual_analysis": {},
                    "ux_analysis": {},
                    "market_analysis": {},
                    "final_report": {},
                    "current_step": 0,
                    "total_steps": 4,
                    "step_message": "",
                    "model_used": os.getenv("VISION_MODEL", "openai/gpt-4-vision-preview")
                }
                
                # Progress tracking
                progress_placeholder = st.empty()
                status_placeholder = st.empty()
                
                def progress_callback(step, total, message):
                    """Update progress bar and status"""
                    progress_placeholder.progress(step / total)
                    status_placeholder.info(message)
                
                # Execute workflow
                st.info("🤖 Running AI analysis workflow...")
                final_state = execute_analysis_workflow(
                    graph,
                    initial_state,
                    progress_callback
                )
                
                # Clear progress indicators
                progress_placeholder.empty()
                status_placeholder.success("✅ Analysis complete!")
                
                # Display results
                final_report = final_state.get('final_report', {})
                render_results_dashboard(final_report)
                
                # Download button
                st.divider()
                report_json = json.dumps(final_report, indent=2)
                st.download_button(
                    label="📥 Download Full Report (JSON)",
                    data=report_json,
                    file_name=f"design_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")
                with st.expander("Error Details"):
                    st.exception(e)
    
    else:
        # Welcome screen
        st.info("👆 Upload a design image in the sidebar to begin analysis")
        
        st.markdown("### 🎯 What This Tool Does")
        st.markdown("""
        This AI-powered tool analyzes your social media designs across multiple dimensions:
        
        1. **🎨 Visual Design Analysis**
           - Color palette extraction and harmony
           - Layout composition and balance
           - Typography assessment
        
        2. **👤 UX Critique**
           - Usability heuristics evaluation
           - Accessibility compliance (WCAG)
           - Interaction pattern analysis
        
        3. **📈 Market Research**
           - Platform-specific optimization
           - Current trend alignment
           - Audience fit and engagement prediction
        """)
        
        st.markdown("### 🚀 How It Works")
        st.markdown("""
        1. Upload your design (PNG, JPG, JPEG)
        2. Select target platform (Instagram, Facebook, etc.)
        3. Click "Analyze Design"
        4. AI agents analyze your design using:
           - Vision AI (GPT-4V) for image understanding
           - RAG system with 30+ design patterns
           - Multi-agent orchestration via LangGraph
        5. Get actionable recommendations with priority levels
        """)


if __name__ == "__main__":
    main()
```

---

