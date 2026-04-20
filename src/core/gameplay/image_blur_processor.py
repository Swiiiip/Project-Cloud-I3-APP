import logging
from io import BytesIO

import requests
from PIL import ImageFilter
from PIL.Image import Image, open, Resampling
from numpy import linspace

logger = logging.getLogger(__name__)


class ImageBlurProcessingService:
    def __init__(self,
                 blur_levels: int):
        self._blur_scale = tuple(linspace(0, blur_levels ** 2, num=blur_levels).round().astype(int).tolist())
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

    def _apply_game_effect(self, img: Image, blur_level: int) -> Image:
        try:
            if blur_level >= len(self._blur_scale):
                blur_index = len(self._blur_scale) - 1
            else:
                blur_index = blur_level
            blur_radius = self._blur_scale[blur_index]
            logger.info("Applying blur effect with radius %d for blur level %d", blur_radius, blur_level)
        except IndexError:
            blur_radius = 0
        if blur_radius == 0:
            return img
        pixel_size = max(1, blur_radius // 2)
        small = img.resize(
            (img.size[0] // pixel_size, img.size[1] // pixel_size),
            resample=Resampling.NEAREST
        )
        blurred = small.resize(img.size, Resampling.NEAREST)
        return blurred.filter(ImageFilter.GaussianBlur(radius=blur_radius))
