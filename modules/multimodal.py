from typing import List, Optional
import base64
from io import BytesIO
from PIL import Image
from utils.logging import logger

class MultimodalHandler:
    """
    Handles processing of images and video inputs.
    """
    
    @staticmethod
    def process_image(image_file: BytesIO) -> str:
        """
        Convert an image file to a base64 string for LLM consumption.
        """
        try:
            # Open image to validate it
            img = Image.open(image_file)
            buffered = BytesIO()
            img.save(buffered, format="PNG") # standardized to PNG
            img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
            return f"data:image/png;base64,{img_b64}"
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return None

    @staticmethod
    def process_video_url(url: str) -> str:
        """
        Extract metadata or transcripts from video URLs (Placeholder).
        For a hackathon, we might just return the URL with a note.
        """
        # In a real app, use youtube-transcript-api
        return f"[VIDEO LINK: {url}] (Video processing requires external API/tool)"
