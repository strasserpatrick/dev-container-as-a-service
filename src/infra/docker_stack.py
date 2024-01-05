from pathlib import Path

from cdktf import LocalBackend, TerraformStack
from cdktf_cdktf_provider_docker.provider import DockerProvider
from constructs import Construct

from infra.config import InfraConfig


class DockerStack(TerraformStack):
    def __init__(self, scope: Construct, id: str, config: InfraConfig):
        super().__init__(scope, id)

        self.config = config

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
        )
