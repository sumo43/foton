"""Input/Output nodes for loading and saving images."""

from pathlib import Path
from typing import Any, Union, Optional
import json

from ..base import Node, NodeOutput
from ..image import Image


class Load(Node):
    """Node for loading images from file."""

    def __init__(self, path: Union[str, Path], **kwargs: Any) -> None:
        """Initialize Load node.

        Args:
            path: Path to image file
            **kwargs: Additional configuration
        """
        super().__init__(**kwargs)
        self.path = Path(path)

    def execute(self, **inputs: Any) -> NodeOutput:
        """Load image from file.

        Returns:
            NodeOutput with 'image' key containing loaded Image
        """
        if not self.path.exists():
            raise FileNotFoundError(f"Image file not found: {self.path}")

        image = Image(self.path)

        return NodeOutput(
            data={"image": image}, metadata={"source_path": str(self.path)}
        )


class Export(Node):
    """Node for exporting images to file."""

    def __init__(
        self, path: Union[str, Path], embed_recipe: bool = False, **kwargs: Any
    ) -> None:
        """Initialize Export node.

        Args:
            path: Output path for image file
            embed_recipe: Whether to embed processing recipe in metadata
            **kwargs: Additional configuration
        """
        super().__init__(**kwargs)
        self.path = Path(path)
        self.embed_recipe = embed_recipe

    def execute(self, **inputs: Any) -> NodeOutput:
        """Export image to file.

        Args:
            image: Image to export

        Returns:
            NodeOutput with 'path' key containing output path
        """
        image = self.get_input("image")
        if image is None:
            raise ValueError("No image provided for export")

        if not isinstance(image, Image):
            raise TypeError(f"Expected Image, got {type(image)}")

        # Ensure output directory exists
        self.path.parent.mkdir(parents=True, exist_ok=True)

        # Save image
        image.save(self.path)

        # Optionally embed recipe in metadata file
        metadata = {"output_path": str(self.path)}
        if self.embed_recipe:
            recipe_path = self.path.with_suffix(self.path.suffix + ".recipe.json")
            recipe_data = {
                "image_metadata": image.metadata,
                "processing_chain": "TODO: Add processing chain tracking",
            }
            with open(recipe_path, "w") as f:
                json.dump(recipe_data, f, indent=2)
            metadata["recipe_path"] = str(recipe_path)

        return NodeOutput(data={"image": image}, metadata=metadata)
