# DevContainers

Blueprint for Cloud setup of a development environment with Azure Kubernetes Service (AKS) and Azure Container Registry (ACR). The project is designed to be easily extensible and to provide a "local feeling" with powerful hardware. The project is in an early stage and is not yet ready for production use.

## Local Feeling

The project is designed to provide a "local feeling" with powerful hardware. This means that the user should be able to use the environment as if it was a local machine. This includes the following features:

- Open your code without copying within a few seconds
- Debugging with Visual Studio Code
- Full control over the environment (e.g. sudo permissions)
- No "notebook like" feeling (preconfigured software, no shell like in Colab)
- No VM because of overhead (os, hardware, ...)
- No heavy cluster setup time because of complexity

## VsCode Tunnel

No worries about ssh connections and copying your project files all along, just use the CLI to start your deployment pod with

```bash
python src/devcontainers/cli.py start
```

and register with your github account. After a few seconds, you can re-open your project with [VsCode Remote Tunnel](https://code.visualstudio.com/docs/remote/tunnels). And bam - you are in your cloud environment.

## Motivation

For a computer science lab, I needed a machine learning environment that exceeds my local compute power. Thus, I needed a cloud solution. For a couple of reasons, existing solutions did not fit my needs. One example being Google Colab with its "notebook" environment, that does not allow me to fully access the underlying environment. For example, it is very "hacky" to install alternative Python versions or libraries that are not preinstalled. Therefore, I decided to create my own solution and ruin my bank account in that process.

## Benefits

- easy setup (due to infrastructure as code)
- serverless pay-per-use (almost no idle costs)
- fast startup time (due to containerization)
- flexible hardware reqirements (due to kubernetes)
- local feeling (debugging, sudo, ...)

## Todos

- [x] automate start and stop (and add read logs command)
- [x] create infra repo and code
- [ ] separate in .env.infra and .env.dev and let script automatically generate .env.dev
- [ ] add documentation for cli
- [ ] increase quotas and add gpu node pool

## Infra Setup

### Prerequisites

- Azure CLI
- Azure Subscription
- CDKTF ([installation guide](https://developer.hashicorp.com/terraform/tutorials/cdktf/cdktf-install?variants=cdk-language%3Apython))
- Poetry ([installation guide](https://python-poetry.org/docs/#installation))
- Kubectl ([installation guide](https://kubernetes.io/docs/tasks/tools/))
- Kubelogin ([installation guide](https://azure.github.io/kubelogin/install.html))

### Steps

1. Find out your Azure tenant id and subscription id.
2. Create a Azure AD group for users that should get admin access to Azure Kubernetes Cluster (AKS). Copy the object id of the group.
3. Clone the repo and install dependencies:

    ```bash
    git clone https://github.com/strasserpatrick/devcontainers.git
    poetry install
    poetry shell # to activate virtual environment
    ```

4. Create a `.env` file in the root directory of the repo and add the following variables:

    ```bash
    export AZURE_TENANT_ID=<tenant_id>
    export AZURE_SUBSCRIPTION_ID=<subscription_id>
    export AKS_ADMIN_GROUP_ID=<group_id>
    ```

    It holds all configuration secrets. Other config parameters can be obtained and modified in `src/devcontainers/config.py`.

5. You can deploy the infrastructure with the following command:

    ```bash
    az login
    az account set --subscription <subscription_id> # if not already set
    make deploy
    ```

    Other useful commands for destroying and planning (`make synth`) the infrastructure are available in the `Makefile`.

6. (TODO: automate) Get credentials for AKS cluster and convert kubeconfig:

    ```bash
    az login
    az account set --subscription <subscription_id>
    az aks get-credentials --resource-group <resource_group> --name <cluster_name>
    kubelogin convert-kubeconfig -l azurecli
    ```

## Manual Setup

Instead of automatically deploying the infrastructure and using the cli for automation, the following section describes some manual steps to setup the infrastructure and deploy the container.

### Docker Container

Build and push image to Azure Container Registry (ACR):

```bash
source .env
az acr login --name <acr_registry_name>
docker build --platform=linux/amd64 -t dev-container-image  \
        --build-arg STORAGE_ACCOUNT_NAME=$STORAGE_ACCOUNT_NAME  \
        --build-arg STORAGE_ACCOUNT_KEY=$STORAGE_ACCOUNT_KEY \
        --build-arg STORAGE_CONTAINER_NAME=$STORAGE_CONTAINER_NAME .

docker tag dev-container-image <acr_registry_name>.azurecr.io/<repository_name>/<image_name>:<image_tag>
docker push <acr_registry_name>.azurecr.io/<repository_name>/<image_name>:<image_tag>
```

### AKS Setup

Get credentials for AKS cluster and convert kubeconfig (TODO: add this step to infra repo):

```bash
az login
az account set --subscription <subscription_id>
aks get-credentials --resource-group <resource_group> --name <cluster_name>
kubelogin convert-kubeconfig -l azurecli
```

### Kubectl Control

Create namespace and deploy container. This is done by cli in `src/devcontainers/cli.py`

```bash
kubectl create namespace <namespace>
kubectl apply -f <deployment_file> -n <namespace>
kubectl get pods -n <namespace>
kubectl exec -it <pod_name> -n <namespace> -- /bin/bash
```

Add access token to Kubernetes (look at `src/devcontainers/cli.py` for more information on how to receive the access token):

```bash
kubectl create secret generic github-access-token --from-literal=access_token=<access-token from cli> -n dev
```
