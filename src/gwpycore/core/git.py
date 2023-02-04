import subprocess
from pathlib import Path

__all__ = [
    "git_commit",
    "git_pull",
    "git_push",
]


def git_commit(root_path: Path, msg: str) -> str:
    dir_name = str(root_path)
    result = subprocess.run(["git.exe", "-C", dir_name, "status"], text=True)
    if result.returncode == 0:
        return f"{str(root_path)} is up-to-date (nothing to commit/push)"

    result = subprocess.run(
        ["git.exe", "-C", dir_name, "commit", "-v", "-a", "-m", f'"{msg}"']
    )
    return str(result)


def git_pull(root_path: Path) -> str:
    return str(subprocess.run(["git.exe", "-C", str(root_path), "pull", "--no-rebase", "origin"]))


def git_push(root_path: Path) -> str:
    return str(subprocess.run(["git.exe", "-C", str(root_path), "push", "origin"]))
