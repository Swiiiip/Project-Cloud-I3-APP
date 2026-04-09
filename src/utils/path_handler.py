from pathlib import Path


class PathHandler:
    src_dir = Path(__file__).parent.parent

    @classmethod
    def dot_env(cls) -> Path:
        return cls.src_dir.parent / ".env"

    @classmethod
    def cache_dir(cls) -> Path:
        return cls.src_dir.parent / ".game_state"
