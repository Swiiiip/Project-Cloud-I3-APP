from pathlib import Path


class PathHandler:
    src_dir = Path(__file__).parent.parent

    @classmethod
    def root_dir(cls) -> Path:
        return cls.src_dir.parent

    @classmethod
    def data_dir(cls) -> Path:
        return cls.root_dir() / "data"

    @classmethod
    def emojis_file(cls) -> Path:
        return cls.data_dir() / "emojis.json"

    @classmethod
    def challenge_storage_file(cls) -> Path:
        return cls.data_dir() / "challenge_storage.json"
