from cdktf import App

from infra.azure_stack import AzureStack
from infra.config import infra_config
from infra.docker_stack import DockerStack

if __name__ == "__main__":
    app = App()

    AzureStack(app, "azurestack", config=infra_config)
    # TODO: between azure stack and docker stack, acr registry config needs to be passed
    DockerStack(app, "dockerstack", config=infra_config)

    app.synth()
