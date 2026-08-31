import base64
import io
from PIL import Image
import logging
from typing import Optional, Dict, Any, Tuple

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Utility class for processing images for multi-modal AI."""
    
    @staticmethod
    def encode_image_to_base64(image_data: bytes) -> str:
        """Convert image bytes to base64 string for API transmission."""
        return base64.b64encode(image_data).decode('utf-8')
    
    @staticmethod
    def resize_image_if_needed(image_data: bytes, max_size: Tuple[int, int] = (1024, 1024)) -> bytes:
        """Resize large images to reduce token usage."""
        try:
            img = Image.open(io.BytesIO(image_data))
            
            # Check if resize is needed
            if img.width > max_size[0] or img.height > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                buffer = io.BytesIO()
                img.save(buffer, format=img.format or 'PNG')
                return buffer.getvalue()
            
            return image_data
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return image_data
    
    @staticmethod
    def detect_image_type(image_data: bytes) -> str:
        """Detect if image is a screenshot, error dialog, or other."""
        try:
            img = Image.open(io.BytesIO(image_data))
            
            # Simple heuristic: check for UI elements
            # This is a simplified version; in production use a dedicated classifier
            width, height = img.size
            
            # Very wide/narrow images are likely UI elements
            aspect_ratio = width / height
            
            if 1.5 <= aspect_ratio <= 2.5:
                return "screenshot_desktop"
            elif 0.4 <= aspect_ratio <= 0.6:
                return "screenshot_mobile"
            else:
                return "screenshot_general"
                
        except Exception as e:
            logger.error(f"Error detecting image type: {e}")
            return "unknown"
    
    @staticmethod
    def extract_text_from_image(image_data: bytes) -> Optional[str]:
        """Use OCR to extract text from images (for non-Vision models)."""
        try:
            # This requires pytesseract
            # Install: pip install pytesseract pillow
            import pytesseract
            from PIL import Image
            import io
            
            img = Image.open(io.BytesIO(image_data))
            text = pytesseract.image_to_string(img)
            return text.strip() if text else None
            
        except ImportError:
            logger.warning("pytesseract not installed. Install for OCR capabilities.")
            return None
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return None