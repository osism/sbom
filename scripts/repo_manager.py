from github import Github
import git
import os
import shutil


def get_repo_urls(user: str) -> list:
    repo_list = []
    g = Github()
    user = g.get_user(user)

    # loop all repos of the org
    for repo in user.get_repos():
        # do not append to list if repo is a fork, archived or private
        if not repo.fork and not repo.archived and not repo.private:
            repo_list.append(repo.clone_url)

    return repo_list


def clone_repos(user: str) -> None:
    try:
        os.mkdir("repos")
    except OSError:
        pass

    for repo in get_repo_urls(user):
        try:
            repo_name = repo.split('/')[-1]  # foo.git
            repo_name = repo_name.removesuffix(".git")  # foo
            clone_destination = f"repos/{repo_name}"  # repos/foo
            git.Repo.clone_from(repo, clone_destination)
        except git.exc.GitCommandError:
            pass


def delete_repos() -> None:
    shutil.rmtree("repos")
