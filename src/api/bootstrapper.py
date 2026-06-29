from fastapi import FastAPI

from src.api.routes.daily_challenge_router import DailyChallengeRouter
from src.api.session.cookie_session_resolver import CookieSessionResolver
from src.persistence.challenge_storage.abstract_challenge_storage import AbstractChallengeStorage
from src.core.gameplay.image_blur_processor import ImageBlurProcessingService
from src.core.gameplay.daily_challenge import DailyChallengeService
from src.core.emoji.emoji_kitchen import EmojiKitchenService
from src.persistence.emoji_repository.file_emoji_repository import FileEmojiRepository
from src.utils.path_handler import PathHandler
from src.utils.runtime_env import RuntimeEnv


class BlurmojiApiBootstrapper:
    def __init__(self, challenge_storage: AbstractChallengeStorage):
        self._app = FastAPI(title="Blurmoji API")
        self._challenge_storage = challenge_storage

    def build(self) -> FastAPI:
        repo = FileEmojiRepository(PathHandler.root_dir() / "emojis.json")
        emoji_kitchen_service = EmojiKitchenService(repo)
        game_service = DailyChallengeService(emoji_kitchen_service, self._challenge_storage)
        image_blur_processor = ImageBlurProcessingService(blur_levels=RuntimeEnv.require_int("DAILY_CHALLENGE_MAX_GUESSES"))
        session_resolver = CookieSessionResolver()

        daily_router = DailyChallengeRouter(game_service,
                                            image_blur_processor,
                                            emoji_kitchen_service,
                                            session_resolver)
        self._app.include_router(daily_router.router)

        return self._app
