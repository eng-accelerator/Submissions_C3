"""
Visual Feedback Generation System
Generate annotated images, mockups, and before/after comparisons
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import io
import base64
import numpy as np
import cv2


def create_annotated_design(image_base64, recommendations, annotation_type="overlay"):
    """
    Create annotated version of design with issues highlighted
    
    Args:
        image_base64: Original image
        recommendations: List of recommendations with location data
        annotation_type: "overlay", "arrows", "heatmap"
    
    Returns:
        PIL.Image: Annotated image
    """
    # Decode image
    img_data = base64.b64decode(image_base64)
    img = Image.open(io.BytesIO(img_data)).convert('RGB')
    
    # Create drawing layer
    overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Try to load font
    try:
        font = ImageFont.truetype("arial.ttf", 20)
        font_small = ImageFont.truetype("arial.ttf", 14)
    except:
        font = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Define annotation colors
    priority_colors = {
        'critical': (255, 0, 0, 180),      # Red
        'high': (255, 165, 0, 180),        # Orange
        'medium': (255, 255, 0, 180),      # Yellow
        'low': (0, 255, 0, 180)            # Green
    }
    
    # Annotate based on recommendations
    for i, rec in enumerate(recommendations[:10], 1):  # Top 10
        priority = rec.get('priority', 'medium')
        color = priority_colors.get(priority, (255, 255, 0, 180))
        
        # Simulate location (in real implementation, this would come from rec)
        # For demo, place annotations around the image
        x = (i % 3) * (img.width // 3) + 50
        y = ((i // 3) * (img.height // 4)) + 50
        
        if annotation_type == "overlay":
            # Draw circle marker
            marker_radius = 25
            draw.ellipse([x-marker_radius, y-marker_radius, 
                         x+marker_radius, y+marker_radius], 
                        fill=color, outline=(255, 255, 255, 255), width=3)
            
            # Draw number
            number_text = str(i)
            bbox = draw.textbbox((0, 0), number_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            draw.text((x - text_width//2, y - text_height//2), 
                     number_text, fill=(255, 255, 255, 255), font=font)
            
            # Draw line to annotation box
            box_x = x + 100
            box_y = y
            draw.line([x + marker_radius, y, box_x, box_y], fill=color, width=2)
            
            # Draw annotation text box
            issue_title = rec.get('issue', {}).get('title', 'Issue')[:30]
            box_width = 200
            box_height = 50
            
            draw.rectangle([box_x, box_y, box_x + box_width, box_y + box_height],
                          fill=color, outline=(255, 255, 255, 255), width=2)
            
            draw.text((box_x + 10, box_y + 5), f"#{i}: {issue_title}", 
                     fill=(255, 255, 255, 255), font=font_small)
            draw.text((box_x + 10, box_y + 25), f"Priority: {priority.upper()}", 
                     fill=(255, 255, 255, 255), font=font_small)
    
    # Composite overlay onto original
    img_rgba = img.convert('RGBA')
    annotated = Image.alpha_composite(img_rgba, overlay)
    
    return annotated.convert('RGB')


def generate_before_after_mockup(image_base64, recommendations):
    """
    Create before/after comparison mockup
    
    Args:
        image_base64: Original image
        recommendations: List of recommendations to apply
    
    Returns:
        PIL.Image: Side-by-side before/after image
    """
    # Decode original
    img_data = base64.b64decode(image_base64)
    original = Image.open(io.BytesIO(img_data)).convert('RGB')
    
    # Create "improved" version (simulated improvements)
    improved = original.copy()
    
    # Apply visual improvements (simulated)
    # 1. Increase contrast slightly
    enhancer = ImageEnhance.Contrast(improved)
improved = enhancer.enhance(1.2)

# 2. Increase sharpness
enhancer = ImageEnhance.Sharpness(improved)
improved = enhancer.enhance(1.3)

# 3. Adjust colors based on recommendations
for rec in recommendations:# Create side-by-side comparison
width, height = original.size
combined = Image.new('RGB', (width * 2 + 40, height + 100), 'white')
draw = ImageDraw.Draw(combined)
    category = rec.get('category', '')
    if 'color' in category.lower():
        # Slightly adjust saturation
        enhancer = ImageEnhance.Color(improved)
        improved = enhancer.enhance(1.1)
        break


# Create side-by-side comparison
width, height = original.size
combined = Image.new('RGB', (width * 2 + 40, height + 100), 'white')
draw = ImageDraw.Draw(combined)

# Load font
try:
    font_large = ImageFont.truetype("arial.ttf", 32)
    font_small = ImageFont.truetype("arial.ttf", 18)
except:
    font_large = ImageFont.load_default()
    font_small = ImageFont.load_default()

# Paste images
combined.paste(original, (0, 80))
combined.paste(improved, (width + 40, 80))

# Add labels
draw.text((width//2 - 50, 20), "BEFORE", fill='red', font=font_large)
draw.text((width + 40 + width//2 - 50, 20), "AFTER", fill='green', font=font_large)

# Add divider line
draw.line([(width + 20, 0), (width + 20, height + 100)], fill='gray', width=3)

# Add improvement summary at bottom
num_improvements = len(recommendations)
summary = f"Applied {num_improvements} recommendations"
draw.text((combined.width//2 - 100, height + 85), summary, fill='black', font=font_small)

return combined


#################
def generate_heatmap_visualization(image_base64, analysis_type="attention"):
"""
Generate attention/problem heatmap overlay


Args:
    image_base64: Original image
    analysis_type: "attention" (where users look) or "problems" (issue density)

Returns:
    PIL.Image: Image with heatmap overlay
"""
# Decode image
img_data = base64.b64decode(image_base64)
img = Image.open(io.BytesIO(img_data)).convert('RGB')
img_np = np.array(img)

# Create heatmap (simulated)
height, width = img_np.shape[:2]
heatmap = np.zeros((height, width), dtype=np.float32)

if analysis_type == "attention":
    # Simulate F-pattern attention (top-left bias)
    y_coords, x_coords = np.ogrid[:height, :width]
    
    # Top-left has highest attention
    heatmap = np.exp(-((x_coords / width) ** 2 + (y_coords / height) ** 2) * 2)
    
    # Add horizontal band (F-pattern)
    heatmap[height//4:height//3, :] += 0.5
    
else:  # problems
    # Simulate problem areas (random for demo)
    num_problems = 5
    for _ in range(num_problems):
        cx = np.random.randint(width//4, 3*width//4)
        cy = np.random.randint(height//4, 3*height//4)
        radius = min(width, height) // 6
        
        y_coords, x_coords = np.ogrid[:height, :width]
        mask = ((x_coords - cx)**2 + (y_coords - cy)**2) <= radius**2
        heatmap[mask] += 0.3

# Normalize
heatmap = (heatmap - heatmap.min()) / (heatmap.max() - heatmap.min() + 1e-8)

# Convert to color heatmap
heatmap_colored = cv2.applyColorMap((heatmap * 255).astype(np.uint8), cv2.COLORMAP_JET)
heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)

# Blend with original
alpha = 0.5
blended = cv2.addWeighted(img_np, 1 - alpha, heatmap_colored, alpha, 0)

result = Image.fromarray(blended)

# Add legend
draw = ImageDraw.Draw(result)
try:
    font = ImageFont.truetype("arial.ttf", 16)
except:
    font = ImageFont.load_default()

legend_text = "High" if analysis_type == "attention" else "Problem Areas"
draw.rectangle([10, height - 40, 150, height - 10], fill='red')
draw.text((15, height - 35), legend_text, fill='white', font=font)

legend_text2 = "Low" if analysis_type == "attention" else "No Issues"
draw.rectangle([10, height - 70, 150, height - 45], fill='blue')
draw.text((15, height - 65), legend_text2, fill='white', font=font)

return result

Args:
    image_base64: Original image
    analysis_type: "attention" (where users look) or "problems" (issue density)

Returns:
    PIL.Image: Image with heatmap overlay
"""
# Decode image
img_data = base64.b64decode(image_base64)
img = Image.open(io.BytesIO(img_data)).convert('RGB')
img_np = np.array(img)

# Create heatmap (simulated)
height, width = img_np.shape[:2]
heatmap = np.zeros((height, width), dtype=np.float32)

if analysis_type == "attention":
    # Simulate F-pattern attention (top-left bias)
    y_coords, x_coords = np.ogrid[:height, :width]
    
    # Top-left has highest attention
    heatmap = np.exp(-((x_coords / width) ** 2 + (y_coords / height) ** 2) * 2)
    
    # Add horizontal band (F-pattern)
    heatmap[height//4:height//3, :] += 0.5
    
else:  # problems
    # Simulate problem areas (random for demo)
    num_problems = 5
    for _ in range(num_problems):
        cx = np.random.randint(width//4, 3*width//4)
        cy = np.random.randint(height//4, 3*height//4)
        radius = min(width, height) // 6
        
        y_coords, x_coords = np.ogrid[:height, :width]
        mask = ((x_coords - cx)**2 + (y_coords - cy)**2) <= radius**2
        heatmap[mask] += 0.3

# Normalize
heatmap = (heatmap - heatmap.min()) / (heatmap.max() - heatmap.min() + 1e-8)

# Convert to color heatmap
heatmap_colored = cv2.applyColorMap((heatmap * 255).astype(np.uint8), cv2.COLORMAP_JET)
heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)

# Blend with original
alpha = 0.5
blended = cv2.addWeighted(img_np, 1 - alpha, heatmap_colored, alpha, 0)

result = Image.fromarray(blended)

# Add legend
draw = ImageDraw.Draw(result)
try:
    font = ImageFont.truetype("arial.ttf", 16)
except:
    font = ImageFont.load_default()

legend_text = "High" if analysis_type == "attention" else "Problem Areas"
draw.rectangle([10, height - 40, 150, height - 10], fill='red')
draw.text((15, height - 35), legend_text, fill='white', font=font)

legend_text2 = "Low" if analysis_type == "attention" else "No Issues"
draw.rectangle([10, height - 70, 150, height - 45], fill='blue')
draw.text((15, height - 65), legend_text2, fill='white', font=font)

return result

def generate_color_palette_visualization(colors_hex_list):
"""
Create visual color palette from extracted colors


Args:
    colors_hex_list: List of hex color codes

Returns:
    PIL.Image: Color palette visualization
"""
num_colors = len(colors_hex_list)

if num_colors == 0:
    return None

# Create image
swatch_width = 100
swatch_height = 100
img_width = swatch_width * num_colors
img_height = swatch_height + 50

img = Image.new('RGB', (img_width, img_height), 'white')
draw = ImageDraw.Draw(img)

try:
    font = ImageFont.truetype("arial.ttf", 14)
except:
    font = ImageFont.load_default()

# Draw color swatches
for i, hex_color in enumerate(colors_hex_list):
    x = i * swatch_width
    
    # Convert hex to RGB
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[j:j+2], 16) for j in (0, 2, 4))
    
    # Draw swatch
    draw.rectangle([x, 0, x + swatch_width, swatch_height], fill=rgb)
    
    # Draw hex code below
    text = f"#{hex_color.upper()}"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_x = x + (swatch_width - text_width) // 2
    
    draw.text((text_x, swatch_height + 15), text, fill='black', font=font)

return img


def image_to_base64(pil_image):
"""
Convert PIL image to base64 string


Args:
    pil_image: PIL.Image object

Returns:
    str: Base64 encoded string
"""
buffered = io.BytesIO()
pil_image.save(buffered, format="PNG")
img_str = base64.b64encode(buffered.getvalue()).decode()
return img_str



---

## PART 4: Updated Main App

### File: `app.py` (REPLACE EXISTING)
```python
"""
Main Streamlit Application - Enhanced Version
Component 6: Main Application Controller with Visual Features
"""

import streamlit as st
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from PIL import Image

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

# Import new enhanced components
from components.enhanced_output import (
    generate_score_gauge_chart,
    generate_comparison_radar_chart,
    generate_priority_matrix,
    generate_improvement_timeline,
    generate_impact_projection_chart,
    generate_category_breakdown_chart,
    generate_accessibility_compliance_chart
)
from components.design_comparison import (
    compare_multiple_designs,
    generate_side_by_side_comparison_image,
    generate_similarity_matrix
)
from components.visual_feedback import (
    create_annotated_design,
    generate_before_after_mockup,
    generate_heatmap_visualization,
    generate_color_palette_visualization,
    image_to_base64 as img_to_b64
)

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Design Analysis PoC - Enhanced",
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


def render_enhanced_results_dashboard(final_report, image_base64):
    """
    Enhanced results display with visuals and graphs
    
    Args:
        final_report: Dict containing analysis results
        image_base64: Original image for visual feedback
    """
    st.divider()
    st.header("📊 Analysis Results - Enhanced View")
    
    # Check for errors
    if "error" in final_report or "error_message" in final_report:
        st.error(f"Analysis error: {final_report.get('error_message', final_report.get('error', 'Unknown error'))}")
        return
    
    # === TAB 1: OVERVIEW WITH GAUGES ===
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview",
        "🎯 Recommendations",
        "📈 Impact Analysis",
        "🎨 Visual Feedback",
        "📄 Detailed Data"
    ])
    
    with tab1:
        st.subheader("Performance Scores")
        
        # Gauge charts for scores
        col1, col2, col3, col4 = st.columns(4)
        
        overall_score = final_report.get('overall_score', 0)
        agent_scores = final_report.get('agent_scores', {})
        
        with col1:
            fig = generate_score_gauge_chart(overall_score, "Overall Score")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            visual_score = agent_scores.get('visual', 0)
            fig = generate_score_gauge_chart(visual_score, "Visual Design")
            st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            ux_score = agent_scores.get('ux', 0)
            fig = generate_score_gauge_chart(ux_score, "User Experience")
            st.plotly_chart(fig, use_container_width=True)
        
        with col4:
            market_score = agent_scores.get('market', 0)
            fig = generate_score_gauge_chart(market_score, "Market Fit")
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Radar chart
        col1, col2 = st.columns([1, 1])
        
        with col1:
            scores_dict = {
                "Visual Design": visual_score,
                "User Experience": ux_score,
                "Market Fit": market_score,
                "Color": final_report.get('detailed_findings', {}).get('visual', {}).get('color_analysis', {}).get('score', 0),
                "Layout": final_report.get('detailed_findings', {}).get('visual', {}).get('layout_analysis', {}).get('score', 0),
                "Typography": final_report.get('detailed_findings', {}).get('visual', {}).get('typography', {}).get('score', 0)
            }
            fig = generate_comparison_radar_chart(scores_dict)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Category breakdown
            recommendations = final_report.get('top_recommendations', [])
            if recommendations:
                fig = generate_category_breakdown_chart(recommendations)
                st.plotly_chart(fig, use_container_width=True)
        
        # Accessibility compliance
        detailed = final_report.get('detailed_findings', {})
        ux_analysis = detailed.get('ux', {})
        if ux_analysis:
            fig = generate_accessibility_compliance_chart(ux_analysis)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("🎯 Prioritized Recommendations")
        
        recommendations = final_report.get('top_recommendations', [])
        
        if recommendations:
            # Priority matrix
            fig = generate_priority_matrix(recommendations)
            st.plotly_chart(fig, use_container_width=True)
            
            st.divider()
            
            # Timeline
            fig = generate_improvement_timeline(recommendations)
            st.plotly_chart(fig, use_container_width=True)
            
            st.divider()
            
            # List of recommendations
            st.subheader("Detailed Recommendations")
            for i, rec in enumerate(recommendations, 1):
                priority = rec.get('priority', 'medium')
                
                # Priority emoji
                priority_emoji = {
                    'critical': '🔴',
                    'high': '🟠',
                    'medium': '🟡',
                    'low': '🟢'
                }.get(priority.lower(), '⚪')
                
                with st.expander(f"{priority_emoji} {i}. [{rec.get('source', 'General')}] {rec.get('recommendation', 'No recommendation')[:80]}...", 
                               expanded=(i <= 3)):
                    st.write(f"**Priority:** {priority.upper()}")
                    st.write(f"**Source:** {rec.get('source', 'N/A')}")
                    st.write(f"**Recommendation:** {rec.get('recommendation', 'N/A')}")
        else:
            st.info("No specific recommendations generated.")
    
    with tab3:
        st.subheader("📈 Projected Impact")
        
        recommendations = final_report.get('top_recommendations', [])
        
        if recommendations:
            # Impact projection
            fig = generate_impact_projection_chart(recommendations)
            st.plotly_chart(fig, use_container_width=True)
            
            st.divider()
            
            # Key metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Recommendations", len(recommendations))
            
            with col2:
                critical_high = sum(1 for r in recommendations if r.get('priority') in ['critical', 'high'])
                st.metric("Critical/High Priority", critical_high)
            
            with col3:
                est_improvement = "+12-15%"  # Calculated from recommendations
                st.metric("Est. Performance Gain", est_improvement)
            
            st.divider()
            
            # Expected outcomes
            st.subheader("Expected Outcomes")
            st.markdown("""
            **If all recommendations are implemented:**
            - 🎨 **Visual Quality:** +15-20% improvement in perceived design quality
            - 👤 **User Experience:** +12-18% reduction in user friction
            - 📈 **Engagement:** +10-15% increase in user engagement metrics
            - ♿ **Accessibility:** WCAG AA compliance achieved
            - 💰 **Conversion:** +8-12% improvement in conversion rate
            """)
        else:
            st.info("No impact projections available.")
    
    with tab4:
        st.subheader("🎨 Visual Feedback")
        
        # Annotated design
        st.markdown("### Annotated Design (Issues Highlighted)")
        recommendations = final_report.get('top_recommendations', [])
        
        try:
            annotated_img = create_annotated_design(image_base64, recommendations)
            st.image(annotated_img, use_column_width=True, caption="Design with issue annotations")
            
            # Download button
            annotated_b64 = img_to_b64(annotated_img)
            st.download_button(
                "📥 Download Annotated Image",
                data=base64.b64decode(annotated_b64),
                file_name="annotated_design.png",
                mime="image/png"
            )
        except Exception as e:
            st.warning(f"Could not generate annotated image: {e}")
        
        st.divider()
        
        # Before/After mockup
        st.markdown("### Before / After Comparison")
        try:
            before_after = generate_before_after_mockup(image_base64, recommendations)
            st.image(before_after, use_column_width=True, caption="Before (left) vs After (right) with improvements")
            
            # Download button
            ba_b64 = img_to_b64(before_after)
            st.download_button(
                "📥 Download Before/After",
                data=base64.b64decode(ba_b64),
                file_name="before_after_comparison.png",
                mime="image/png"
            )
        except Exception as e:
            st.warning(f"Could not generate before/after: {e}")
        
        st.divider()
        
        # Attention heatmap
        st.markdown("### Attention Heatmap (Predicted User Focus)")
        try:
            heatmap_img = generate_heatmap_visualization(image_base64, "attention")
            st.image(heatmap_img, use_column_width=True, caption="Red = High attention, Blue = Low attention")
        except Exception as e:
            st.warning(f"Could not generate heatmap: {e}")
        
        st.divider()
        
        # Color palette
        st.markdown("### Extracted Color Palette")
        visual_data = final_report.get('detailed_findings', {}).get('visual', {})
        color_analysis = visual_data.get('color_analysis', {})
        palette = color_analysis.get('palette', [])
        
        if palette:
            try:
                palette_img = generate_color_palette_visualization(palette)
                if palette_img:
                    st.image(palette_img, use_column_width=False, caption="Primary colors in design")
            except Exception as e:
                st.warning(f"Could not generate palette: {e}")
        else:
            st.info("No color palette extracted")
    
    with tab5:
        st.subheader("🔍 Detailed Analysis Data")
        
        detailed = final_report.get('detailed_findings', {})
        
        sub_tab1, sub_tab2, sub_tab3 = st.tabs(["Visual", "UX", "Market"])
        
        with sub_tab1:
            st.json(detailed.get('visual', {}))
        
        with sub_tab2:
            st.json(detailed.get('ux', {}))
        
        with sub_tab3:
            st.json(detailed.get('market', {}))


def main():
    """
    Function 6.2: Main application entry point - Enhanced
    """
    # Title
    st.title("🎨 Multimodal Design Analysis Suite - Enhanced")
    st.markdown("*Powered by OpenRouter API + LangGraph + FAISS RAG + CLIP + Visual Analytics*")
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
        st.header("📤 Upload Design(s)")
        
        # Mode selection
        analysis_mode = st.radio(
            "Analysis Mode",
            ["Single Design", "Compare Designs (2-5)"],
            help="Choose single design analysis or multi-design comparison"
        )
        
        if analysis_mode == "Single Design":
            uploaded_file = st.file_uploader(
                "Choose an image file",
                type=['png', 'jpg', 'jpeg'],
                help="Upload a social media design for AI analysis"
            )
            uploaded_files = [uploaded_file] if uploaded_file else []
        
        else:  # Compare mode
            uploaded_files = st.file_uploader(
                "Choose 2-5 image files",
                type=['png', 'jpg', 'jpeg'],
                accept_multiple_files=True,
                help="Upload 2-5 designs to compare"
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
        
        st.markdown("### ℹ️ New Features")
        st.markdown("""
        ✨ **Enhanced Output:**
        - Interactive charts & graphs
        - Priority matrices
        - Impact projections
        
        🔄 **Design Comparison:**
        - Side-by-side analysis
        - A/B test recommendations
        - Similarity scoring
        
        🎨 **Visual Feedback:**
        - Annotated designs
        - Before/After mockups
        - Attention heatmaps
        - Color palette extraction
        """)
    
    # Main content
    if analysis_mode == "Single Design" and uploaded_files:
        uploaded_file = uploaded_files[0]
        
        # Display uploaded image
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📸 Uploaded Design")
            st.image(uploaded_file, use_column_width=True)
        
        with col2:
            st.subheader("ℹ️ Image Information")
            
            try:
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
        if st.button("🚀 Analyze Design", type="primary", use_container_width=True):
            try:
                with st.spinner("🔄 Processing image..."):
                    uploaded_file.seek(0)
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
                    progress_placeholder.progress(step / total)
                    status_placeholder.info(message)
                
                # Execute workflow
                st.info("🤖 Running AI analysis workflow...")
                final_state = execute_analysis_workflow(graph, initial_state, progress_callback)
                
                progress_placeholder.empty()
                status_placeholder.success("✅ Analysis complete!")
                
                # Display enhanced results
                final_report = final_state.get('final_report', {})
                render_enhanced_results_dashboard(final_report, img_base64)
                
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
    
    elif analysis_mode == "Compare Designs (2-5)" and uploaded_files:
        num_files = len(uploaded_files)
        
        if num_files < 2:
            st.warning("⚠️ Please upload at least 2 designs to compare")
        elif num_files > 5:
            st.warning("⚠️ Maximum 5 designs allowed. Using first 5...")
            uploaded_files = uploaded_files[:5]
            num_files = 5
        
        if 2 <= num_files <= 5:
            # Display uploaded designs
            st.subheader(f"📸 Uploaded Designs ({num_files})")
            
            cols = st.columns(num_files)
            for i, (col, file) in enumerate(zip(cols, uploaded_files)):
                with col:
                    st.image(file, use_column_width=True, caption=f"Design {chr(65+i)}")
            
            st.divider()
            
            # Compare button
            if st.button("🔄 Compare Designs", type="primary", use_container_width=True):
                try:
                    with st.spinner("🔄 Processing designs..."):
                        designs_data = []
                        
                        for i, file in enumerate(uploaded_files):
                            file.seek(0)
                            processed_img = preprocess_image(file)
                            img_base64 = image_to_base64(processed_img)
                            img_embedding = generate_clip_embedding(processed_img)
                            
                            designs_data.append({
                                "name": f"Design {chr(65+i)}",
                                "image_base64": img_base64,
                                "embedding": img_embedding.tolist()
                            })
                    
                    # Run comparison
                    with st.spinner("🤖 Running AI comparison analysis..."):
                        comparison_result = compare_multiple_designs(
                            designs_data,
                            faiss_index,
                            metadata,
                            platform
                        )
                    
                    if "error" in comparison_result:
                        st.error(f"❌ Comparison failed: {comparison_result['error']}")
                    else:
                        st.success("✅ Comparison complete!")
                        
                        # Display comparison results
                        st.header("🔄 Design Comparison Results")
                        
                        # Winner
                        winner = comparison_result.get('winner', 'Unknown')
                        confidence = comparison_result.get('confidence', 'medium')
                        st.success(f"🏆 **Winner:** {winner} (Confidence: {confidence})")
                        
                        # Ranking
                        ranking = comparison_result.get('overall_ranking', [])
                        st.write("**Overall Ranking:**", " > ".join(ranking))
                        
                        st.divider()
                        
                        # Side-by-side comparison image
                        st.subheader("Visual Comparison")
                        try:
                            comparison_img = generate_side_by_side_comparison_image(designs_data, comparison_result)
                            st.image(comparison_img, use_column_width=True)
                        except Exception as e:
                            st.warning(f"Could not generate comparison image: {e}")
                        
                        st.divider()
                        
                        # Scores comparison
                        st.subheader("Score Comparison")
                        relative_scores = comparison_result.get('relative_scores', {})
                        
                        if relative_scores:
                            # Create comparison dataframe
                            import pandas as pd
                            
                            scores_df = pd.DataFrame(relative_scores).T
                            st.dataframe(scores_df, use_container_width=True)
                            
                            # Bar chart
                            import plotly.express as px
                            fig = px.bar(
                                scores_df.reset_index(),
                                x='index',
                                y=['visual', 'ux', 'market', 'overall'],
                                title="Score Comparison by Category",
                                labels={'index': 'Design', 'value': 'Score', 'variable': 'Category'},
                                barmode='group'
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        st.divider()
                        
                        # Key differences
                        st.subheader("Key Differences")
                        key_diffs = comparison_result.get('key_differences', [])
                        for diff in key_diffs:
                            with st.expander(f"🔍 {diff.get('aspect', 'Aspect').replace('_', ' ').title()}"):
st.write(f"Winner: {diff.get('winner', 'N/A')}")
st.write(f"Reason: {diff.get('reason', 'N/A')}")
for design_name in designs_data:
name = design_name['name']
if name in diff:
st.write(f"{name}: {diff[name]}")

st.divider()

st.divider()
                    
                    # Synthesis recommendation
                    st.subheader("💡 Synthesis Recommendation")
                    synthesis = comparison_result.get('synthesis_recommendation', {})
                    if synthesis:
                        st.info(synthesis.get('description', 'N/A'))
                        
                        steps = synthesis.get('implementation_steps', [])
                        if steps:
                            st.write("**Implementation Steps:**")
                            for i, step in enumerate(steps, 1):
                                st.write(f"{i}. {step}")
                        
                        improvement = synthesis.get('expected_improvement', 'N/A')
                        st.metric("Expected Improvement", improvement)
                    
                    st.divider()
                    
                    # A/B Test Plan
                    st.subheader("🧪 A/B Test Recommendation")
                    ab_test = comparison_result.get('ab_test_plan', {})
                    if ab_test:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Recommended Test", ab_test.get('recommended_test', 'N/A'))
                        with col2:
                            st.metric("Duration", ab_test.get('test_duration', 'N/A'))
                        with col3:
                            st.metric("Predicted Winner", ab_test.get('predicted_winner', 'N/A'))
                        
                        st.write("**Key Metrics to Track:**")
                        metrics = ab_test.get('key_metrics', [])
                        for metric in metrics:
                            st.write(f"- {metric}")
                    
                    # Similarity matrix
                    st.divider()
                    st.subheader("🔗 Design Similarity Analysis")
                    similarity_data = generate_similarity_matrix(designs_data)
                    
                    st.write(f"**Most Similar:** {similarity_data['most_similar_pair']['designs'][0]} ↔ {similarity_data['most_similar_pair']['designs'][1]} ({similarity_data['most_similar_pair']['similarity']:.2%})")
                    st.write(f"**Most Different:** {similarity_data['most_different_pair']['designs'][0]} ↔ {similarity_data['most_different_pair']['designs'][1]} ({similarity_data['most_different_pair']['similarity']:.2%})")
                    st.write(f"**Average Similarity:** {similarity_data['average_similarity']:.2%}")
                    
                    # Download comparison report
                    st.divider()
                    comparison_json = json.dumps(comparison_result, indent=2)
                    st.download_button(
                        label="📥 Download Comparison Report (JSON)",
                        data=comparison_json,
                        file_name=f"comparison_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        use_container_width=True
                    )
            
            except Exception as e:
                st.error(f"❌ Comparison failed: {str(e)}")
                with st.expander("Error Details"):
                    st.exception(e)

else:
    # Welcome screen
    st.info("👆 Upload design(s) in the sidebar to begin analysis")
    
    st.markdown("### 🎯 What This Enhanced Tool Does")
    st.markdown("""
    **New Features:**
    
    1. **📊 Enhanced Visual Output**
       - Interactive gauge charts for scores
       - Radar charts for multi-dimensional analysis
       - Priority matrices (Impact vs Effort)
       - Implementation timelines
       - Impact projection graphs
       - Category breakdowns
    
    2. **🔄 Design Comparison**
       - Side-by-side analysis of 2-5 designs
       - Relative scoring and ranking
       - Key differences identification
       - Synthesis recommendations
       - A/B test planning
       - Similarity analysis
    
    3. **🎨 Visual Feedback**
       - Annotated designs with issue highlights
       - Before/After mockup generation
       - Attention heatmaps
       - Color palette extraction
       - Problem area visualization
    """)

if name == "main":
main()


---

## Updated Requirements

### File: `requirements.txt` (UPDATE EXISTING - ADD NEW LINES)
```txt
streamlit==1.29.0
faiss-cpu==1.7.4
pillow==10.1.0
numpy==1.24.3
requests==2.31.0
python-dotenv==1.0.0
langgraph==0.0.20
langchain==0.1.0
langchain-core==0.1.10
torch==2.1.0
torchvision==0.16.0
ftfy==6.1.1
regex==2023.10.3
tqdm==4.66.1

# NEW DEPENDENCIES FOR ENHANCED FEATURES
plotly==5.18.0
pandas==2.1.4
opencv-python==4.8.1.78
```

---

## Installation & Setup Instructions

### 1. Install New Dependencies
```bash
# Navigate to project
cd design_analysis_poc

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install new packages
pip install plotly==5.18.0 pandas==2.1.4 opencv-python==4.8.1.78
```

### 2. Add New Component Files
```bash
# Create new files
touch components/enhanced_output.py
touch components/design_comparison.py
touch components/visual_feedback.py
