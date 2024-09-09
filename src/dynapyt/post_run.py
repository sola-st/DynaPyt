import fire
from pathlib import Path

from .utils.runtimeUtils import gather_coverage, gather_output


def post_run(coverage_dir: str = "", output_dir: str = ""):
    if len(output_dir) > 0:
        gather_output(Path(output_dir))
    if len(coverage_dir) > 0:
        gather_coverage(Path(coverage_dir))


if __name__ == "__main__":
    fire.Fire(post_run)
