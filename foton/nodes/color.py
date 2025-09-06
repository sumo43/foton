"""Color processing nodes."""

from typing import Any, Union
from pathlib import Path
import numpy as np
from PIL import Image as PILImage, ImageEnhance

from ..base import Node, NodeOutput
from ..image import Image


class ColorGrade(Node):
    """Color grading node with LUT support."""
    
    def __init__(
        self, 
        lut: Union[str, Path, None] = None,
        intensity: float = 1.0,
        **kwargs: Any
    ) -> None:
        """Initialize ColorGrade node.
        
        Args:
            lut: Path to LUT file (.cube format) or None
            intensity: Intensity of the effect (0.0 to 1.0)
            **kwargs: Additional configuration
        """
        super().__init__(**kwargs)
        self.lut_path = Path(lut) if lut else None
        self.intensity = max(0.0, min(1.0, intensity))
        self._lut_data = None
        
        if self.lut_path:
            self._load_lut()
    
    def _load_lut(self) -> None:
        """Load LUT data from .cube file."""
        if not self.lut_path or not self.lut_path.exists():
            raise FileNotFoundError(f"LUT file not found: {self.lut_path}")
        
        # Placeholder LUT loading
        # In a real implementation, this would parse .cube files
        # For now, we'll create a simple identity LUT
        size = 32
        self._lut_data = np.linspace(0, 1, size)
    
    def _apply_lut(self, image: Image) -> Image:
        """Apply LUT to image."""
        if self._lut_data is None:
            return image
        
        # Placeholder LUT application
        # In a real implementation, this would perform 3D LUT interpolation
        img_array = np.array(image.pil, dtype=np.float32) / 255.0
        
        # Simple color grading effect (warm tone)
        if self.lut_path and "Kodak" in str(self.lut_path):
            img_array[:, :, 0] *= 1.1  # Slight red boost
            img_array[:, :, 2] *= 0.95  # Slight blue reduction
        
        # Apply intensity
        if self.intensity < 1.0:
            original = np.array(image.pil, dtype=np.float32) / 255.0
            img_array = original * (1 - self.intensity) + img_array * self.intensity
        
        img_array = np.clip(img_array * 255, 0, 255).astype(np.uint8)
        result_pil = PILImage.fromarray(img_array, mode=image.mode)
        
        return Image(result_pil, metadata=image.metadata.copy())
    
    def execute(self, **inputs: Any) -> NodeOutput:
        """Apply color grading to input image.
        
        Args:
            image: Input Image to color grade
            
        Returns:
            NodeOutput with 'image' containing color graded result
        """
        image = self.get_input("image")
        if image is None:
            raise ValueError("No image provided for color grading")
        
        if not isinstance(image, Image):
            raise TypeError(f"Expected Image, got {type(image)}")
        
        # Apply color grading
        if self.lut_path:
            result_image = self._apply_lut(image)
        else:
            # Simple color enhancement without LUT
            enhancer = ImageEnhance.Color(image.pil)
            enhanced_pil = enhancer.enhance(1.2)  # Slight saturation boost
            result_image = Image(enhanced_pil, metadata=image.metadata.copy())
        
        result_image.metadata.update({
            "color_graded": True,
            "lut": str(self.lut_path) if self.lut_path else None,
            "intensity": self.intensity
        })
        
        return NodeOutput(
            data={"image": result_image},
            metadata={
                "lut_path": str(self.lut_path) if self.lut_path else None,
                "intensity": self.intensity,
                "applied": True
            }
        )