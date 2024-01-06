from pathlib import Path

from cdktf import LocalBackend, TerraformStack
from cdktf_cdktf_provider_docker.provider import (
    DockerProvider,
    DockerProviderRegistryAuth,
)
from constructs import Construct

from infra.config import InfraConfig, RegistryConfig, StorageConfig


class DockerStack(TerraformStack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        config: InfraConfig,
        registry_config: RegistryConfig,
        storage_config: StorageConfig,
    ):
        super().__init__(scope, id)

        self.config = config
        self.registry_config = registry_config
        self.storage_config = storage_config

    def configure_provider_and_backend(self):
        backend_file_path: Path = self.config.local_backend_path / "docker.tfstate"

        if not backend_file_path.exists():
            self.config.local_backend_path.mkdir(exist_ok=True)
            backend_file_path.touch()

        LocalBackend(
            scope=self,
            path=str(backend_file_path),
        )

        DockerProvider(
            scope=self,
            id_="docker_provider",
            registry_auth=[
                DockerProviderRegistryAuth(
                    address=self.registry_config.registry_url,
                    username="admin",
                    password=self.registry_config.registry_pass,
                )
            ],
        )
