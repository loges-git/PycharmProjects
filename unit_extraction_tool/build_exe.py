import os
import shutil
import subprocess
import sys
from pathlib import Path

def build_exe():
    """
    Build standalone executable using PyInstaller
    """
    print("🚀 Starting build process...")
    
    # Clean previous builds
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    
    if os.path.exists('UnitExtractionTool.spec'):
        os.remove('UnitExtractionTool.spec')

    # Get streamlit path
    import streamlit
    streamlit_path = os.path.dirname(streamlit.__file__)
    
    # Define hidden imports needed for Streamlit
    hidden_imports = [
        'streamlit',
        'streamlit.runtime.scriptrunner.magic_funcs',
        'streamlit.runtime.scriptrunner.script_runner',
        'git',
    ]
    
    # Construct PyInstaller command
    cmd = [
        'pyinstaller',
        '--name=UnitExtractionTool',
        '--onefile',
        '--clean',
        '--noconfirm',
        # Add streamlit package data
        f'--add-data={streamlit_path};streamlit',
        # Include local modules and components
        '--add-data=components;components',
        '--add-data=app.py;.',
        '--add-data=config.py;.',
        '--add-data=styles.py;.',
        '--add-data=utils.py;.',
        '--add-data=git_operations.py;.',
        '--add-data=file_extractor.py;.',
        # Hidden imports
        *[f'--hidden-import={imp}' for imp in hidden_imports],
        # Main entry point
        'run_app.py'  # We need a wrapper script for the exe
    ]
    
    print("🔨 Running PyInstaller...")
    subprocess.check_call(cmd)
    
    print("✅ Build complete! Check 'dist' folder.")

if __name__ == "__main__":
    # Create a wrapper script for the exe
    with open('run_app.py', 'w') as f:
        f.write('''
import streamlit.web.cli as stcli
import os, sys

def resolve_path(path):
    if getattr(sys, "frozen", False):
        basedir = sys._MEIPASS
    else:
        basedir = os.path.dirname(__file__)
    return os.path.join(basedir, path)

if __name__ == "__main__":
    os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
    app_path = resolve_path("app.py")
    sys.argv = ["streamlit", "run", app_path, "--global.developmentMode=false"]
    sys.exit(stcli.main())
''')
    
    try:
        build_exe()
    finally:
        if os.path.exists('run_app.py'):
            os.remove('run_app.py')
