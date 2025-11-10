#!/usr/bin/env python
import shutil
import subprocess
import sys
from pathlib import Path
from subprocess import CalledProcessError
from typing import Any

try:
    from commitizen.cz.utils import get_backup_file_path
except ImportError as error:
    print("Could not import commitizen:", error, file=sys.stderr)
    exit(1)


def main() -> int:
    """
    Main function for the prepare-commit-msg hook.
    """
    commit_msg_file_path = sys.argv[1]
    commit_source = sys.argv[2] if len(sys.argv) > 2 else None

    if commit_source in ("message", "template"):
        return 0

    tty_path = "CON" if sys.platform == "win32" else "/dev/tty"

    # Prepare arguments for the subprocess
    subprocess_args: dict[str, Any] = {
        "stdin": None,
        "check": True,
    }

    # On Windows, we need to create a new console for prompt_toolkit to work
    if sys.platform == "win32":
        subprocess_args["creationflags"] = subprocess.CREATE_NEW_CONSOLE
    else:
        # On other systems, we connect to the existing terminal
        with open(tty_path) as tty:
            subprocess_args["stdin"] = tty

    try:
        subprocess.run(
            [
                "cz",
                "commit",
                "--dry-run",
                "--write-message-to-file",
                commit_msg_file_path,
            ],
            **subprocess_args,
        )

        backup_file = Path(get_backup_file_path())
        shutil.copyfile(commit_msg_file_path, backup_file)

    except CalledProcessError:
        print("Commitizen cancelled. Aborting commit.", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    exit(main())
