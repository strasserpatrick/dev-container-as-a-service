from cdktf import App

from infra.azure_stack import AzureStack
from infra.config import infra_config
from infra.docker_stack import DockerStack

if __name__ == "__main__":
    app = App()

    azure_stack = AzureStack(app, "azurestack", config=infra_config)
    storage_config = azure_stack.get_storage_configuration()
    registry_config = azure_stack.get_registry_configuration()

    DockerStack(
        app,
        "dockerstack",
        config=infra_config,
        storage_config=storage_config,
        registry_config=registry_config,
    )

    app.synth()
