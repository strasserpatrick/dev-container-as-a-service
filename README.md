# DevContainers

## Motivation

- "local feeling" with powerful (flexible) hardware (debugging, ide, no nano or vim)
- sudo permissions for full control (e.g. apt install libraries, cuda, ...)
- no "notebook like" feeling (preconfigured software, no shell)
- no VM because of inflexibility (os, hardware, ...)
- no heavy cluster setup time because of complexity

## Benefits

- no need to install anything locally (except vscode)
- cold-start setup time is around 5 minutes
- easily extensible
- warm start is around 1 minute (at most)
- pay per use (just storage costs at idle time)
- kubecl is hidden from end user

## Todos

- [x] automate start and stop (and add read logs command)
- [x] create infra repo and code
- [ ] add documentation for cli
- [ ] add readme tree
- [ ] refactor benefits and motivation section and considerations
- [ ] increase quotas and add gpu node pool
- [ ] test and verify nvidia cuda and cudnn

## Infra Setup

### Prerequisites

- Azure CLI
- Azure Subscription
- CDKTF ([installation guide](https://developer.hashicorp.com/terraform/tutorials/cdktf/cdktf-install?variants=cdk-language%3Apython))
- Poetry ([installation guide](https://python-poetry.org/docs/#installation))

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

## Considerations

- Container instances and container apps only allow 6 cpu cores. This is not enough for every case and not as flexible as aks.
- I could try to be presented as community project for microsoft
- A multi user scenario could be possible in aks with one namespace (and persistent storage) per user (or group). Users obviously only are allowed to run start and stop commands. This would be a nice feature for aks.
- Users could be allowed to push custom images in registry for custom images.
- Separation of concerns: admin maintains infra repo. Infra creates a namespace for each user in aad group (and a storage container). User communicates with api server and can start and stop his tunnel. Api server is responsible for fetching the users token and storage account key and starting the tunnel. When a new user is added to the aad group, infra needs to be updated. This could be done with a webhook. The api server could be a function app. For now, a single repo with a single user is enough. (then this could in something like a service)

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
