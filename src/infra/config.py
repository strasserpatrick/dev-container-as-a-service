from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

root_dir = Path(__file__).parent.parent.parent


class InfraConfig(BaseSettings):
    arm_tenant_id: str
    arm_subscription_id: str
    azure_location: str = "West Europe"
    azure_resource_group_name: str = "devcontainers"
    local_backend_path: Path = root_dir / ".terraform"


infra_config = InfraConfig()