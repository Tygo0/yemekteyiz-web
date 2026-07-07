"""
The only place the automation package talks to the backend — always over
HTTPS/REST, never SQL, matching the architecture's hard rule.
"""
import requests
from automation.models import WeekImportPayload


class BackendClient:
    def __init__(self, base_url: str, username: str, password: str, timeout: float = 15.0):
        self.base_url = base_url.rstrip("/")
        self._username = username
        self._password = password
        self._timeout = timeout
        self._token = None

    def _login(self) -> None:
        resp = requests.post(
            f"{self.base_url}/api/auth/login",
            json={"username": self._username, "password": self._password},
            timeout=self._timeout,
        )
        resp.raise_for_status()
        self._token = resp.json()["access_token"]

    def _auth_headers(self) -> dict:
        if not self._token:
            self._login()
        return {"Authorization": f"Bearer {self._token}"}

    def get_week(self, week_id: int) -> dict | None:
        resp = requests.get(f"{self.base_url}/api/weeks/{week_id}", timeout=self._timeout)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    def list_contestants(self, week_id: int) -> list[dict]:
        resp = requests.get(
            f"{self.base_url}/api/contestants", params={"week_id": week_id}, timeout=self._timeout
        )
        resp.raise_for_status()
        return resp.json()

    def import_week(self, payload: WeekImportPayload) -> dict:
        resp = requests.post(
            f"{self.base_url}/api/automation/import",
            json=payload.to_api_dict(),
            headers=self._auth_headers(),
            timeout=self._timeout,
        )
        if resp.status_code == 401:
            # Token expired mid-run — re-login once and retry.
            self._login()
            resp = requests.post(
                f"{self.base_url}/api/automation/import",
                json=payload.to_api_dict(),
                headers=self._auth_headers(),
                timeout=self._timeout,
            )
        resp.raise_for_status()
        return resp.json()
