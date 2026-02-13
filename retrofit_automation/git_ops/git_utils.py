import subprocess


def run_git(cmd, cwd):
    """
    Run a git command safely and return stdout.
    Raises exception if command fails.
    """
    result = subprocess.run(
        cmd,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=False
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Git command failed:\n"
            f"Command: {' '.join(cmd)}\n"
            f"Error: {result.stderr}"
        )

    return result.stdout.strip()


def git_fetch(repo_path):
    return run_git(["git", "fetch"], repo_path)


def git_checkout(branch, repo_path):
    return run_git(["git", "checkout", branch], repo_path)


def git_pull(repo_path):
    return run_git(["git", "pull"], repo_path)


def git_branch_list(repo_path):
    return run_git(["git", "branch"], repo_path)


def git_remote_branch_list(repo_path):
    return run_git(["git", "branch", "-r"], repo_path)


def git_status(repo_path):
    return run_git(["git", "status", "--porcelain"], repo_path)
