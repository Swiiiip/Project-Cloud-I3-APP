from dataclasses import dataclass

from src.config.constants import ChallengeStorageBackend, GameStateStorage, ServicePorts


@dataclass(frozen=True)
class ServiceUrls:
    game_engine: str
    emoji_catalog: str
    emoji_render: str
    gateway: str


@dataclass(frozen=True)
class StorageSettings:
    backend: ChallengeStorageBackend
    game_state_storage_host: str | None = None

    @property
    def game_state_storage_port(self) -> int:
        return ServicePorts.GAME_STATE_STORAGE

    @property
    def game_state_ttl_seconds(self) -> int:
        return GameStateStorage.TTL_SECONDS
