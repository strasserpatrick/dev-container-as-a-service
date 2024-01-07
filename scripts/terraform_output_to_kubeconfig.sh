#!/bin/bash

# This script will take the output of terraform output -json and create a kubeconfig file

# 1.step: extract kubeconfig from terraform output with the help of jq
jq -r '.azurestack.aks_kubeconfig' .terraform/output.json > $DEVCONTAINER_KUBECONFIG_PATH


# 2.step: convert with the help of kubelogin 
kubelogin convert-kubeconfig -l azurecli --kubeconfig $DEVCONTAINER_KUBECONFIG_PATH
