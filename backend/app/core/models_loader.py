from __future__ import annotations
import os
from typing import Optional

from .nsfw_pipeline import NSFWSmartClassifier
from ..config import get_settings


class ModelRegistry:
    def __init__(self):
        self._loaded = False
        self.sd_pipeline = None
        self.img2img_pipeline = None
        self.upscaler = None
        self.video_model = None
        self.nsfw = None

    def load_all(self):
        if self._loaded:
            return self
        settings = get_settings()

        # Lazy imports to avoid heavy startup
        try:
            from diffusers import StableDiffusionPipeline, StableDiffusionImg2ImgPipeline
            import torch
        except Exception:
            StableDiffusionPipeline = None
            StableDiffusionImg2ImgPipeline = None
            torch = None

        try:
            from realesrgan import RealESRGAN
        except Exception:
            RealESRGAN = None

        # Load SD pipelines if available
        if StableDiffusionPipeline:
            device = "cuda" if torch and torch.cuda.is_available() else "cpu"
            self.sd_pipeline = StableDiffusionPipeline.from_pretrained(settings.SD_MODEL_ID)
            self.sd_pipeline = self.sd_pipeline.to(device)
            if StableDiffusionImg2ImgPipeline:
                self.img2img_pipeline = StableDiffusionImg2ImgPipeline.from_pretrained(settings.SD_INPAINT_MODEL_ID)
                self.img2img_pipeline = self.img2img_pipeline.to(device)

        # Load Real-ESRGAN if available
        if RealESRGAN:
            try:
                from PIL import Image
                import torch
                device = "cuda" if torch and torch.cuda.is_available() else "cpu"
                self.upscaler = RealESRGAN(device, scale=4)
                self.upscaler.load_weights(os.path.join(get_settings().MODELS_DIR, "realesrgan", "weights.pth"))
            except Exception:
                self.upscaler = None

        # Load video model placeholder (actual loading implemented in worker)
        self.video_model = None

        # NSFW smart classifier
        self.nsfw = NSFWSmartClassifier()

        self._loaded = True
        return self


registry = ModelRegistry()
