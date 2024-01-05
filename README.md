# DevContainers

## Todos

- [ ] increase quotas and add gpu node pool
- [x] automate start and stop (and add read logs command)
- [ ] test and verify nvidia cuda and cudnn
- [ ] create infra repo and code

## Setup

### Docker Container

```bash
source .env
az acr login --name acr4devcontainers
docker build --platform=linux/amd64 -t dev-container-image  --build-arg STORAGE_ACCOUNT_NAME=$STORAGE_ACCOUNT_NAME  --build-arg STORAGE_ACCOUNT_KEY=$STORAGE_ACCOUNT_KEY --build-arg STORAGE_CONTAINER_NAME=$STORAGE_CONTAINER_NAME .

docker tag dev-container-image acr4devcontainers.azurecr.io/dcaas/dc:0.2.3
docker push acr4devcontainers.azurecr.io/dcaas/dc:0.2.3
```

### AKS Setup

```bash
az login
az account set --subscription <subscription_id>
aks get-credentials --resource-group <resource_group> --name <cluster_name>
kubelogin convert-kubeconfig -l azurecli
```

### Kubectl Control

```bash
kubectl create namespace <namespace>
kubectl apply -f <deployment_file> -n <namespace>
kubectl get pods -n <namespace>
kubectl exec -it <pod_name> -n <namespace> -- /bin/bash
```

add access token to kubernetes (secret is received by cli):

```bash
kubectl create secret generic github-access-token --from-literal=access_token=<access-token from cli> -n dev
```

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

## Considerations

- Container instances and container apps only allow 6 cpu cores. This is not enough for every case and not as flexible as aks.
- I could try to be presented as community project for microsoft
- A multi user scenario could be possible in aks with one namespace (and persistent storage) per user (or group). Users obviously only are allowed to run start and stop commands. This would be a nice feature for aks.
- Users could be allowed to push custom images in registry for custom images.
- Separation of concerns: admin maintains infra repo. Infra creates a namespace for each user in aad group (and a storage container). User communicates with api server and can start and stop his tunnel. Api server is responsible for fetching the users token and storage account key and starting the tunnel. When a new user is added to the aad group, infra needs to be updated. This could be done with a webhook. The api server could be a function app. For now, a single repo with a single user is enough. (then this could in something like a service)x

## Pseudocode

### Create (infra)

- create resource group
- aks cluster with gpu node pool (tags)
- storage account and container for persistent storage (add mounting)
- acr registry
- push image to acr registry
- aks namespace

TBD: Who sets kubectl config? I think the start command because we do not need a kubernetes provider then.

### Start

- oath device flow for auth token
- kubectl apply -f with the token and node selector to gpu machine and storage account values

### Stop

- kubectl delete -f

### Delete (infra)

- delete resource group (with az command, clean local backend. I think this is easier than terraform destroy)
