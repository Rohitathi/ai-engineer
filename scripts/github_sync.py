import os
import requests


def sync_repo(repo: str | None = None) -> dict:
    repo = repo or os.getenv("GITHUB_REPO", "")
    if not repo:
        return {"status": "skipped", "reason": "no repo configured"}

    try:
        response = requests.get(f"https://api.github.com/repos/{repo}", timeout=10)
        response.raise_for_status()
        data = response.json()
        return {"status": "ok", "full_name": data.get("full_name"), "default_branch": data.get("default_branch")}
    except Exception as exc:  # pragma: no cover
        return {"status": "error", "message": str(exc)}
