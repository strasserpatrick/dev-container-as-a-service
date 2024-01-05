import logging
from pathlib import Path

import yaml
from kubernetes import client, config
from kubernetes.client.rest import ApiException


class KubernetesService:
    pod_name: str = "vscode-host"

    def __init__(self, namespace: str = "dev"):
        self.namespace = namespace
        config.load_kube_config()
        self.v1 = client.CoreV1Api()

    def start(self, access_token: str, yaml_file_path: Path):
        try:
            self._store_access_token(access_token)  # if present, delete the secret?

            with open(yaml_file_path, "r") as file:
                pod_manifest = yaml.safe_load(file)

            # Create the Pod
            self.v1.create_namespaced_pod(body=pod_manifest, namespace=self.namespace)
            logging.info("Pod created successfully.")

        except ApiException as e:
            logging.error(f"Error creating Pod: {e}")

    def stop(self):
        try:
            self.v1.delete_namespaced_pod(self.pod_name, self.namespace)
            logging.info("Pod deleted successfully.")

        except ApiException as e:
            logging.error(f"Error deleting Pod: {e}")

    def logs(self):
        try:
            return self.v1.read_namespaced_pod_log(self.pod_name, self.namespace)
        except ApiException:
            logging.error("No logs found for Pod. Has it been started?")

    def _delete_secret(self, secret_name: str):
        try:
            self.v1.delete_namespaced_secret(secret_name, self.namespace)
            logging.debug(f"Secret {secret_name} deleted successfully.")

        except ApiException as e:
            logging.error(f"Error deleting Pod: {e}")

    def _store_access_token(self, access_token: str):
        secret_name: str = "github-access-token"
        self._delete_secret(secret_name)

        try:
            secret = client.V1Secret(
                metadata=client.V1ObjectMeta(name=secret_name),
                string_data={"access_token": access_token},
                type="Opaque",
            )

            self.v1.create_namespaced_secret(namespace=self.namespace, body=secret)
            logging.info(
                f"Secret {secret_name} created successfully in namespace {self.namespace}."  # noqa
            )

        except ApiException as e:
            logging.error(f"Error deleting Pod: {e}")
