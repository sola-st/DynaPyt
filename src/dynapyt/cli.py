import argparse
import docker
import os
import shutil
import tempfile
from pathlib import Path
import dynapyt

def main():
    parser = argparse.ArgumentParser(description="DynaPyt CLI")
    parser.add_argument("--project-root", required=True, help="Path to the project root")
    parser.add_argument("--analysis", required=True, help="Path to the analysis file")
    parser.add_argument("--setup", required=False, default="", help="Setup script/command to run")
    parser.add_argument("--output-dir", required=True, help="Output directory for analysis results")
    parser.add_argument("run_command", nargs=argparse.REMAINDER, help="Command to run after instrumentation")
    
    args = parser.parse_args()
    
    project_root = Path(args.project_root).resolve()
    analysis_file = Path(args.analysis).resolve()
    output_dir = Path(args.output_dir).resolve()
    
    run_cmd_list = args.run_command
    if run_cmd_list and run_cmd_list[0] == "--":
        run_cmd_list = run_cmd_list[1:]
    run_command = " ".join(run_cmd_list)

    dynapyt_dir = Path(dynapyt.__file__).parent.parent.parent

    client = docker.from_env()

    # Docker image build
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        
        dockerfile_content = """
FROM python:3.13-slim
RUN apt-get update && apt-get install -y gcc git
RUN pip install git+https://github.com/sola-st/DynaPyt.git@main#egg=dynapyt
"""
        with open(temp_dir_path / "Dockerfile", "w") as f:
            f.write(dockerfile_content)

        print("Building Docker image with DynaPyt installed...")
        try:
            image, logs = client.images.build(path=str(temp_dir_path), tag="dynapyt_runner", rm=True)
            for log in logs:
                if 'stream' in log:
                    print(log['stream'], end='')
        except docker.errors.BuildError as e:
            print("Failed to build Docker image:")
            for log in e.build_logs:
                if 'stream' in log:
                    print(log['stream'], end='')
            return


    setup_cmd = args.setup
    analysis_file_mnt = f"/analysis/{analysis_file.name}"

    print(f"\nRunning container for project {project_root}...")
    print(f"Analysis file: {analysis_file_mnt}")
    print(f"Setup command: {setup_cmd}")
    print(f"Output directory: {output_dir}")
    print(f"Run command: {run_command}")

    tmp_output_dir = "/tmp/dynapyt_output"

    final_analysis_file = analysis_file.parent / "final_analysis.txt"
    with open(analysis_file, "r") as f:
        content = f.read()
    with open(final_analysis_file, "w") as f:
        for line in content.splitlines():
            if ";output_dir=" not in line:
                f.write(line + f";output_dir={tmp_output_dir}\n")
            else:
                analysis, _ = line.split(";output_dir=")
                f.write(analysis + f";output_dir={tmp_output_dir}\n")

    entrypoint_script = f"""#!/bin/bash
set -e
cp -r /project_root /tmp/project
cd /tmp/project
{setup_cmd}
export PYTHONPATH="/analysis:$PYTHONPATH"
python -m dynapyt.run_instrumentation --directory . --analysisFile /analysis/final_analysis.txt
export DYNAPYT_SESSION_ID="1234-abcd"
cp /analysis/final_analysis.txt /tmp/dynapyt_analyses-1234-abcd.txt
{run_command}
"""
    
    try:
        container = client.containers.run(
            "dynapyt_runner",
            command=["/bin/bash", "-c", entrypoint_script],
            mounts=[
                docker.types.Mount(target="/project_root", source=str(project_root), type="bind", read_only=False),
                docker.types.Mount(target="/analysis", source=str(analysis_file.parent), type="bind", read_only=True),
                docker.types.Mount(target="/tmp/dynapyt_output", source=str(output_dir), type="bind", read_only=False),
            ],
            remove=True,
            stdout=True,
            stderr=True,
            stream=True
        )
        for line in container:
            print(line.decode("utf-8"), end="")
    except docker.errors.ContainerError as e:
        print(f"Container error: {e}")
        try:
            print(e.container.logs().decode("utf-8"))
        except docker.errors.NotFound:
            pass


if __name__ == "__main__":
    main()
