"""AI-powered image processing nodes."""

from tkinter import W
from typing import Any, List, Optional
from io import BytesIO
import tempfile
import os
import requests
import numpy as np
from PIL import Image as PILImage

import base64
from io import BytesIO
from PIL import Image

import fal_client

from ..base import Node, NodeOutput
from ..image import Image


class Edit(Node):
    """Node that calls fal.ai nano-banana edit endpoint to edit images.

    If an input `image` is provided, it will be uploaded to fal storage.
    Alternatively, you can pass `image_urls` directly in the constructor.
    """

    def __init__(
        self,
        prompt: str,
        image_urls: Optional[List[str]] = None,
        with_logs: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.prompt = prompt
        self.image_urls = image_urls or []
        self.with_logs = with_logs

    def _on_queue_update(self, update: Any) -> None:
        try:
            if isinstance(update, fal_client.InProgress):
                for log in update.logs:
                    msg = log.get("message")
                    if msg:
                        print(msg)
        except Exception:
            pass

    def _ensure_urls(self) -> List[str]:
        urls: List[str] = list(self.image_urls)

        image = self.get_input("image")
        if image is not None and isinstance(image, Image):
            # Upload provided Image to fal storage
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp_path = tmp.name
            try:
                image.pil.save(tmp_path)
                uploaded_url = fal_client.upload_file(tmp_path)
                urls.append(uploaded_url)
            finally:
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass

        if not urls:
            raise ValueError("No images provided. Supply an input Image or image_urls.")

        return urls

    def _get_image_url(self, result: Any) -> Optional[str]:
        # Common fal result shapes
        if not isinstance(result, dict):
            return None

        # images as list of dicts or strings
        images = result.get("images")
        if isinstance(images, list) and images:
            first = images[0]
            if isinstance(first, str):
                return first
            if isinstance(first, dict):
                if "url" in first and isinstance(first["url"], str):
                    return first["url"]

        # single image dict or string
        image = result.get("image")
        if isinstance(image, str):
            return image
        if isinstance(image, dict):
            url = image.get("url")
            if isinstance(url, str):
                return url

        # sometimes nested under output key
        output = result.get("output")
        if isinstance(output, dict):
            return self._extract_first_image_url(output)

        return None

    def execute(self, **inputs: Any) -> NodeOutput:
        image = self.get_input("image")

        # save image.pil which is a pil image

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name
        image.pil.save(tmp_path)

        url = fal_client.upload_file(tmp_path)

        result = fal_client.subscribe(
            "fal-ai/nano-banana/edit",
            arguments={"prompt": self.prompt, "image_urls": [url]},
            with_logs=self.with_logs,
            on_queue_update=self._on_queue_update,
        )

        image_url = result.get("images")[0].get("url")

        print(image_url)

        resp = requests.get(image_url, timeout=15)
        resp.raise_for_status()
        pil = PILImage.open(BytesIO(resp.content)).convert("RGB")
        result_image = Image(pil, metadata={"source_url": image_url})
        result_image.metadata.update({"prompt": self.prompt, "model": "nano-banana"})

        return NodeOutput(
            data={"image": result_image},
            metadata={
                "endpoint": "fal-ai/nano-banana/edit",
                "prompt": self.prompt,
                "image_urls": [image_url],
                "result_image_url": image_url,
            },
        )
