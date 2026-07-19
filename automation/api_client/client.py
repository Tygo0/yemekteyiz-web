"""
The only place the automation package talks to the backend — always over
HTTPS/REST, never SQL, matching the architecture's hard rule.
"""
import requests
from automation.models import WeekImportPayload

# Matches AutomationFailureReportSchema.error_message's validate.Length(max=2000)
# in backend/app/schemas/automation_schema.py. A validator rejection with many
# errors (e.g. a bad extraction with dozens of missing-dish/score complaints)
# easily exceeds this, and an oversized message would otherwise 400 here —
# crashing the failure-reporting path itself and masking the real error.
MAX_ERROR_MESSAGE_LENGTH = 2000


def _truncate_error_message(message: str, max_length: int = MAX_ERROR_MESSAGE_LENGTH) -> str:
    if len(message) <= max_length:
        return message
    omitted = len(message) - max_length
    suffix = f"... [truncated, {omitted} more characters]"
    if len(suffix) >= max_length:
        return suffix[:max_length]
    return message[: max_length - len(suffix)] + suffix


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

    def report_failure(self, week_id: int, error_message: str, contestant_count: int = 0) -> dict:
        """
        Logs a failure the pipeline caught on its own side (validator
        rejection, vision refusal) so it still shows up in GET
        /automation/logs — without this, only failures the backend itself
        rejects (via /automation/import) would ever be visible there.
        """
        payload = {
            "week_id": week_id,
            "error_message": _truncate_error_message(error_message),
            "contestant_count": contestant_count,
        }
        resp = requests.post(
            f"{self.base_url}/api/automation/logs",
            json=payload,
            headers=self._auth_headers(),
            timeout=self._timeout,
        )
        if resp.status_code == 401:
            self._login()
            resp = requests.post(
                f"{self.base_url}/api/automation/logs",
                json=payload,
                headers=self._auth_headers(),
                timeout=self._timeout,
            )
        resp.raise_for_status()
        return resp.json()
