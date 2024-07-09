#!/bin/bash
# Usage: bash run_cli.sh <path_to_project_root> <project_name> <test_command>
# Example: bash run_cli.sh simple-with-pytest simple_with_pytest "pytest -n 6 tests"

RED='\033[0;31m'
GREEN='\033[0;32m'
RESET='\033[0m'

python -m venv venv
source venv/bin/activate
SCRIPTS_DIR=$(dirname $(realpath "$0"))
echo "Installing..."
pip install -e $SCRIPTS_DIR/../..[end2end]
pip install -e $SCRIPTS_DIR/../projects/$1
if [ -f $SCRIPTS_DIR/../projects/$1/requirements.txt ]; then
    pip install -r $SCRIPTS_DIR/../projects/$1/requirements.txt
fi
# python -c "import $2.analysis; print($2.analysis.Analysis)"
echo "Instrumenting..."
python -m dynapyt.run_instrumentation --directory $SCRIPTS_DIR/../projects/$1 --analysis="$2.analysis.Analysis"
echo "Setting up the analyses..."
uniqueID=$(python -c "import uuid; print(uuid.uuid4())")
export DYNAPYT_SESSION_ID=$uniqueID
temp_dir="${TMPDIR:-/tmp}"
mkdir $temp_dir/dynapyt_output-$uniqueID
echo "$2.analysis.Analysis;output_dir=$temp_dir/dynapyt_output-$uniqueID" > $temp_dir/dynapyt_analyses-$uniqueID.txt
cat $temp_dir/dynapyt_analyses-$uniqueID.txt
echo "Setting up coverage..."
export DYNAPYT_COVERAGE="$temp_dir/dynapyt_coverage-$uniqueID"
cd $SCRIPTS_DIR/../projects/$1
echo "Running..."
$3
cd $SCRIPTS_DIR
echo "Collecting the results..."
python -m dynapyt.post_run --coverage_dir="$temp_dir/dynapyt_coverage-$uniqueID" --output_dir="$temp_dir/dynapyt_output-$uniqueID"
echo "Checking correctness..."
python ./check.py --project_dir="$SCRIPTS_DIR/../projects/$1" --output_dir="$temp_dir/dynapyt_output-$uniqueID" --coverage_dir="$temp_dir/dynapyt_coverage-$uniqueID"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Passed.${RESET}"
else
    echo -e "${RED}Failed.${RESET}"
fi
echo "Cleaning up..."
python ./revert.py --root="$SCRIPTS_DIR/../projects/$1"
rm $temp_dir/dynapyt_analyses-$uniqueID.txt
rm -rf $temp_dir/dynapyt_coverage-$uniqueID
rm -rf $temp_dir/dynapyt_output-$uniqueID
deactivate
rm -rf venv
echo "Done."