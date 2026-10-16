#!/usr/bin/env python3

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def load_env(path: Path) -> None:
    """Load simple KEY=VALUE entries without overriding the calling environment."""
    if not path.exists():
        return
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def fail(message: str) -> None:
    print(f"forge-api: {message}", file=sys.stderr)
    raise SystemExit(2)


def create_token(user: str) -> None:
    container_cli = shutil.which("podman") or shutil.which("docker")
    if not container_cli:
        fail("podman or docker is required")

    command = [
        container_cli,
        "exec",
        "-u",
        "git",
        "forgejo",
        "forgejo",
        "admin",
        "user",
        "generate-access-token",
        "--username",
        user,
        "--token-name",
        f"forge-cli-{int(time.time())}",
        "--scopes",
        "all",
        "--raw",
    ]
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as error:
        raise SystemExit(error.returncode) from error


def api_post(api_url: str, token: str, endpoint: str, body: dict) -> None:
    request = urllib.request.Request(
        f"{api_url.rstrip('/')}{endpoint}",
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"token {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request) as response:
            result = json.load(response)
    except urllib.error.HTTPError as error:
        detail = error.read().decode(errors="replace").strip()
        fail(f"request failed ({error.code}): {detail or error.reason}")
    except urllib.error.URLError as error:
        fail(f"could not reach Forgejo: {error.reason}")

    created = result.get("html_url") or result.get("username") or result.get("name")
    print(f"created {created}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Provision the local Forgejo instance")
    commands = parser.add_subparsers(dest="command", required=True)

    token = commands.add_parser("token", help="create an API token")
    token.add_argument("user")

    org = commands.add_parser("org", help="manage organizations")
    org_commands = org.add_subparsers(dest="org_command", required=True)
    org_create = org_commands.add_parser("create", help="create an organization")
    org_create.add_argument("name")
    org_create.add_argument("--description", default="")
    org_create.add_argument(
        "--visibility", choices=("public", "limited", "private"), default="public"
    )

    repo = commands.add_parser("repo", help="manage repositories")
    repo_commands = repo.add_subparsers(dest="repo_command", required=True)
    repo_create = repo_commands.add_parser("create", help="create a repository")
    repo_create.add_argument("repository", metavar="[OWNER/]NAME")
    repo_create.add_argument("--description", default="")
    repo_create.add_argument("--private", action="store_true")
    repo_create.add_argument("--init", action="store_true")

    return parser


def main() -> None:
    load_env(Path(__file__).resolve().parent / ".env")
    args = build_parser().parse_args()

    if args.command == "token":
        create_token(args.user)
        return

    token = os.environ.get("TOKEN")
    if not token:
        fail("TOKEN is not set; run `export TOKEN=$(./forge-api.py token USER)` first")
    forge_host = os.environ.get("FORGE_HOST", "forge.lan")
    api_url = os.environ.get("FORGE_API_URL", f"http://{forge_host}:3000/api/v1")

    if args.command == "org":
        api_post(
            api_url,
            token,
            "/orgs",
            {
                "username": args.name,
                "description": args.description,
                "visibility": args.visibility,
            },
        )
        return

    if "/" in args.repository:
        parts = args.repository.split("/")
        if len(parts) != 2 or not all(parts):
            fail("repository must be OWNER/NAME")
        owner, name = parts
        endpoint = f"/orgs/{urllib.parse.quote(owner, safe='')}/repos"
    else:
        name = args.repository
        endpoint = "/user/repos"
    api_post(
        api_url,
        token,
        endpoint,
        {
            "name": name,
            "description": args.description,
            "private": args.private,
            "auto_init": args.init,
        },
    )


if __name__ == "__main__":
    main()
