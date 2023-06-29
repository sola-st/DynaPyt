from pathlib import Path

here = Path(__file__).parent.resolve()
dirty_files = here.glob("**/*.py.orig")
for dirty_file in dirty_files:
    metadata_file = Path(*(dirty_file.parts[:-1])) / (
        dirty_file.name.rstrip(".py.orig") + "-dynapyt.json"
    )
    print(f"Deleting {metadata_file}")
    if metadata_file.exists():
        metadata_file.unlink()
    correct_file = Path(*(dirty_file.parts[:-1])) / (
        dirty_file.name.rstrip(".py.orig") + ".py"
    )
    print(f"Restoring {dirty_file} to {correct_file}")
    dirty_file.rename(correct_file)
