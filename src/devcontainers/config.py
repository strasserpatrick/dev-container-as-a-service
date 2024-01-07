from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class DevcontainerConfig(BaseSettings):
    devcontainer_kubeconfig_path: Optional[Path] = None
    devcontainer_registry_name: str
    devcontainer_repository_name: str = "dcaas"
    devcontainer_image_name: str = "dc"
    devcontainer_image_tag: str = "latest"


config = DevcontainerConfig()
