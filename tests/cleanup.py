from pathlib import Path
import shutil

here = Path(__file__).parent.resolve()
dirty_files = here.glob("**/*.py.orig")
for dirty_file in dirty_files:
    metadata_file = Path(*(dirty_file.parts[:-1])) / (
        dirty_file.name.rstrip(".py.orig") + "-dynapyt.json"
    )
    print(f"Deleting {metadata_file}")
    if metadata_file.exists():
        metadata_file.unlink()
    if (Path(*(dirty_file.parts[:-1])) / "__pycache__").exists():
        print(f"Deleting {Path(*(dirty_file.parts[:-1])) / '__pycache__'}")
        shutil.rmtree(Path(*(dirty_file.parts[:-1])) / "__pycache__")
    correct_file = Path(*(dirty_file.parts[:-1])) / (
        dirty_file.name.rstrip(".py.orig") + ".py"
    )
    print(f"Restoring {dirty_file} to {correct_file}")
    dirty_file.rename(correct_file)

dirty_files = here.glob("**/*-dynapyt.json")
for dirty_file in dirty_files:
    if (Path(*(dirty_file.parts[:-1])) / "__pycache__").exists():
        print(f"Deleting {Path(*(dirty_file.parts[:-1])) / '__pycache__'}")
        shutil.rmtree(Path(*(dirty_file.parts[:-1])) / "__pycache__")
    if dirty_file.exists():
        dirty_file.unlink()

dirty_files = here.glob("**/coverage*.json")
for dirty_file in dirty_files:
    if dirty_file.exists():
        dirty_file.unlink()

dirty_dirs = here.glob("**/dynapyt_coverage-*")
for dirty_dir in dirty_dirs:
    if dirty_dir.exists():
        shutil.rmtree(dirty_dir)
