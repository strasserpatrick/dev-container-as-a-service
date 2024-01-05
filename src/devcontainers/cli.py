import logging
from functools import cache
from pathlib import Path

import typer

from devcontainers.github_service import GithubService
from devcontainers.kubernetes_service import KubernetesService

app = typer.Typer()

file_dir = Path(__file__).parent


@cache
def get_k8s_service():
    return KubernetesService()


@cache
def get_github_service():
    return GithubService()


@app.command(help="Github Authorization and starts the dev container")
def start(
    yaml_file: Path = typer.Option(
        file_dir / "vscode-host.yaml",
        help="Path to the YAML configuration file of pod deployment.",
    )
):
    gh_service = get_github_service()

    device_code, url, usercode = gh_service.get_device_code_with_url_and_usercode()

    typer.echo("=" * 50)
    typer.echo(f"Opening {url} in your browser...")
    typer.launch(url)
    typer.echo(f"Enter the code {usercode} in the browser.")
    typer.echo("=" * 50)

    logging.info("Device Code obtained")
    access_token = gh_service.access_token_polling(device_code)
    logging.info("Access Token obtained")

    k8s_service = get_k8s_service()
    k8s_service.start(access_token=access_token, yaml_file_path=yaml_file)


@app.command(help="Stops the dev container")
def stop():
    k8s_service = get_k8s_service()
    k8s_service.stop()


@app.command(help="Gets the logs of the dev container")
def logs():
    k8s_service = get_k8s_service()
    typer.echo(k8s_service.logs())


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
    app()


if __name__ == "__main__":
    main()
