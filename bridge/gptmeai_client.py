"""Read-only GPTMEAi HTTP client."""

import json
from urllib import error, request


class GPTMEAiReadOnlyClient:
    """Small standard-library client for GPTMEAi status endpoints only."""

    def __init__(self, base_url="http://127.0.0.1:8010", timeout=2.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _get_json(self, path):
        url = f"{self.base_url}/{path.lstrip('/')}"
        http_request = request.Request(url, headers={"Accept": "application/json"}, method="GET")
        try:
            with request.urlopen(http_request, timeout=self.timeout) as response:
                raw_body = response.read().decode("utf-8", errors="replace")
                try:
                    body = json.loads(raw_body) if raw_body else {}
                except json.JSONDecodeError:
                    body = {"text": raw_body}
                return {
                    "available": True,
                    "url": url,
                    "status_code": response.status,
                    "body": body,
                }
        except error.HTTPError as exc:
            raw_body = exc.read().decode("utf-8", errors="replace")
            try:
                body = json.loads(raw_body) if raw_body else {}
            except json.JSONDecodeError:
                body = {"text": raw_body}
            return {
                "available": False,
                "url": url,
                "status_code": exc.code,
                "error": str(exc),
                "body": body,
            }
        except (error.URLError, TimeoutError, OSError) as exc:
            return {
                "available": False,
                "url": url,
                "status_code": None,
                "error": str(exc),
                "body": {},
            }

    def health(self):
        return self._get_json("/health")

    def planner_status(self):
        return self._get_json("/planner/status")

    def execution_status(self):
        return self._get_json("/execution/status")
