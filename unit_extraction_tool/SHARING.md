# How to Share the Unit Extraction Tool

This guide provides instructions on how to share the Unit Extraction Tool with others, including both developers and non-technical users.

## Option 1: Share Source Code (For Developers)

Best for users who are comfortable with Git and Python.

1.  **Share the Git Repository**:
    Provide them with the URL to your git repository.

2.  **Installation Instructions**:
    Tell them to follow the **Installation** section in the `README.md`:
    ```bash
    git clone <repo-url>
    cd unit_extraction_tool
    pip install -r requirements.txt
    streamlit run app.py
    ```

## Option 2: Share Portable Bundle (For Same OS)

Best for users on the same operating system (e.g., Windows to Windows) who don't want to install Python manually.

1.  **Prepare the Bundle**:
    -   Delete any existing `venv` folder.
    -   Create a new virtual environment: `python -m venv venv`
    -   Activate it and install dependencies:
        ```cmd
        venv\Scripts\activate
        pip install -r requirements.txt
        ```
    -   **Important**: Copy your configured `config.py` (with repo URLs) if you want to share your configuration.

2.  **Zip the Folder**:
    -   Select the entire `unit_extraction_tool` folder.
    -   Right-click -> Send to -> Compressed (zipped) folder.

3.  **Share the Zip**:
    -   Send the `.zip` file to the user.
    -   Instruct them to unzip it and double-click `run.bat` to start the tool.

## Option 3: Share Standalone Executable (Best for End Users)

Best for non-technical users. Creates a single `.exe` file that requires no installation.

1.  **Build the Executable**:
    Run the build script in your terminal:
    ```bash
    python build_exe.py
    ```
    *Note: This process may take a few minutes.*

2.  **Locate the Output**:
    Go to the `dist` folder. You will find `UnitExtractionTool.exe`.

3.  **Share the Executable**:
    -   Send the `UnitExtractionTool.exe` file to the user.
    -   They can run it simply by double-clicking.
    -   **Note**: They might get a warning from Windows Defender since the app is not signed. Tell them to click "More info" -> "Run anyway".

## Important Notes

-   **Access to Repositories**: The user must have permission/access to the Git repositories defined in `config.py` (e.g., SSH keys set up or VPN connected).
-   **Configuration**: If you share the source (Option 1) or build (Option 3), ensure the user knows how to update `config.py` or provides a pre-configured one.
