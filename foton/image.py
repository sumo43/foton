"""Image data structures and utilities."""

from typing import Optional, Union, Any
from pathlib import Path
import numpy as np
from PIL import Image as PILImage


class Image:
    """Represents an image in the EditGraph pipeline."""
    
    def __init__(
        self,
        data: Union[PILImage.Image, np.ndarray, str, Path],
        metadata: Optional[dict] = None
    ) -> None:
        """Initialize an Image.
        
        Args:
            data: Image data as PIL Image, numpy array, or file path
            metadata: Optional metadata dictionary
        """
        self.metadata = metadata or {}
        
        if isinstance(data, (str, Path)):
            self._pil_image = PILImage.open(data)
        elif isinstance(data, PILImage.Image):
            self._pil_image = data
        elif isinstance(data, np.ndarray):
            self._pil_image = PILImage.fromarray(data)
        else:
            raise ValueError(f"Unsupported image data type: {type(data)}")
    
    @property
    def pil(self) -> PILImage.Image:
        """Get PIL Image representation."""
        return self._pil_image
    
    @property
    def numpy(self) -> np.ndarray:
        """Get numpy array representation."""
        return np.array(self._pil_image)
    
    @property
    def size(self) -> tuple[int, int]:
        """Get image size as (width, height)."""
        return self._pil_image.size
    
    @property
    def mode(self) -> str:
        """Get image mode (RGB, RGBA, etc.)."""
        return self._pil_image.mode
    
    def save(self, path: Union[str, Path]) -> None:
        """Save image to file."""
        self._pil_image.save(path)
    
    def copy(self) -> "Image":
        """Create a copy of the image."""
        return Image(self._pil_image.copy(), self.metadata.copy())
    
    def __repr__(self) -> str:
        return f"Image(size={self.size}, mode={self.mode})"