from git_ops.git_utils import (
    git_fetch,
    git_checkout,
    git_pull,
    git_branch_list,
    git_remote_branch_list,
    run_git,
)


def create_or_reuse_feature_branch(
    repo_path,
    base_branch,
    banking_number,
):
    banking_number = banking_number.strip()
    if not banking_number:
        raise ValueError("BANKING number cannot be empty")

    feature_branch = f"feature/{banking_number}"

    # Always fetch first
    git_fetch(repo_path)

    # Check local branches
    local_branches = git_branch_list(repo_path)
    if feature_branch in local_branches:
        print(f"🔁 Reusing existing local branch: {feature_branch}")
        git_checkout(feature_branch, repo_path)
        return feature_branch

    # Check remote branches
    remote_branches = git_remote_branch_list(repo_path)
    if f"origin/{feature_branch}" in remote_branches:
        raise RuntimeError(
            f"❌ Branch '{feature_branch}' already exists on remote.\n"
            "Please reuse it or choose a new BANKING number."
        )

    # Create new branch correctly
    print(f"🌱 Creating new feature branch from {base_branch}")
    git_checkout(base_branch, repo_path)
    git_pull(repo_path)
    run_git(["git", "checkout", "-b", feature_branch], repo_path)

    print(f"✅ Created feature branch: {feature_branch}")
    return feature_branch
