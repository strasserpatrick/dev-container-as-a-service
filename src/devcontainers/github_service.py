import logging
import time

import requests as r


class GithubService:
    client_id: str = "01ab8ac9400c4e429b23"
    grant_type: str = "urn:ietf:params:oauth:grant-type:device_code"
    scope: str = "read:org"

    login_url: str = "https://github.com/login/device/code"
    poll_url: str = "https://github.com/login/oauth/access_token"

    def __init__(self):
        self.headers = {"Accept": "application/json"}

    def get_device_code_with_url_and_usercode(self):
        data = {"client_id": self.client_id, "scope": self.scope}

        res = r.post(self.login_url, data=data, headers=self.headers).json()
        device_code = res["device_code"]

        return device_code, res["verification_uri"], res["user_code"]

    def access_token_polling(self, device_code):
        data = {
            "client_id": self.client_id,
            "device_code": device_code,
            "grant_type": self.grant_type,
        }

        res = r.post(self.poll_url, data=data, headers=self.headers).json()

        while "error" in res:
            if res["error"] == "authorization_pending":
                logging.info("Waiting for authorization...")

                time.sleep(7)
                res = r.post(self.poll_url, data=data, headers=self.headers).json()

            else:
                logging.error("Error: {}".format(res["error"]))
                break
        logging.info("=" * 50)

        access_token = res["access_token"]
        return access_token
