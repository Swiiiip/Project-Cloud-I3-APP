import os
from pathlib import Path

from src.persistence.abstract_challenge_storage import AbstractChallengeStorage
from src.persistence.file_challenge_storage import FileChallengeStorage
from src.persistence.in_memory_challenge_storage import InMemoryChallengeStorage
from src.persistence.redis_challenge_storage import RedisChallengeStorage


class ChallengeStorageFactory:
    @staticmethod
    def create(root_dir: Path) -> AbstractChallengeStorage:
        backend = os.getenv("CHALLENGE_STORAGE_BACKEND", "file").strip().lower()

        if backend == "redis":
            return RedisChallengeStorage(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", "6379")),
                db=int(os.getenv("REDIS_DB", "0")),
                ttl=int(os.getenv("REDIS_TTL_SECONDS", "86400")),
            )

        if backend == "in_memory":
            return InMemoryChallengeStorage()

        return FileChallengeStorage(root_dir / "daily.json")

