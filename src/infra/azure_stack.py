from pathlib import Path

from cdktf import LocalBackend, TerraformStack
from cdktf_cdktf_provider_azurerm.provider import AzurermProvider
from cdktf_cdktf_provider_azurerm.resource_group import ResourceGroup
from constructs import Construct

from infra.config import InfraConfig


class AzureStack(TerraformStack):
    def __init__(self, scope: Construct, id: str, config: InfraConfig):
        super().__init__(scope, id)

        self.config = config

        self.configure_provider_and_backend()

        self.resource_group = ResourceGroup(
            scope=self,
            id_="devcontainers_rg",
            name=self.config.azure_resource_group_name,
            location=self.config.azure_location,
        )

    def configure_provider_and_backend(self):
        backend_file_path: Path = self.config.local_backend_path / "azure.tfstate"

        if not backend_file_path.exists():
            self.config.local_backend_path.mkdir(exist_ok=True)
            backend_file_path.touch()

        LocalBackend(
            scope=self,
            path=str(backend_file_path),
        )

        AzurermProvider(scope=self, id="azure_stack_provider", features={})
