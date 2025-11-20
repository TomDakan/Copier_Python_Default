import shutil
from pathlib import Path

from copier import run_copy


def reproduce():
    root_path = Path.cwd()
    destination_path = root_path / "repro_output"

    if destination_path.exists():
        shutil.rmtree(destination_path)

    data = {
        "project_name": "Repro Project",
        "project_slug": "repro-project",
        "author_name": "Tester",
        "email": "test@example.com",
        "description": "Reproduction project",
        "version": "0.1.0",
        "license": "MIT",
        "task_runner": "just",
        "use_safety": False,
        "use_bandit": False,
        "use_docs": False,
        "initialize_git": False,
    }

    print("Running copier...")
    run_copy(
        src_path=str(root_path),
        dst_path=str(destination_path),
        data=data,
        defaults=True,
        unsafe=True,
        vcs_ref="HEAD",
    )

    justfile = destination_path / "repro-project" / "justfile"
    if justfile.exists():
        print(f"\n--- Content of {justfile} ---")
        print(justfile.read_text())
    else:
        print("justfile was not created!")


if __name__ == "__main__":
    reproduce()
