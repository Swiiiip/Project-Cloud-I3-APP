import uvicorn
from dotenv import load_dotenv
from pathlib import Path

from src.persistence.challenge_storage.challenge_storage_factory import ChallengeStorageFactory
from src.services.game.app import create_app
from src.utils.logger_coonfigurator import LoggerConfigurator
from src.utils.path_handler import PathHandler
from src.utils.runtime_env import RuntimeEnv


def main() -> None:
    LoggerConfigurator.config_logger()
    load_dotenv(dotenv_path=PathHandler.dot_env(), override=False)

    backend = RuntimeEnv.require_str("CHALLENGE_STORAGE_BACKEND").strip().lower()
    if backend == "file":
        challenge_storage = ChallengeStorageFactory.create_file(Path(RuntimeEnv.require_str("CHALLENGE_STORAGE_FILE_PATH")))
    elif backend == "redis":
        challenge_storage = ChallengeStorageFactory.create_redis(
            host=RuntimeEnv.require_str("REDIS_HOST"),
            port=RuntimeEnv.require_int("REDIS_PORT"),
            db=RuntimeEnv.require_int("REDIS_DB"),
            ttl=RuntimeEnv.require_int("REDIS_TTL_SECONDS"),
        )
    elif backend == "in_memory":
        challenge_storage = ChallengeStorageFactory.create_in_memory()
    else:
        raise ValueError(f"Unsupported CHALLENGE_STORAGE_BACKEND '{backend}'")

    app = create_app(challenge_storage)
    uvicorn.run(
        app,
        host=RuntimeEnv.require_str("GAME_SERVICE_HOST"),
        port=RuntimeEnv.require_int("GAME_SERVICE_PORT"),
    )


if __name__ == "__main__":
    main()
