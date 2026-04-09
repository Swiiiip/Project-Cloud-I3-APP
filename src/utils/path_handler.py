from pathlib import Path


class PathHandler:
    src_dir = Path(__file__).parent.parent

    @classmethod
    def dot_env(cls) -> Path:
        return cls.src_dir.parent / ".env"

    @classmethod
    def cache_file(cls) -> Path:
        return cls.src_dir.parent / ".game_state"

    @classmethod
    def root_dir(cls) -> Path:
        return cls.src_dir.parent
