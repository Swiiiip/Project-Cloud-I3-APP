from enum import StrEnum


class Network:
    BIND_HOST = "0.0.0.0"


class ServicePorts:
    GATEWAY = 8000
    GAME_ENGINE = 8010
    EMOJI_CATALOG = 8020
    EMOJI_RENDER = 8030
    FRONTEND = 8001
    GAME_STATE_STORAGE = 6379


class GameRules:
    DAILY_CHALLENGE_MAX_GUESSES = 5


class Http:
    INTERNAL_TIMEOUT_SECONDS = 30


class EmojiKitchen:
    METADATA_URL = "https://raw.githubusercontent.com/xsalazar/emoji-kitchen-backend/main/app/metadata.json"


class GameStateStorage:
    DB = 0
    TTL_SECONDS = 172800


class ChallengeStorageBackend(StrEnum):
    FILE = "file"
    GAME_STATE_STORAGE = "game_state_storage"
    IN_MEMORY = "in_memory"
