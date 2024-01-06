from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings

load_dotenv()

root_dir = Path(__file__).parent.parent.parent


class RegistryConfig(BaseModel):
    registry_url: str
    registry_username: str
    registry_pass: str
    registry_repository_name: str = "dcaas"


class StorageConfig(BaseModel):
    storage_account_name: str
    storage_account_key: str
    storage_container_name: str = "vscodeuser"


class InfraConfig(BaseSettings):
    arm_tenant_id: str
    arm_subscription_id: str
    azure_location: str = "West Europe"
    azure_resource_group_name: str = "devcontainers"
    aks_admin_group_id: str
    local_backend_path: Path = root_dir / ".terraform"
    docker_image_tag_version: str = "0.0.1"


infra_config = InfraConfig()
