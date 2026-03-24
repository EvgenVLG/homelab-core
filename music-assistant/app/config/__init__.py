from .settings import Settings, settings


def load_config():
    return settings


__all__ = ["Settings", "settings", "load_config"]
