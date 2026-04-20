import logging
from io import BytesIO

import requests
from PIL import ImageFilter
from PIL.Image import Image, open, Resampling

from src.config import Config

logger = logging.getLogger(__name__)


class ImageBlurProcessingService:
    def __init__(self):
        self._blur_scale = [scale**2 for scale in range(2, Config.DAILY_CHALLENGE_MAX_GUESSES+2)][::-1]
        logger.info("Blur scale set to : %s", self._blur_scale)

    def get_processed_image(self, image_url: str, blur_level: int) -> Image:
        logger.info("Processing image from %s for blur level %d", image_url, blur_level)
        img = self._fetch_image(image_url)
        processed_img = self._apply_game_effect(img, blur_level)
        return processed_img

    def get_original_image(self, image_url: str) -> Image:
        logger.info("Fetching original image from %s", image_url)
        return self._fetch_image(image_url)

    @staticmethod
    def _fetch_image(image_url: str) -> Image:
        response = requests.get(image_url, timeout=5)
        response.raise_for_status()
        return open(BytesIO(response.content)).convert("RGBA")

    def _apply_game_effect(self, img: Image, attempt_count: int) -> Image:
        try:
            blur_radius = self._blur_scale[attempt_count]
        except IndexError:
            blur_radius = 0
        if blur_radius == 0:
            return img
        pixel_size = max(1, blur_radius // 2)
        small = img.resize(
            (img.size[0] // pixel_size, img.size[1] // pixel_size),
            resample=Resampling.NEAREST
        )
        pixelated = small.resize(img.size, Resampling.NEAREST)
        return pixelated.filter(ImageFilter.GaussianBlur(radius=blur_radius))
