from dataclasses import dataclass

@dataclass
class GithubParameters:
    client_id: str = "01ab8ac9400c4e429b23"
    grant_type: str = "urn:ietf:params:oauth:grant-type:device_code"
    login_url: str = "https://github.com/login/device/code"
    poll_url: str = "https://github.com/login/oauth/access_token"