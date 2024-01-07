from pathlib import Path

from cdktf import LocalBackend, TerraformOutput, TerraformStack
from cdktf_cdktf_provider_azurerm.container_registry import ContainerRegistry
from cdktf_cdktf_provider_azurerm.kubernetes_cluster import (
    KubernetesCluster,
    KubernetesClusterDefaultNodePool,
    KubernetesClusterNetworkProfile,
)
from cdktf_cdktf_provider_azurerm.provider import AzurermProvider
from cdktf_cdktf_provider_azurerm.resource_group import ResourceGroup
from cdktf_cdktf_provider_azurerm.role_assignment import RoleAssignment
from cdktf_cdktf_provider_azurerm.storage_account import StorageAccount
from cdktf_cdktf_provider_azurerm.storage_container import StorageContainer
from constructs import Construct

from infra.config import InfraConfig, RegistryConfig, StorageConfig
from cdktf import Fn

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

        self.kubernetes_cluster = self.create_kubernetes_cluster()
        self.acr_registry = self.create_container_registry()

    def configure_provider_and_backend(self):
        backend_file_path: Path = (
            self.config.local_backend_path / "azure_stack" / "azure.tfstate"
        )

        if not backend_file_path.exists():
            backend_file_path.parent.mkdir(exist_ok=True, parents=True)
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
            resource_group_name=self.resource_group.name,
            location=self.config.azure_location,
            default_node_pool=KubernetesClusterDefaultNodePool(
                name="defnodepool",
                vm_size="Standard_D2_v2",
                node_count=1,
            ),
            automatic_channel_upgrade="patch",
            identity={"type": "SystemAssigned"},
            dns_prefix="dcaks",
            local_account_disabled=True,
            sku_tier="Free",
            azure_active_directory_role_based_access_control={
                "managed": True,
                "admin_group_object_ids": [self.config.aks_admin_group_id],
                "azure_rbac_enabled": False,
            },
            network_profile=KubernetesClusterNetworkProfile(
                network_plugin="kubenet",
                network_policy="calico",
            ),
        )

        TerraformOutput(
            scope=self,
            id="aks_kubeconfig",
            value=Fn.nonsensitive(aks_cluster.kube_config_raw),
        )

        return aks_cluster

    def create_container_registry(self):
        container_registry = ContainerRegistry(
            scope=self,
            id_="devcontainers_acr",
            name="acr4devcont",
            location=self.config.azure_location,
            resource_group_name=self.resource_group.name,
            sku="Basic",
            admin_enabled=True,
        )

        RoleAssignment(
            scope_=self,
            id_="acr_pull_aks",
            principal_id=self.kubernetes_cluster.kubelet_identity.object_id,
            scope=container_registry.id,
            role_definition_name="AcrPull",
        )

        return container_registry

    def get_storage_configuration(self) -> StorageConfig:
        return StorageConfig(
            storage_account_name=self.persistent_storage_account.name,
            storage_account_key=self.persistent_storage_account.primary_access_key,
            storage_container_name=self.persistent_storage_container.name,
        )

    def get_registry_configuration(self) -> RegistryConfig:
        return RegistryConfig(
            registry_url=self.acr_registry.login_server,
            registry_username=self.acr_registry.admin_username,
            registry_pass=self.acr_registry.admin_password,
        )
