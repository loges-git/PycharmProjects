# Unit Extraction Tool

A powerful Streamlit-based utility for extracting files from Git repositories based on Jira ticket numbers. This tool simplifies the process of gathering changed files across multiple branches and repository variants (DB/FE) for deployment or review.

## 🌟 Features

-   **Multi-Repository Support**: Simultaneously handles Database (DB) and Frontend (FE) repository variants.
-   **Jira Integration**: specific file extraction based on Jira ticket numbers committed in git logs.
-   **Smart Extraction**:
    -   Extracts both existing and deleted files.
    -   Maintains original directory structure.
    -   Automatically handles parent commit extraction for deleted files.
-   **Branch Management**: Supports extraction from single or multiple branches (e.g., proper release flow: `release/develop`, `release/release`, `main`).
-   **Safety First**:
    -   Checks for uncommitted changes before starting.
    -   Auto-stashing and restoring of local changes.
    -   Validates repository state.
-   **User-Friendly UI**: Modern, responsive interface built with Streamlit.

## 📋 Prerequisites

-   Python 3.8 or higher
-   Git installed and configured in your system PATH
-   Access to the target repositories (SSH/HTTPS)

## 🚀 Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd unit_extraction_tool
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    
    # Windows
    venv\Scripts\activate
    
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## ⚙️ Configuration

Before running the tool, you must configure your repository settings in `config.py`.

1.  Open `config.py` in your editor.
2.  Update the `CLONE_URLS` dictionary with the actual URLs of your repositories:
    ```python
    CLONE_URLS = {
        'ssa': {
            'db': 'git@github.com:yourorg/ssa-db.git',
            'fe': 'git@github.com:yourorg/ssa-fe.git'
        },
        # ... other repos
    }
    ```
3.  (Optional) Adjust `BRANCH_MAPPING` if your branch names differ:
    ```python
    BRANCH_MAPPING = {
        'CIT': 'release/develop',
        'BFX': 'release/release',
        'PROD': 'main'
    }
    ```

## 💻 Usage

1.  **Start the application:**
    ```bash
    streamlit run app.py
    ```

2.  **Open your browser:** The app should automatically open at `http://localhost:8501`.

3.  **Step-by-Step Guide:**
    *   **Input Parameters**:
        *   Enter the **Jira Number** (e.g., `BANKING-12345`).
        *   Enter the **Base Path** where your repositories are checked out locally.
        *   Click **🔍 Scan Repositories** to find available repos in that path.
        *   Select the **Target Repository** from the dropdown.
    *   **Extraction Options**:
        *   Enter the **Output Directory** where extracted files will be saved.
        *   Choose **Extraction Mode**: Single Branch or Multiple Branches.
    *   **Run**:
        *   Click **🚀 Extract Units**.
    *   **Results**:
        *   View the summary of extracted and deleted files.
        *   Click **📂 Open Folder** to view the files in your file explorer.

## 🔍 Troubleshooting

-   **"Repository not detected"**: Ensure the Base Path is correct and the repository folders follow the naming convention (e.g., `project.repo.db` or `repo.fe`).
-   **"Git command failed"**: accurate Git credentials are required. Ensure you can `git pull` from the terminal without password prompts (use SSH keys).
-   **Permission Errors**: Ensure the Output Directory is writable and not open in another detailed program.

## 📝 License

[Your License Here]
