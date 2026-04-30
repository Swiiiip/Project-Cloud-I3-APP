from pathlib import Path

from src.persistence.challenge_storage.abstract_challenge_storage import AbstractChallengeStorage
from src.persistence.challenge_storage.file_challenge_storage import FileChallengeStorage
from src.persistence.challenge_storage.in_memory_challenge_storage import InMemoryChallengeStorage
from src.persistence.challenge_storage.redis_challenge_storage import RedisChallengeStorage


class ChallengeStorageFactory:
    @staticmethod
    def create_file(file_path: Path) -> AbstractChallengeStorage:
        return FileChallengeStorage(file_path)

    @staticmethod
    def create_redis(host: str, port: int, db: int, ttl: int) -> AbstractChallengeStorage:
        return RedisChallengeStorage(host=host, port=port, db=db, ttl=ttl)

    @staticmethod
    def create_in_memory() -> AbstractChallengeStorage:
        return InMemoryChallengeStorage()


