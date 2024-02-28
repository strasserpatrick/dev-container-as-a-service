import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings


class DevcontainerConfig(BaseSettings):
    devcontainer_kubeconfig_path: Optional[Path] = None
    devcontainer_registry_name: str
    devcontainer_repository_name: str = "dcaas"
    devcontainer_image_name: str = "dc"
    devcontainer_image_tag: str = "latest"


def load_devcontainer_config() -> DevcontainerConfig:
    dotenv_devcontainers = os.environ["DEVCONTAINERS_CONFIG_PATH"]
    load_dotenv(dotenv_devcontainers)
    return DevcontainerConfig()


devcontainer_config = load_devcontainer_config()
