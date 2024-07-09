from pathlib import Path
import fire


def revert(root: str):
    root = Path(root)
    for f in root.glob("**/*-dynapyt.json"):
        if f.is_file():
            f.unlink()
    for f in root.glob("**/*.py"):
        orig = f.with_suffix(".py.orig")
        if orig.is_file():
            f.unlink()
            orig.rename(f)


if __name__ == "__main__":
    fire.Fire(revert)
