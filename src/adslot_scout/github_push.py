from __future__ import annotations

import os
from typing import Any

import httpx

API = os.environ.get("GITHUB_API", "https://api.github.com")


class GitHubError(RuntimeError):
    pass


class GitHubClient:
    def __init__(self, token: str | None = None) -> None:
        self.token = token or os.environ.get("GITHUB_TOKEN", "")
        if not self.token:
            raise GitHubError(
                "GITHUB_TOKEN is missing. Create a PAT with repo scope and export it."
            )
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "adslot-scout",
        }

    def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        with httpx.Client(timeout=30.0, headers=self.headers) as client:
            response = client.request(method, f"{API}{path}", **kwargs)
        if response.status_code >= 400:
            raise GitHubError(f"{method} {path} failed ({response.status_code}): {response.text[:500]}")
        return response

    def whoami(self) -> dict[str, Any]:
        return self._request("GET", "/user").json()

    def create_repo(self, name: str, private: bool, description: str) -> dict[str, Any]:
        payload = {
            "name": name,
            "private": private,
            "description": description,
            "auto_init": True,
        }
        return self._request("POST", "/user/repos", json=payload).json()

    def repo_exists(self, owner: str, repo: str) -> bool:
        with httpx.Client(timeout=30.0, headers=self.headers) as client:
            response = client.get(f"{API}/repos/{owner}/{repo}")
        if response.status_code == 404:
            return False
        if response.status_code >= 400:
            raise GitHubError(f"GET /repos/{owner}/{repo} failed ({response.status_code}): {response.text[:500]}")
        return True

    def put_file(
        self,
        owner: str,
        repo: str,
        path: str,
        content: str,
        message: str,
        branch: str,
    ) -> dict[str, Any]:
        import base64

        sha = None
        with httpx.Client(timeout=30.0, headers=self.headers) as client:
            existing = client.get(
                f"{API}/repos/{owner}/{repo}/contents/{path}",
                params={"ref": branch},
            )
        if existing.status_code == 200:
            sha = existing.json().get("sha")
        elif existing.status_code not in {200, 404}:
            raise GitHubError(f"GET contents/{path} failed ({existing.status_code}): {existing.text[:400]}")

        payload: dict[str, Any] = {
            "message": message,
            "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
            "branch": branch,
        }
        if sha:
            payload["sha"] = sha
        return self._request("PUT", f"/repos/{owner}/{repo}/contents/{path}", json=payload).json()

    def publish_briefing(
        self,
        owner: str,
        repo: str,
        files: dict[str, str],
        branch: str,
        create: bool,
        private: bool,
        description: str,
    ) -> str:
        if create and not self.repo_exists(owner, repo):
            created = self.create_repo(repo, private=private, description=description)
            # Creating under the user account; if owner is an org this still works only for user repos.
            html = created.get("html_url", f"https://github.com/{owner}/{repo}")
        else:
            html = f"https://github.com/{owner}/{repo}"
        for path, content in files.items():
            self.put_file(owner, repo, path, content, f"Add {path} from AdSlot Scout", branch)
        return html
