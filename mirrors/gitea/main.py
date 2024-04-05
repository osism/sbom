import sys

from github import Github
from loguru import logger
import requests
import yaml

GITHUB_URL = "https://github.com"

level = "INFO"
log_fmt = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | "
    "<level>{message}</level>"
)

logger.remove()
logger.add(sys.stderr, format=log_fmt, level=level, colorize=True)


def read_config():
    with open("config.yaml", "r") as fp:
        try:
            result = yaml.safe_load(fp)
        except yaml.YAMLError as e:
            print(e)

    return result


def mirror_github_repository(
    url: str, headers: dict, payload: dict, enable_ssl: bool = True
) -> None:
    logger.info(
        f"Mirroring {payload['clone_addr']} -> {payload['repo_owner']}/{payload['repo_name']}"
    )
    result = requests.post(url=url, headers=headers, json=payload, verify=enable_ssl)
    return result


def get_headers(token: str) -> dict:
    result = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"token {token}",
    }
    return result


def get_payload(
    org: str, repo: str, owner: str, token: str = None, private: bool = True
) -> dict:
    result = {
        "service": "github",
        "clone_addr": f"{GITHUB_URL}/{org}/{repo}",
        "mirror": True,
        "private": private,
        "repo_name": repo,
        "repo_owner": owner,
    }
    if token:
        result["auth_token"] = token
    return result


def get_repos(org: str, token: str = None) -> dict:
    if token:
        github = Github(token)
    else:
        github = Github()
    organization = github.get_organization(org)
    result = organization.get_repos(type="public")
    return result


def mirror_github_organization(
    gitea_api_url: str,
    gitea_api_ssl: bool,
    gitea_owner: str,
    gitea_token: str,
    github_org: str,
    github_token: str,
) -> None:

    for repo in get_repos(org=github_org, token=github_token):
        logger.info(f"Processing {repo.name}")
        mirror_github_repository(
            url=f"{gitea_api_url}/repos/migrate",
            headers=get_headers(gitea_token),
            payload=get_payload(
                token=github_token,
                org=github_org,
                repo=repo.name,
                private=repo.private,
                owner=gitea_owner,
            ),
            enable_ssl=gitea_api_ssl,
        )


config = read_config()
mirror_github_organization(
    gitea_api_url=config["gitea_api_url"],
    gitea_api_ssl=config.get("gitea_api_ssl", True),
    gitea_owner=config["gitea_owner"],
    gitea_token=config["gitea_token"],
    github_org=config["github_org"],
    github_token=config.get("github_token", None),
)
