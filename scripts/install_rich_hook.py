import site
import sys
from pathlib import Path

# The code we want to put in sitecustomize.py
RICH_HOOK = """
try:
    from rich.traceback import install
    install()
except ImportError:
    pass
"""


def main() -> None:
    """
    Adds sitecustomize.py to the site-packages directory to automate using Rich for terminal formatting.
    """
    # Find the site-packages directory
    try:
        # Use getsitepackages() which returns a list
        site_packages_path = site.getsitepackages()[0]
    except AttributeError:
        # Fallback for some venv configurations
        from distutils.sysconfig import get_python_lib

        site_packages_path = get_python_lib()

    if not site_packages_path:
        print("Could not find site-packages directory.", file=sys.stderr)
        return

    # Define the path for our custom file
    customizer_path = Path(site_packages_path) / "sitecustomize.py"

    # Write the rich hook, creating or overwriting the file
    try:
        customizer_path.write_text(RICH_HOOK)
        print(f"Successfully wrote rich hook to {customizer_path}")
    except Exception as e:
        print(f"Error writing to {customizer_path}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
