from pathlib import Path


def create_retro_workspace(banking_number):
    """
    Creates review workspace on Desktop:
    Retro_auto/
        feature-BANKING-xxxx/
            Dev/
            CIT/
            Retro/
    """

    banking_number = banking_number.strip()
    if not banking_number:
        raise ValueError("BANKING number cannot be empty")

    # Windows-safe folder name
    folder_name = f"feature-{banking_number}"

    base_path = Path.home() / "Desktop" / "Retro_auto" / folder_name
    base_path.mkdir(parents=True, exist_ok=True)

    dev_dir = base_path / "Dev"
    cit_dir = base_path / "CIT"
    retro_dir = base_path / "Retro"

    dev_dir.mkdir(exist_ok=True)
    cit_dir.mkdir(exist_ok=True)
    retro_dir.mkdir(exist_ok=True)

    print(f"📁 Review workspace created at: {base_path}")

    return {
        "base": base_path,
        "dev": dev_dir,
        "cit": cit_dir,
        "retro": retro_dir,
    }
