import time
import typer
import requests as r

from devcontainers.config import GithubParameters

app = typer.Typer()

@app.command()
def start():
    headers = {'Accept': 'application/json'}
    
    data = { "client_id": GithubParameters.client_id, "scope": "read:org"}

    res = r.post(GithubParameters.login_url, data=data, headers=headers).json()
    device_code = res['device_code']

    typer.echo("=" * 50)
    typer.echo("Please visit {} and enter code {}".format(res['verification_uri'], res['user_code']))
    typer.echo("=" * 50)

    data = {
        "client_id": GithubParameters.client_id,
        "device_code": device_code,
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code"
    }

    res = r.post(GithubParameters.poll_url, data=data, headers=headers).json()

    while 'error' in res:
        if res['error'] == 'authorization_pending':
            typer.echo("Waiting for authorization...")
        
            time.sleep(7)
            res = r.post(GithubParameters.poll_url, data=data, headers=headers).json()

        else:
            typer.echo("Error: {}".format(res['error']))
            break
    typer.echo("=" * 50)

    access_token = res['access_token']

    typer.echo("Access Token: {}".format(access_token))

    # TODO: now start kubernetes pod with access token as env variable


    
@app.command()
def stop():
    typer.echo("Goodbye World")


@app.command()
def logs():
    typer.echo("Hello World from logs")


if __name__ == "__main__":
    start()