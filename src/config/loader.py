from pathlib import Path

from dotenv import load_dotenv

from src.config.constants import ChallengeStorageBackend
from src.config.settings import ServiceUrls, StorageSettings
from src.utils.runtime_env import RuntimeEnv

_DOTENV_LOADED = False


def _ensure_dotenv() -> None:
    global _DOTENV_LOADED
    if _DOTENV_LOADED:
        return
    project_root = Path(__file__).resolve().parents[2]
    load_dotenv(dotenv_path=project_root / ".env", override=False)
    _DOTENV_LOADED = True


def load_service_urls() -> ServiceUrls:
    _ensure_dotenv()
    return ServiceUrls(
        game_engine=RuntimeEnv.require_str("GAME_ENGINE_SERVICE_BASE_URL"),
        emoji_catalog=RuntimeEnv.require_str("EMOJI_CATALOG_SERVICE_BASE_URL"),
        emoji_render=RuntimeEnv.require_str("EMOJI_RENDER_SERVICE_BASE_URL"),
        gateway=RuntimeEnv.require_str("API_BASE_URL"),
    )


def load_game_engine_service_base_url() -> str:
    _ensure_dotenv()
    return RuntimeEnv.require_str("GAME_ENGINE_SERVICE_BASE_URL")


def load_api_base_url() -> str:
    _ensure_dotenv()
    return RuntimeEnv.require_str("API_BASE_URL")


def load_session_cookie_secret() -> str:
    _ensure_dotenv()
    return RuntimeEnv.require_str("SESSION_COOKIE_SECRET")


def load_storage_settings() -> StorageSettings:
    _ensure_dotenv()
    backend_raw = RuntimeEnv.require_str("CHALLENGE_STORAGE_BACKEND").strip().lower()
    backend = ChallengeStorageBackend(backend_raw)

    storage_host: str | None = None
    if backend == ChallengeStorageBackend.GAME_STATE_STORAGE:
        storage_host = RuntimeEnv.require_str("GAME_STATE_STORAGE_HOST")

    return StorageSettings(backend=backend, game_state_storage_host=storage_host)
