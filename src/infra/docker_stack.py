from hashlib import sha1
from pathlib import Path

from cdktf import LocalBackend, TerraformStack
from cdktf_cdktf_provider_docker.image import Image, ImageBuild
from cdktf_cdktf_provider_docker.provider import (
    DockerProvider,
    DockerProviderRegistryAuth,
)
from cdktf_cdktf_provider_docker.registry_image import RegistryImage
from constructs import Construct

from infra.config import InfraConfig, RegistryConfig, StorageConfig, root_dir


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

        self.configure_provider_and_backend()
        self.build_and_push_image()

    def configure_provider_and_backend(self):
        backend_file_path: Path = (
            self.config.local_backend_path / "docker_stack" / "docker.tfstate"
        )

        if not backend_file_path.exists():
            backend_file_path.parent.mkdir(exist_ok=True, parents=True)
            backend_file_path.touch()

        LocalBackend(
            scope=self,
            path=str(backend_file_path),
        )

        DockerProvider(
            scope=self,
            id="docker_provider",
            registry_auth=[
                DockerProviderRegistryAuth(
                    address=self.registry_config.registry_url,
                    username=self.registry_config.registry_username,
                    password=self.registry_config.registry_pass,
                )
            ],
        )

    def build_and_push_image(self):
        container_name: str = "dc"
        image_name: str = f"{self.registry_config.registry_url}/{self.registry_config.registry_repository_name}/{container_name}:{self.config.docker_image_tag_version}"  # noqa

        devcontainers_code_dir = root_dir / "src" / "devcontainers"

        image = Image(
            scope=self,
            id="dc_image",
            name=image_name,
            build_attribute=ImageBuild(
                context=str(root_dir),
                platform="linux/amd64",
                build_args=self.storage_config.model_dump(),
            ),
            triggers={
                "src_code": str(
                    sha1(
                        "".join(
                            [
                                f.read_text()
                                for f in devcontainers_code_dir.glob("*")
                                if f.is_file() and f.suffix in [".py", ".yaml"]
                            ]
                        ).encode("utf-8")
                    )
                ),
                "dockerfile": str(
                    sha1((root_dir / "Dockerfile").read_text().encode("utf-8"))
                ),
            },
        )

        # registry image for pushing
        RegistryImage(
            scope=self,
            id_="dc_registry_image",
            name=image.name,
        )
