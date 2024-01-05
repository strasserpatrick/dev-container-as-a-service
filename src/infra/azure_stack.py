from pathlib import Path

from cdktf import LocalBackend, TerraformStack
from cdktf_cdktf_provider_azurerm.kubernetes_cluster import KubernetesCluster, KubernetesClusterDefaultNodePool
from cdktf_cdktf_provider_azurerm.provider import AzurermProvider
from cdktf_cdktf_provider_azurerm.resource_group import ResourceGroup
from cdktf_cdktf_provider_azurerm.storage_account import StorageAccount
from cdktf_cdktf_provider_azurerm.storage_container import StorageContainer
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

        (
            self.persistent_storage_account,
            self.persistent_storage_container,
        ) = self.create_storage()

        # self.kubernetes_cluster = self.create_kubernetes_cluster()

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

    def create_storage(self):
        persistent_storage_account = StorageAccount(
            scope=self,
            id_="devcontainers_sa",
            name="perssa4devcontainers",
            resource_group_name=self.resource_group.name,
            location=self.config.azure_location,
            account_replication_type="LRS",
            account_tier="Standard",
        )

        persistent_storage_container = StorageContainer(
            scope=self,
            id_="devcontainers_sc",
            name="vscodeuser",
            storage_account_name=persistent_storage_account.name,
            container_access_type="private",
        )

        return persistent_storage_account, persistent_storage_container

    def create_kubernetes_cluster(self):
        aks_cluster = KubernetesCluster(
            scope=self,
            id_="devcontainers_aks",
            name="aks",
            resource_group_name=self.config.azure_resource_group_name,
            location=self.config.azure_location,
            default_node_pool=KubernetesClusterDefaultNodePool(
                name="defaultnodepool",
                vm_size="Standard_D2_v2",
                node_count=1,
            ),
        )

        return aks_cluster
