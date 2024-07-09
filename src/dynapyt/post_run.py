import fire
from pathlib import Path

from .utils.runtimeUtils import gather_coverage, gather_output


def post_run(coverage_dir: str, output_dir: str):
    gather_coverage(Path(coverage_dir))
    gather_output(Path(output_dir))


if __name__ == "__main__":
    fire.Fire(post_run)
