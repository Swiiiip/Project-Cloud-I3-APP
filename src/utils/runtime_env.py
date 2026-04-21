import os


class RuntimeEnv:
    @staticmethod
    def require_str(key: str) -> str:
        value = os.getenv(key)
        if value is None or not value.strip():
            raise ValueError(f"Missing required environment variable '{key}'")
        return value.strip()

    @staticmethod
    def require_int(key: str) -> int:
        value = RuntimeEnv.require_str(key)
        try:
            return int(value)
        except ValueError as exc:
            raise ValueError(f"Environment variable '{key}' must be an integer") from exc

