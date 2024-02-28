#!/bin/bash
# Usage: ./run_single_project.sh <project_path_from_projects> <project_name> <tests_path_from_project_root>
# Example: ./run_single_project.sh simple-with-pytest simple_with_pytest tests

python -m venv venv
source venv/bin/activate
SCRIPTS_DIR=$(dirname $(realpath "$0"))
pip install -e $SCRIPTS_DIR/../..[end2end]
pip install -e $SCRIPTS_DIR/../projects/$1
if [ -f $SCRIPTS_DIR/../projects/$1/requirements.txt ]; then
    pip install -r $SCRIPTS_DIR/../projects/$1/requirements.txt
fi
python $SCRIPTS_DIR/run_project.py --project_path="$1" --module_name="$2" --path_to_tests="$3"
deactivate
rm -rf venv
