from src.config.constants import ChallengeStorageBackend, GameRules, Network, ServicePorts
from src.config.loader import load_storage_settings
from src.config.settings import StorageSettings
from src.persistence.challenge_storage.abstract_challenge_storage import AbstractChallengeStorage
from src.persistence.challenge_storage.challenge_storage_factory import ChallengeStorageFactory
from src.services.game_engine.app import create_app
from src.utils.path_handler import PathHandler


class GameEngineBootstrap:
    @staticmethod
    def create_challenge_storage(storage: StorageSettings) -> AbstractChallengeStorage:
        backend = storage.backend
        if backend == ChallengeStorageBackend.FILE:
            return ChallengeStorageFactory.create_file(PathHandler.challenge_storage_file())
        if backend == ChallengeStorageBackend.GAME_STATE_STORAGE:
            host = storage.game_state_storage_host
            if host is None:
                raise ValueError("GAME_STATE_STORAGE_HOST is required when using game_state_storage backend")
            return ChallengeStorageFactory.create_game_state_storage(
                host=host,
                port=storage.game_state_storage_port,
                ttl=storage.game_state_ttl_seconds,
            )
        if backend == ChallengeStorageBackend.IN_MEMORY:
            return ChallengeStorageFactory.create_in_memory()
        raise ValueError(f"Unsupported challenge storage backend '{backend}'")

    @staticmethod
    def create_application():
        storage = load_storage_settings()
        challenge_storage = GameEngineBootstrap.create_challenge_storage(storage)
        return create_app(challenge_storage, max_attempts=GameRules.DAILY_CHALLENGE_MAX_GUESSES)

    @staticmethod
    def bind_host() -> str:
        return Network.BIND_HOST

    @staticmethod
    def bind_port() -> int:
        return ServicePorts.GAME_ENGINE
