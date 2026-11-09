import requests
import urllib3

# The self-hosted server uses a self-signed certificate.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

USERS_API = "/proxy/users/api/v2"


class UniFiApiClient:
    """Thin wrapper over the UniFi OS console REST API (one instance = one session)."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.verify = False

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        return self.session.request(method, f"{self.base_url}{path}", timeout=30, **kwargs)

    def login(self, username: str, password: str, otp: str = "") -> requests.Response:
        payload = {"username": username, "password": password, "rememberMe": False}
        if otp:
            payload["token"] = otp
        response = self._request("POST", "/api/auth/login", json=payload)
        csrf = response.headers.get("X-Updated-CSRF-Token") or response.headers.get("X-CSRF-Token")
        if csrf:
            self.session.headers["X-CSRF-Token"] = csrf
        return response

    def get_role_id(self, name: str = "Super Admin") -> str:
        roles = self._request("GET", f"{USERS_API}/roles").json()["data"]
        return next(role["unique_id"] for role in roles if role["name"] == name)

    def create_local_user(self, username: str, password: str, email: str, role_id: str) -> requests.Response:
        payload = {
            "first_name": "Auto",
            "last_name": "Test",
            "user_email": email,
            "username": username,
            "password": password,
            "only_local_account": True,
            "role_id": role_id,
            "group_ids": [],
            "force_add_nfc": True,
            "nfc_token": "",
            "pin_code": "",
        }
        return self._request("POST", f"{USERS_API}/user", json=payload)

    def list_users(self) -> list[dict]:
        return self._request("GET", f"{USERS_API}/users").json()["data"]

    def delete_user(self, user_id: str) -> requests.Response:
        """Active administrators can't be deleted, so deactivate first."""
        self._request("PUT", f"{USERS_API}/user/{user_id}/deactivate")
        return self._request("DELETE", f"{USERS_API}/user/{user_id}")

    def whoami(self) -> requests.Response:
        return self._request("GET", "/api/users/self")

    def logout(self) -> requests.Response:
        return self._request("POST", "/api/auth/logout")
