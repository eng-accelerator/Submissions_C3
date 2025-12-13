# components/agents.py

"""
Component 4: Multimodal AI Agent Layer
Technology: OpenRouter API (GPT-4V or other vision models)
"""

import requests
import json
import os
import time
from dotenv import load_dotenv
from components.rag_system import retrieve_relevant_patterns, augment_prompt_with_rag

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
# Use a default model that supports vision on OpenRouter
VISION_MODEL = os.getenv("VISION_MODEL", "openai/gpt-4o")
SITE_URL = os.getenv("SITE_URL", "http://localhost:8501")
APP_NAME = os.getenv("APP_NAME", "DesignAnalysisPoc")


def call_openrouter_vision(image_base64, prompt, temperature=0.7, max_tokens=2000, retries=2, backoff=1.5):
    """
    Function 4.1: Core function to call OpenRouter Vision API
    
    Args:
        image_base64: Base64 encoded image
        prompt: Text prompt
        temperature: Model temperature
        max_tokens: Maximum response tokens
    
    Returns:
        dict: Parsed JSON response
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": SITE_URL,
        "X-Title": APP_NAME,
        "Content-Type": "application/json"
    }
    
    data = {
        "model": VISION_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "response_format": {"type": "json_object"}
    }
    
    last_error = None
    for attempt in range(retries + 1):
        try:
            base_url = OPENROUTER_BASE_URL.rstrip("/")
            response = requests.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                try:
                    result = response.json()
                except ValueError:
                    last_error = {
                        "error": "Invalid JSON response from API",
                        "raw_content": response.text
                    }
                    print("❌ Invalid JSON response from API")
                    raise ValueError("invalid json")
                
                choices = result.get("choices", [])
                if not choices:
                    last_error = {
                        "error": "Empty response from model",
                        "raw_response": result
                    }
                    print("❌ Empty response from model")
                    raise ValueError("empty choices")
                
                content = choices[0].get("message", {}).get("content", "")
                if not content:
                    last_error = {
                        "error": "Empty content from model",
                        "raw_response": result
                    }
                    print("❌ Empty content from model")
                    raise ValueError("empty content")
                
                # Parse JSON response from model output
                try:
                    parsed = json.loads(content)
                    # If model returned stringified JSON inside a key, attempt to parse
                    if isinstance(parsed, dict):
                        for k, v in list(parsed.items()):
                            if isinstance(v, str) and v.strip().startswith("{"):
                                try:
                                    parsed[k] = json.loads(v)
                                except Exception:
                                    pass
                    return parsed
                except json.JSONDecodeError:
                    last_error = {
                        "error": "Invalid JSON response",
                        "raw_content": content,
                        "raw_response": result
                    }
                    print("❌ Invalid JSON response content")
                    raise ValueError("invalid json content")
            else:
                # Try to parse error body for more detail
                try:
                    details = response.json()
                except ValueError:
                    details = response.text
                last_error = {
                    "error": f"API error: {response.status_code}",
                    "details": details
                }
                print(f"❌ API error: {response.status_code} -> {details}")
                raise ValueError(f"status {response.status_code}")
        
        except Exception as e:
            # retry if attempts remain
            if attempt < retries:
                sleep_for = backoff ** attempt
                print(f"🔁 Retry {attempt+1}/{retries} after error: {e}. Sleeping {sleep_for:.2f}s")
                time.sleep(sleep_for)
                continue
            else:
                break
    
    return last_error or {"error": "Unknown error"}


def visual_analysis_agent(state, faiss_index, metadata, top_k=3):
    """
    Function 4.2: Visual Analysis Agent with RAG
    
    Args:
        state: Current analysis state
        faiss_index: FAISS index for RAG
        metadata: Pattern metadata
    
    Returns:
        dict: Updated state with visual_analysis
    """
    print("🎨 Running Visual Analysis Agent...")
    
    # Retrieve relevant patterns
    creative = state.get("creative_type", "")
    query = f"visual design color theory layout composition typography {state['platform']} {creative}"
    patterns = retrieve_relevant_patterns(
        query, faiss_index, metadata, state['platform'], top_k=top_k
    )
    
    # Base prompt
    base_prompt = f"""You are an expert visual design analyst. Analyze this {state['platform']} {creative} design image.

**EVALUATION CRITERIA:**

1. **COLOR PALETTE ANALYSIS:**
   - Extract 5-7 dominant colors (provide hex codes)
   - Assess color harmony (complementary, analogous, triadic)
   - Check contrast ratios for readability
   - Evaluate brand consistency

2. **LAYOUT & COMPOSITION:**
   - Rule of thirds application
   - Visual hierarchy and focal points
   - Balance and symmetry
   - White space utilization
   - Grid alignment

3. **TYPOGRAPHY:**
   - Font readability and legibility
   - Size appropriateness for platform
   - Hierarchy (headings, body, captions)
   - Font pairing effectiveness

**REQUIRED JSON OUTPUT FORMAT:**
{{
    "overall_score": <0-100>,
    "color_analysis": {{
        "score": <0-100>,
        "palette": ["#hex1", "#hex2", "#hex3", "#hex4", "#hex5"],
        "harmony_type": "<complementary/analogous/triadic/monochromatic>",
        "findings": ["finding1", "finding2", "finding3"],
        "recommendations": ["rec1", "rec2", "rec3"]
    }},
    "layout_analysis": {{
        "score": <0-100>,
        "hierarchy_clarity": <0-100>,
        "balance_score": <0-100>,
        "findings": ["finding1", "finding2"],
        "recommendations": ["rec1", "rec2"]
    }},
    "typography": {{
        "score": <0-100>,
        "readability": <0-100>,
        "findings": ["finding1", "finding2"],
        "recommendations": ["rec1", "rec2"]
    }}
}}

Return ONLY valid JSON, no other text."""
    
    # Augment with RAG
    enhanced_prompt = augment_prompt_with_rag(base_prompt, patterns)
    
    # Call vision API
    result = call_openrouter_vision(state['image_base64'], enhanced_prompt, retries=3)
    
    # Update state
    state['visual_analysis'] = result
    state['current_step'] = state.get('current_step', 0) + 1
    
    return state


def ux_critique_agent(state, faiss_index, metadata, top_k=3):
    """
    Function 4.3: UX Critique Agent with RAG
    
    Args:
        state: Current analysis state
        faiss_index: FAISS index for RAG
        metadata: Pattern metadata
    
    Returns:
        dict: Updated state with ux_analysis
    """
    print("👤 Running UX Critique Agent...")
    
    # Retrieve UX patterns
    creative = state.get("creative_type", "")
    query = f"user experience usability accessibility heuristics {state['platform']} {creative}"
    patterns = retrieve_relevant_patterns(
        query, faiss_index, metadata, state['platform'], top_k=top_k
    )
    
    base_prompt = f"""You are a UX expert specializing in {state['platform']} {creative} design. Analyze this design for usability and user experience.

**EVALUATION CRITERIA:**

1. **USABILITY HEURISTICS (Nielsen's principles):**
   - Visibility of system status
   - User control and freedom
   - Consistency and standards
   - Error prevention
   - Recognition rather than recall

2. **ACCESSIBILITY (WCAG Standards):**
   - Text contrast ratios (minimum 4.5:1 for normal text)
   - Touch target sizes (minimum 44x44px)
   - Readability for screen readers
   - Color-blind friendly design

3. **INTERACTION PATTERNS:**
   - CTA (Call-to-Action) prominence and clarity
   - Navigation clarity
   - Information hierarchy
   - User flow intuitiveness

**REQUIRED JSON OUTPUT FORMAT:**
{{
    "overall_score": <0-100>,
    "usability": {{
        "score": <0-100>,
        "heuristic_violations": ["violation1", "violation2"],
        "findings": ["finding1", "finding2", "finding3"],
        "recommendations": ["rec1", "rec2", "rec3"]
    }},
    "accessibility": {{
        "score": <0-100>,
        "wcag_compliance": "<A/AA/AAA or Non-compliant>",
        "contrast_issues": ["issue1", "issue2"],
        "recommendations": ["rec1", "rec2"]
    }},
    "interaction_patterns": {{
        "score": <0-100>,
        "cta_effectiveness": <0-100>,
        "findings": ["finding1", "finding2"],
        "recommendations": ["rec1", "rec2"]
    }}
}}

Return ONLY valid JSON, no other text."""
    
    enhanced_prompt = augment_prompt_with_rag(base_prompt, patterns)
    result = call_openrouter_vision(state['image_base64'], enhanced_prompt, retries=3)
    
    state['ux_analysis'] = result
    state['current_step'] = state.get('current_step', 0) + 1
    
    return state


def market_research_agent(state, faiss_index, metadata, top_k=3):
    """
    Function 4.4: Market Research Agent with RAG
    
    Args:
        state: Current analysis state
        faiss_index: FAISS index for RAG
        metadata: Pattern metadata
    
    Returns:
        dict: Updated state with market_analysis
    """
    print("📈 Running Market Research Agent...")
    
    # Retrieve market patterns
    creative = state.get("creative_type", "")
    query = f"marketing trends engagement {state['platform']} {creative} target audience social media"
    patterns = retrieve_relevant_patterns(
        query, faiss_index, metadata, state['platform'], top_k=top_k
    )
    
    base_prompt = f"""You are a social media marketing analyst specializing in {state['platform']} {creative}. Analyze this design for market fit and engagement potential.

**EVALUATION CRITERIA:**

1. **PLATFORM OPTIMIZATION:**
   - Alignment with {state['platform']} best practices
   - Format compliance (dimensions, aspect ratio)
   - Platform-specific features utilization

2. **TREND ALIGNMENT:**
   - Current design trends (2024-2025)
   - Visual style relevance
   - Content type appropriateness

3. **TARGET AUDIENCE FIT:**
   - Demographic appeal (age, interests)
   - Messaging clarity and tone
   - Cultural relevance

4. **ENGAGEMENT POTENTIAL:**
   - Predicted engagement rate
   - Viral potential elements
   - Conversion optimization

**REQUIRED JSON OUTPUT FORMAT:**
{{
    "overall_score": <0-100>,
    "platform_optimization": {{
        "score": <0-100>,
        "format_compliance": ["aspect_ratio: X:Y", "dimensions: WxH"],
        "findings": ["finding1", "finding2"],
        "recommendations": ["rec1", "rec2"]
    }},
    "trend_analysis": {{
        "score": <0-100>,
        "aligned_trends": ["trend1", "trend2"],
        "missed_opportunities": ["opportunity1", "opportunity2"],
        "recommendations": ["rec1", "rec2"]
    }},
    "audience_fit": {{
        "score": <0-100>,
        "target_demographics": ["demographic1", "demographic2"],
        "messaging_effectiveness": <0-100>,
        "recommendations": ["rec1", "rec2"]
    }},
    "engagement_prediction": {{
        "estimated_engagement_rate": "X-Y%",
        "viral_potential": "<low/medium/high>",
        "conversion_factors": ["factor1", "factor2"],
        "optimization_tips": ["tip1", "tip2", "tip3"]
    }}
}}

Return ONLY valid JSON, no other text."""
    
    enhanced_prompt = augment_prompt_with_rag(base_prompt, patterns)
    result = call_openrouter_vision(state['image_base64'], enhanced_prompt, retries=3)
    
    state['market_analysis'] = result
    state['current_step'] = state.get('current_step', 0) + 1
    
    return state


def conversion_optimization_agent(state, faiss_index, metadata, top_k=3):
    """
    Function 4.5: Conversion/CTA Optimization Agent
    Focuses on action clarity, messaging, and funnel readiness.
    """
    print("🎯 Running Conversion Optimization Agent...")
    
    creative = state.get("creative_type", "")
    query = f"conversion optimization CTA clarity persuasive copy {state['platform']} {creative}"
    patterns = retrieve_relevant_patterns(
        query, faiss_index, metadata, state['platform'], top_k=top_k
    )
    
    base_prompt = f"""You are a conversion rate optimization specialist evaluating this {state['platform']} {creative} creative.

Focus on messaging clarity, CTA prominence, incentive strength, and friction removal.

REQUIRED JSON OUTPUT:
{{
  "overall_score": <0-100>,
  "cta": {{
    "score": <0-100>,
    "visibility": <0-100>,
    "clarity_findings": ["finding1","finding2"],
    "recommendations": ["rec1","rec2"]
  }},
  "copy": {{
    "score": <0-100>,
    "value_prop_strength": <0-100>,
    "findings": ["finding1","finding2"],
    "recommendations": ["rec1","rec2"]
  }},
  "funnel_fit": {{
    "score": <0-100>,
    "barriers": ["barrier1","barrier2"],
    "recommendations": ["rec1","rec2"]
  }}
}}

Return ONLY valid JSON."""
    
    enhanced_prompt = augment_prompt_with_rag(base_prompt, patterns)
    result = call_openrouter_vision(state['image_base64'], enhanced_prompt, retries=3)
    
    state['conversion_analysis'] = result
    state['current_step'] = state.get('current_step', 0) + 1
    
    return state


def brand_consistency_agent(state, faiss_index, metadata, top_k=3):
    """
    Function 4.6: Brand Consistency Agent
    Audits logo usage, palette, typography, tone, and layout against brand best practices.
    """
    print("🏷️ Running Brand Consistency Agent...")
    
    creative = state.get("creative_type", "")
    query = f"brand consistency visual identity logo typography palette tone {state['platform']} {creative}"
    patterns = retrieve_relevant_patterns(
        query, faiss_index, metadata, state['platform'], top_k=top_k
    )
    
    base_prompt = f"""You are a brand guardian evaluating this {state['platform']} {creative} asset for brand consistency.

Assess alignment to typical brand standards: logo use/clearspace, approved palette, typography families/weights, tone/voice, component styling, and imagery style.

REQUIRED JSON OUTPUT:
{{
  "overall_score": <0-100>,
  "logo_usage": {{
    "score": <0-100>,
    "issues": ["issue1","issue2"],
    "recommendations": ["rec1","rec2"]
  }},
  "palette_alignment": {{
    "score": <0-100>,
    "allowed_palette_match": ["#hex1","#hex2"],
    "off_brand_colors": ["#hexX"],
    "recommendations": ["rec1","rec2"]
  }},
  "typography_alignment": {{
    "score": <0-100>,
    "on_brand_fonts": ["font1"],
    "off_brand_fonts": ["fontX"],
    "recommendations": ["rec1","rec2"]
  }},
  "tone_voice": {{
    "score": <0-100>,
    "findings": ["finding1","finding2"],
    "recommendations": ["rec1","rec2"]
  }},
  "component_style": {{
    "score": <0-100>,
    "alignment_notes": ["note1","note2"],
    "recommendations": ["rec1","rec2"]
  }}
}}

Return ONLY valid JSON."""
    
    enhanced_prompt = augment_prompt_with_rag(base_prompt, patterns)
    result = call_openrouter_vision(state['image_base64'], enhanced_prompt, retries=3)
    
    state['brand_analysis'] = result
    state['current_step'] = state.get('current_step', 0) + 1
    
    return state
