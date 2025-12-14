"""
Multi-Design Comparison System
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from components.agents import call_openrouter_vision
from components.rag_system import retrieve_relevant_patterns, augment_prompt_with_rag
import json


def compare_multiple_designs(designs_data, faiss_index, metadata, platform):
    """
    Compare 2-5 designs side by side
    
    Args:
        designs_data: List of dicts with {name, image_base64, embedding}
        faiss_index: FAISS index
        metadata: Pattern metadata
        platform: Target platform
    
    Returns:
        dict: Comprehensive comparison report
    """
    num_designs = len(designs_data)
    
    if num_designs < 2:
        return {"error": "Need at least 2 designs to compare"}
    
    if num_designs > 5:
        designs_data = designs_data[:5]  # Limit to 5
        num_designs = 5
    
    print(f"🔄 Comparing {num_designs} designs...")
    
    # Retrieve relevant comparison patterns
    query = f"design comparison A/B testing best practices {platform}"
    patterns = retrieve_relevant_patterns(query, faiss_index, metadata, platform, top_k=5)
    
    # Build comparison prompt
    design_descriptions = []
    for i, design in enumerate(designs_data, 1):
        design_descriptions.append(f"Design {chr(64+i)} ({design['name']})")
    
    base_prompt = f"""You are a design comparison expert. Compare these {num_designs} designs for {platform}.

DESIGNS TO COMPARE:
{', '.join(design_descriptions)}

EVALUATION FRAMEWORK:

1. **RELATIVE SCORING** (0-100 for each design on each criterion):
   - Visual Design Quality
   - User Experience
   - Market/Platform Fit
   - Brand Consistency
   - Conversion Potential

2. **HEAD-TO-HEAD COMPARISON:**
   - What are the key differences?
   - Which design elements work better in each?
   - What makes one design stronger than another?

3. **RANKING:**
   - Rank designs from best to worst
   - Explain the reasoning for ranking

4. **SYNTHESIS RECOMMENDATION:**
   - Can we combine best elements from multiple designs?
   - What would the "ideal" hybrid design look like?

5. **A/B TEST RECOMMENDATIONS:**
   - Which designs should be A/B tested?
   - What specific elements to test?
   - Predicted winner and confidence level

REQUIRED JSON OUTPUT:
{{
    "overall_ranking": ["Design A", "Design B", ...],
    "winner": "Design X",
    "confidence": "high/medium/low",
    
    "relative_scores": {{
        "Design A": {{
            "visual": 0-100,
            "ux": 0-100,
            "market": 0-100,
            "brand": 0-100,
            "conversion": 0-100,
            "overall": 0-100
        }},
        "Design B": {{ ... }}
    }},
    
    "key_differences": [
        {{
            "aspect": "color_palette",
            "Design A": "description",
            "Design B": "description",
            "winner": "Design A",
            "reason": "why A wins"
        }}
    ],
    
    "strengths": {{
        "Design A": ["strength1", "strength2"],
        "Design B": ["strength1", "strength2"]
    }},
    
    "weaknesses": {{
        "Design A": ["weakness1", "weakness2"],
        "Design B": ["weakness1", "weakness2"]
    }},
    
    "synthesis_recommendation": {{
        "strategy": "combine/choose/test",
        "description": "Take X from Design A, Y from Design B...",
        "implementation_steps": ["step1", "step2"],
        "expected_improvement": "+X% over best individual design"
    }},
    
    "ab_test_plan": {{
        "recommended_test": "Design A vs Design B",
        "test_duration": "X days",
        "sample_size": "Y users",
        "key_metrics": ["metric1", "metric2"],
        "predicted_winner": "Design X",
        "confidence_level": 0.0-1.0,
        "elements_to_test": ["element1", "element2"]
    }}
}}

Return ONLY valid JSON."""
    
    # Augment with RAG
    enhanced_prompt = augment_prompt_with_rag(base_prompt, patterns)
    
    # Create multi-image message for API
    content = [{"type": "text", "text": enhanced_prompt}]
    
    for design in designs_data:
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{design['image_base64']}"
            }
        })
    
    # Call vision API with multiple images
    try:
        import requests
        import os
        
        headers = {
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "HTTP-Referer": os.getenv("SITE_URL", "http://localhost:8501"),
            "X-Title": os.getenv("APP_NAME", "DesignAnalysisPoc"),
            "Content-Type": "application/json"
        }
        
        data = {
            "model": os.getenv("VISION_MODEL", "openai/gpt-4o"),
            "messages": [{"role": "user", "content": content}],
            "max_tokens": 3000,
            "temperature": 0.7,
            "response_format": {"type": "json_object"}
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=90
        )
        
        if response.status_code == 200:
            try:
                result = response.json()
            except ValueError:
                return {"error": "Invalid JSON response from API", "raw_content": response.text}
            choices = result.get("choices", [])
            if not choices:
                return {"error": "Empty response from model", "raw_response": result}
            content_str = choices[0].get("message", {}).get("content", "")
            if not content_str:
                return {"error": "Empty content from model", "raw_response": result}
            try:
                comparison_result = json.loads(content_str)
            except json.JSONDecodeError:
                return {"error": "Invalid JSON in model content", "raw_content": content_str, "raw_response": result}
            
            # Add metadata
            comparison_result['num_designs_compared'] = num_designs
            comparison_result['platform'] = platform
            comparison_result['design_names'] = [d['name'] for d in designs_data]
            
            return comparison_result
        else:
            try:
                details = response.json()
            except ValueError:
                details = response.text
            return {"error": f"API error: {response.status_code}", "details": details}
    
    except Exception as e:
        return {"error": str(e)}


def generate_side_by_side_comparison_image(designs_data, comparison_result):
    """
    Create visual side-by-side comparison
    
    Args:
        designs_data: List of design dicts
        comparison_result: Comparison analysis result
    
    Returns:
        PIL.Image: Combined comparison image
    """
    num_designs = len(designs_data)
    
    # Decode base64 images
    images = []
    for design in designs_data:
        img_data = base64.b64decode(design['image_base64'])
        img = Image.open(io.BytesIO(img_data))
        images.append(img)
    
    # Standardize sizes
    target_width = 400
    resized_images = []
    for img in images:
        aspect_ratio = img.height / img.width
        new_height = int(target_width * aspect_ratio)
        resized = img.resize((target_width, new_height), Image.Resampling.LANCZOS)
        resized_images.append(resized)
    
    max_height = max(img.height for img in resized_images)
    
    # Create combined image
    combined_width = target_width * num_designs + 20 * (num_designs - 1)
    combined_height = max_height + 100  # Extra space for labels
    
    combined = Image.new('RGB', (combined_width, combined_height), 'white')
    draw = ImageDraw.Draw(combined)
    
    # Paste images side by side
    x_offset = 0
    for i, img in enumerate(resized_images):
        combined.paste(img, (x_offset, 80))
        
        # Add label
        design_name = designs_data[i]['name']
        ranking = comparison_result.get('overall_ranking', [])
        rank = ranking.index(design_name) + 1 if design_name in ranking else i + 1
        
        label = f"#{rank} - {design_name}"
        
        # Draw label background
        bbox = draw.textbbox((0, 0), label)
        text_width = bbox[2] - bbox[0]
        text_x = x_offset + (target_width - text_width) // 2
        
        draw.rectangle([text_x - 10, 20, text_x + text_width + 10, 60], fill='darkblue')
        draw.text((text_x, 30), label, fill='white')
        
        # Add score
        scores = comparison_result.get('relative_scores', {}).get(design_name, {})
        overall_score = scores.get('overall', 0)
        score_text = f"Score: {overall_score}/100"
        draw.text((x_offset + 10, max_height + 85), score_text, fill='black')
        
        x_offset += target_width + 20
    
    return combined


def calculate_design_similarity(embedding1, embedding2):
    """
    Calculate cosine similarity between two design embeddings
    
    Args:
        embedding1: First CLIP embedding
        embedding2: Second CLIP embedding
    
    Returns:
        float: Similarity score (0-1)
    """
    emb1 = np.array(embedding1)
    emb2 = np.array(embedding2)
    
    # Cosine similarity
    similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
    
    return float(similarity)


def generate_similarity_matrix(designs_data):
    """
    Create similarity matrix for all designs
    
    Args:
        designs_data: List of design dicts with embeddings
    
    Returns:
        dict: Similarity matrix and analysis
    """
    num_designs = len(designs_data)
    similarity_matrix = np.zeros((num_designs, num_designs))
    
    for i in range(num_designs):
        for j in range(num_designs):
            if i == j:
                similarity_matrix[i][j] = 1.0
            else:
                sim = calculate_design_similarity(
                    designs_data[i]['embedding'],
                    designs_data[j]['embedding']
                )
                similarity_matrix[i][j] = sim
    
    # Find most similar and most different pairs
    max_sim = 0
    min_sim = 1
    most_similar_pair = None
    most_different_pair = None
    
    for i in range(num_designs):
        for j in range(i + 1, num_designs):
            sim = similarity_matrix[i][j]
            if sim > max_sim:
                max_sim = sim
                most_similar_pair = (designs_data[i]['name'], designs_data[j]['name'])
            if sim < min_sim:
                min_sim = sim
                most_different_pair = (designs_data[i]['name'], designs_data[j]['name'])
    
    return {
        "similarity_matrix": similarity_matrix.tolist(),
        "design_names": [d['name'] for d in designs_data],
        "most_similar_pair": {
            "designs": most_similar_pair,
            "similarity": round(max_sim, 3)
        },
        "most_different_pair": {
            "designs": most_different_pair,
            "similarity": round(min_sim, 3)
        },
        "average_similarity": round(np.mean(similarity_matrix[np.triu_indices(num_designs, k=1)]), 3)
    }
