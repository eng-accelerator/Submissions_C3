# components/image_processing.py

"""
Component 2: Image Processing Module
Technology: PIL + CLIP + Base64
"""

import base64
from io import BytesIO
from PIL import Image
import torch
import clip
import numpy as np

# Load CLIP model (global, loaded once)
device = "cuda" if torch.cuda.is_available() else "cpu"
try:
    clip_model, clip_preprocess = clip.load("ViT-B/32", device=device)
    print(f"✅ CLIP model loaded on {device}")
except Exception as e:
    print(f"⚠️ Error loading CLIP: {e}")
    clip_model, clip_preprocess = None, None


def preprocess_image(uploaded_file):
    """
    Function 2.1: Convert uploaded file to PIL Image
    
    Args:
        uploaded_file: Streamlit UploadedFile object
    
    Returns:
        PIL.Image: Processed image (resized to max 1024x1024)
    """
    try:
        image = Image.open(uploaded_file)
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize for API efficiency (max 1024x1024)
        max_size = 1024
        if image.width > max_size or image.height > max_size:
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        return image
    except Exception as e:
        raise Exception(f"Error preprocessing image: {str(e)}")


def image_to_base64(pil_image):
    """
    Function 2.2: Convert PIL image to base64 string
    
    Args:
        pil_image: PIL.Image object
    
    Returns:
        str: Base64 encoded image string
    """
    try:
        buffered = BytesIO()
        pil_image.save(buffered, format="JPEG", quality=95)
        img_bytes = buffered.getvalue()
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        return img_base64
    except Exception as e:
        raise Exception(f"Error converting image to base64: {str(e)}")


def generate_clip_embedding(pil_image):
    """
    Function 2.3: Generate CLIP embedding for image
    
    Args:
        pil_image: PIL.Image object
    
    Returns:
        np.array: 512-dimensional CLIP embedding
    """
    if clip_model is None or clip_preprocess is None:
        print("⚠️ CLIP not loaded, returning zero vector")
        return np.zeros(512)
    
    try:
        image_input = clip_preprocess(pil_image).unsqueeze(0).to(device)
        
        with torch.no_grad():
            image_features = clip_model.encode_image(image_input)
            # Normalize for cosine similarity
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        
        return image_features.cpu().numpy()[0]
    except Exception as e:
        print(f"⚠️ Error generating CLIP embedding: {e}")
        return np.zeros(512)


def extract_image_metadata(pil_image):
    """
    Function 2.4: Extract technical image properties
    
    Args:
        pil_image: PIL.Image object
    
    Returns:
        dict: Image metadata (dimensions, format, aspect ratio, etc.)
    """
    try:
        return {
            "width": pil_image.width,
            "height": pil_image.height,
            "format": pil_image.format if pil_image.format else "JPEG",
            "mode": pil_image.mode,
            "aspect_ratio": round(pil_image.width / pil_image.height, 2)
        }
    except Exception as e:
        return {"error": str(e)}