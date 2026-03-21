from __future__ import annotations

import json
import os
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request

app = Flask(__name__)

LOG_DIR = Path(os.environ.get("RUNNER_LOG_DIR", "/app/logs"))
LOG_DIR.mkdir(parents=True, exist_ok=True)

RUNNER_MODE = os.environ.get("RUNNER_MODE", "mock").strip().lower()

PROJECT_PATHS = {
    "house-bot": "/workspace/house-bot",
    "music-assistant": "/workspace/music-assistant",
    "homelab-core": "/workspace/homelab-core",
    "generic": "/workspace/generic",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_execution_id() -> str:
    return uuid.uuid4().hex[:12]


def write_log(event_type: str, payload: dict[str, Any]) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d")
    log_file = LOG_DIR / f"runner-{ts}.log"
    record = {
        "ts": utc_now(),
        "event_type": event_type,
        "payload": payload,
    }
    with log_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def choose_mock_output(project: str, user_request: str) -> dict[str, Any]:
    if project == "house-bot":
        return {
            "status": "success",
            "summary": "Added chat ID authorization middleware and unauthorized response handling.",
            "files_changed": ["bot/main.py", "bot/auth.py"],
            "diff": """--- a/bot/main.py
+++ b/bot/main.py
@@
- app = create_app()
+ app = create_app(with_chat_auth=True)
""".strip(),
            "commands": [
                "docker compose up -d --build",
                "docker logs -f house-bot",
            ],
            "assumptions": [
                "Runner is still in mock mode",
                "No real files were changed",
            ],
        }

    if project == "music-assistant":
        return {
            "status": "success",
            "summary": "Added dry-run support and prevented file writes when enabled.",
            "files_changed": ["app/main.py", "app/writers.py"],
            "diff": """--- a/app/writers.py
+++ b/app/writers.py
@@
- write_output(path, rows)
+ if not dry_run:
+     write_output(path, rows)
""".strip(),
            "commands": [
                "docker compose up -d --build",
                "docker compose exec music-assistant python -m app --dry-run",
            ],
            "assumptions": [
                "Runner is still in mock mode",
                "No real files were changed",
            ],
        }

    if project == "homelab-core":
        return {
            "status": "success",
            "summary": "Prepared a homelab feature patch plan with compose-safe changes.",
            "files_changed": ["docker-compose.yml", "README.md"],
            "diff": """--- a/docker-compose.yml
+++ b/docker-compose.yml
@@
+ # mock homelab feature change
""".strip(),
            "commands": [
                "docker compose config",
                "docker compose up -d",
            ],
            "assumptions": [
                "Runner is still in mock mode",
                "No real files were changed",
            ],
        }

    return {
        "status": "success",
        "summary": f"Prepared generic mock implementation for request: {user_request}",
        "files_changed": ["README.md"],
        "diff": """--- a/README.md
+++ b/README.md
@@
+ MVP mock change
""".strip(),
        "commands": [
            "docker compose up -d --build",
            "docker logs -f <service-name>",
        ],
        "assumptions": [
            "Runner is still in mock mode",
            "No real files were changed",
        ],
    }


def build_plan_only_output(
    project: str,
    user_request: str,
    claude_prompt: str,
    execution_id: str,
) -> dict[str, Any]:
    project_path = PROJECT_PATHS.get(project, PROJECT_PATHS["generic"])

    # Пока это не реальный Claude CLI вызов, а подготовленный plan-only ответ.
    # Следующим этапом мы заменим это на controlled subprocess/CLI call.
    summary = (
        f"Plan-only execution prepared for project '{project}'. "
        f"No files were modified. Ready to replace with real Claude executor."
    )

    preview_prompt = claude_prompt[:4000]

    return {
        "status": "success",
        "summary": summary,
        "files_changed": [],
        "diff": "",
        "commands": [
            f"cd {project_path}",
            "# next step: invoke Claude Code in plan-only mode",
        ],
        "assumptions": [
            "Runner is in plan mode",
            "No real files were changed",
            "Claude execution is not yet wired in this stage",
        ],
        "plan": {
            "project_path": project_path,
            "execution_id": execution_id,
            "prompt_preview": preview_prompt,
        },
    }


@app.get("/health")
def health() -> Any:
    return jsonify(
        {
            "status": "ok",
            "service": "ai-runner",
            "mode": RUNNER_MODE,
            "ts": utc_now(),
        }
    )


@app.post("/execute")
def execute() -> Any:
    data = request.get_json(silent=True) or {}

    execution_id = str(data.get("execution_id") or new_execution_id()).strip()

    user_request = str(data.get("user_request", "")).strip()
    interpretation = data.get("interpretation") or {}

    if isinstance(interpretation, str):
        try:
            interpretation = json.loads(interpretation)
        except json.JSONDecodeError:
            interpretation = {}

    claude_prompt = str(data.get("claude_prompt", "")).strip()

    project = str(interpretation.get("project", "generic")).strip() or "generic"
    task_type = str(interpretation.get("task_type", "feature")).strip() or "feature"
    project_path = PROJECT_PATHS.get(project, PROJECT_PATHS["generic"])

    request_record = {
        "execution_id": execution_id,
        "user_request": user_request,
        "project": project,
        "project_path": project_path,
        "task_type": task_type,
        "has_prompt": bool(claude_prompt),
        "mode": RUNNER_MODE,
    }
    write_log("execute_request", request_record)

    if RUNNER_MODE == "plan":
        result = build_plan_only_output(
            project=project,
            user_request=user_request,
            claude_prompt=claude_prompt,
            execution_id=execution_id,
        )
    else:
        result = choose_mock_output(project, user_request)

    result["execution_id"] = execution_id
    result["user_request"] = user_request
    result["interpretation"] = interpretation
    result["claude_prompt"] = claude_prompt
    result["runner"] = {
        "service": "ai-runner",
        "mode": RUNNER_MODE,
        "project_path": project_path,
        "ts": utc_now(),
    }

    write_log("execute_response", result)
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081, debug=False)
