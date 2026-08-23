"""Optional live read-only GPTMEAi status check."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import time
from urllib import error, request


ALLOWED_ENDPOINTS = (
    "/health",
    "/planner/status",
    "/execution/status",
)

DEFAULT_BASE_URL = "http://127.0.0.1:8010"
DEFAULT_TIMEOUT_SECONDS = 2.0
REPORT_FILENAME = "GPTMEAI_LIVE_READONLY_STATUS_REPORT.md"


def project_root():
    return Path(__file__).resolve().parents[1]


def report_path(root):
    return Path(root) / "reports" / "codex" / REPORT_FILENAME


def _utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _shape_summary(body):
    if isinstance(body, dict):
        return {
            "body_type": "object",
            "top_level_keys": sorted(str(key) for key in body.keys()),
        }
    if isinstance(body, list):
        return {
            "body_type": "array",
            "top_level_keys": [],
        }
    return {
        "body_type": type(body).__name__,
        "top_level_keys": [],
    }


def _parse_json(raw_body):
    if not raw_body:
        return {}, False
    try:
        return json.loads(raw_body), False
    except json.JSONDecodeError:
        return None, True


def check_endpoint(base_url, endpoint, timeout):
    if endpoint not in ALLOWED_ENDPOINTS:
        raise ValueError(f"Endpoint is not allowed: {endpoint}")

    url = f"{base_url.rstrip('/')}{endpoint}"
    started = time.perf_counter()
    http_request = request.Request(
        url,
        headers={"Accept": "application/json"},
        method="GET",
    )

    try:
        with request.urlopen(http_request, timeout=timeout) as response:
            raw_body = response.read().decode("utf-8", errors="replace")
            body, malformed = _parse_json(raw_body)
            return {
                "endpoint": endpoint,
                "url": url,
                "available": True,
                "response_received": True,
                "http_status": response.status,
                "ok": 200 <= response.status < 300 and not malformed,
                "malformed": malformed,
                "body": body,
                "shape": _shape_summary(body),
                "error": "" if not malformed else "response was not valid JSON",
                "duration_seconds": round(time.perf_counter() - started, 3),
            }
    except error.HTTPError as exc:
        raw_body = exc.read().decode("utf-8", errors="replace")
        body, malformed = _parse_json(raw_body)
        return {
            "endpoint": endpoint,
            "url": url,
            "available": True,
            "response_received": True,
            "http_status": exc.code,
            "ok": False,
            "malformed": malformed,
            "body": body,
            "shape": _shape_summary(body),
            "error": str(exc) if not malformed else "response was not valid JSON",
            "duration_seconds": round(time.perf_counter() - started, 3),
        }
    except (error.URLError, TimeoutError, OSError) as exc:
        return {
            "endpoint": endpoint,
            "url": url,
            "available": False,
            "response_received": False,
            "http_status": None,
            "ok": False,
            "malformed": False,
            "body": {},
            "shape": _shape_summary({}),
            "error": str(exc),
            "duration_seconds": round(time.perf_counter() - started, 3),
        }


def evaluate_results(results, strict=False):
    if not results:
        return {
            "status": "FAIL",
            "exit_code": 1,
            "errors": ["no endpoint results were collected"],
        }

    failures = []
    unavailable = []
    for result in results:
        endpoint = result.get("endpoint", "")
        if result.get("malformed"):
            failures.append(f"{endpoint}: malformed response")
        elif result.get("response_received") and not result.get("ok"):
            failures.append(f"{endpoint}: HTTP status {result.get('http_status')}")
        elif not result.get("available"):
            unavailable.append(endpoint)

    if failures:
        return {
            "status": "FAIL",
            "exit_code": 1,
            "errors": failures,
        }

    if unavailable:
        return {
            "status": "UNAVAILABLE",
            "exit_code": 1 if strict else 0,
            "errors": [f"{endpoint}: unavailable" for endpoint in unavailable],
        }

    return {
        "status": "OK",
        "exit_code": 0,
        "errors": [],
    }


def write_report(root, base_url, strict, results, evaluation):
    path = report_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# GPTMEAI_LIVE_READONLY_STATUS_REPORT.md",
        "",
        f"- Generated: `{_utc_now()}`",
        f"- Project root: `{root}`",
        f"- GPTMEAi base URL: `{base_url}`",
        f"- Strict mode: `{strict}`",
        f"- Status: `{evaluation['status']}`",
        "",
        "## Endpoints",
        "",
    ]

    for result in results:
        body = result.get("body", {})
        if body is None:
            body = {"error": "body was not valid JSON"}
        lines.extend(
            [
                f"### `{result['endpoint']}`",
                "",
                f"- URL: `{result['url']}`",
                f"- Available: `{result['available']}`",
                f"- HTTP status: `{result['http_status']}`",
                f"- OK: `{result['ok']}`",
                f"- Malformed: `{result['malformed']}`",
                f"- Duration seconds: `{result['duration_seconds']}`",
                f"- Error: `{result.get('error', '')}`",
                f"- Top-level keys: `{', '.join(result.get('shape', {}).get('top_level_keys', []))}`",
                "",
                "```json",
                json.dumps(body, indent=2, sort_keys=True),
                "```",
                "",
            ]
        )

    lines.extend(
        [
            "## Safety",
            "",
            "- This tool performs GET requests only.",
            "- It checks only `/health`, `/planner/status`, and `/execution/status`.",
            "- It is optional for v0.1 local verification.",
            "- It does not start GPTMEAi or enable bridge execution.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _timeout_from_env():
    raw_value = os.environ.get("GPTMEAI_LIVE_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS))
    try:
        timeout = float(raw_value)
    except ValueError:
        timeout = DEFAULT_TIMEOUT_SECONDS
    return max(timeout, 0.1)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    root = project_root()
    base_url = os.environ.get("GPTMEAI_BASE_URL", DEFAULT_BASE_URL)
    timeout = _timeout_from_env()

    results = [check_endpoint(base_url, endpoint, timeout) for endpoint in ALLOWED_ENDPOINTS]
    evaluation = evaluate_results(results, strict=args.strict)
    report = write_report(root, base_url, args.strict, results, evaluation)

    print(f"GPTMEAI_LIVE_READONLY={evaluation['status']}")
    print(f"REPORT={report}")
    for result in results:
        status = result.get("http_status")
        if status is None:
            print(f"{result['endpoint']}=UNAVAILABLE error={result.get('error', '')}")
        else:
            print(f"{result['endpoint']}=HTTP_{status}")
    for error_message in evaluation["errors"]:
        print(f"- {error_message}")
    return evaluation["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
