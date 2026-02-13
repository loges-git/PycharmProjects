from git_ops.git_utils import git_status


def check_working_tree_clean(repo_path):
    """
    Blocks execution if repo has staged or unstaged changes.
    """
    status = git_status(repo_path)

    if status:
        raise RuntimeError(
            "❌ Working tree is NOT clean.\n\n"
            "Please commit, stash, or discard changes before running retrofit.\n\n"
            f"Details:\n{status}"
        )

    print("✅ Repo clean. Proceeding.")


def warn_untracked_files(repo_path):
    """
    Shows warning if untracked files exist.
    Does NOT block execution.
    """
    status = git_status(repo_path)
    untracked = [
        line for line in status.splitlines()
        if line.startswith("??")
    ]

    if untracked:
        print("⚠️ WARNING: Untracked files detected:")
        for file in untracked:
            print(f"   {file}")

        print(
            "\n⚠️ These files will NOT be included in commit.\n"
            "If they are important, add them explicitly."
        )
