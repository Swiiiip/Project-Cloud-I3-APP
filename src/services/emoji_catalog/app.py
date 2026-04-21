from fastapi import FastAPI

from src.core.service.emoji_kitchen import EmojiKitchenService
from src.persistence.emoji_repository.file_emoji_repository import FileEmojiRepository
from src.utils.path_handler import PathHandler


class EmojiCatalogServiceApp:
    def __init__(self):
        repo = FileEmojiRepository(PathHandler.root_dir() / "emojis.json")
        self._emoji_service = EmojiKitchenService(repo)
        self._app = FastAPI(title="Blurmoji Emoji Catalog Service")
        self._register_routes()

    @property
    def app(self) -> FastAPI:
        return self._app

    def _register_routes(self) -> None:
        self._app.add_api_route("/internal/catalog/supported_emojis", self.get_supported_emojis, methods=["GET"])
        self._app.add_api_route("/internal/catalog/health", self.health, methods=["GET"])

    def get_supported_emojis(self) -> dict:
        categories = list(self._emoji_service.fetch_grouped_supported_emoji_payload())
        return {"categories": categories}

    @staticmethod
    def health() -> dict:
        return {"status": "ok"}


def create_app() -> FastAPI:
    return EmojiCatalogServiceApp().app

