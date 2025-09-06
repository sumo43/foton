"""
EditGraph: A LangChain-style library for building image generation and editing pipelines.
"""

from .graph import Graph
from .image import Image
from . import nodes

__version__ = "0.1.0"
__all__ = ["Graph", "Image", "nodes"]