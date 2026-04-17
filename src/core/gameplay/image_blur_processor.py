import logging
import requests
from io import BytesIO
from PIL import ImageFilter
from PIL.Image import Image, open, Resampling
from typing import Optional

from src.config import Config

logger = logging.getLogger(__name__)


class ImageBlurProcessingService:
    def __init__(self):
        self._blur_scale = [scale**2 for scale in range(2, Config.DAILY_CHALLENGE_MAX_GUESSES+2)][::-1]
        logger.info("Blur scale set to : %s", self._blur_scale)

    def get_processed_image(self, image_url: str, attempt_count: int) -> Optional[BytesIO]:
        try:
            logger.info("Processing image from %s for attempt %d", image_url, attempt_count)
            response = requests.get(image_url, timeout=5)
            response.raise_for_status()

            img = open(BytesIO(response.content)).convert("RGBA")
            processed_img = self._apply_game_effect(img, attempt_count)
            img_byte_arr = BytesIO()
            processed_img.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            return img_byte_arr

        except Exception as e:
            logger.error("Failed to process image: %s", e)
            return None

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


if __name__ == '__main__':
    from src.utils.logger_coonfigurator import LoggerConfigurator
    from src.utils.path_handler import PathHandler
    LoggerConfigurator.config_logger()

    image_url = r"https://www.gstatic.com/android/keyboard/emojikitchen/20201001/u2665-ufe0f/u2665-ufe0f_u2615.png"
    service = ImageBlurProcessingService(max_attempts=5)
    for attempt in range(5):
        image_bytes = service.get_processed_image(image_url, attempt)
        processed_image = PathHandler.src_dir / f"blurred_image_{attempt}.png"
        with processed_image.open("wb") as f:
            f.write(image_bytes.getbuffer())
