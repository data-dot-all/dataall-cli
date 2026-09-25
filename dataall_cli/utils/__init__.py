"""data.all cli utils."""

from dataall_core.discovery import discover_from_frontend, frontend_origin

from .config import load_config, save_config

__all__ = ["discover_from_frontend", "frontend_origin", "load_config", "save_config"]
