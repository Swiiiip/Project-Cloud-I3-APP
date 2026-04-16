from fastapi import FastAPI

from src.api.routes.daily_challenge_router import DailyChallengeRouter
from src.core.service.emoji.emoji_data_population import EmojiDataPopulationService
from src.core.service.emoji.emoji_kitchen import EmojiKitchenService
from src.core.service.emoji.image_blur_processing import ImageBlurProcessingService
from src.core.service.gameplay.daily_challenge import DailyChallengeService
from src.persistence.file_emoji_repository import FileEmojiRepository
from src.utils.path_handler import PathHandler


class BlurmojiApiBootstrapper:
    def __init__(self):
        self.app = FastAPI(title="Emoji Kitchen Game")

        # 1. Infrastructure Layer
        self.repo = FileEmojiRepository(PathHandler.root_dir() / "emojis.json")

        # 2. Service Layer
        self.emoji_populator = EmojiDataPopulationService(self.repo).populate_repository()
        self.emoji_service = EmojiKitchenService(self.repo)
        self.image_service = ImageBlurProcessingService()
        self.game_service = DailyChallengeService(self.emoji_service)

        # 3. Routing Layer (Passing services via injection)
        self.daily_router = DailyChallengeRouter(self.game_service, self.image_service, self.emoji_service)

        self._setup_routes()

    def _setup_routes(self):
        self.app.include_router(self.daily_router.router)
