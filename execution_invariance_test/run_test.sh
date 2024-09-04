#!/bin/bash

python3 -m venv venv 
source venv/bin/activate
pip install -U pip setuptools 
SCRIPTS_DIR=$(dirname $(realpath "$0"))
PARENT_DIR=$(dirname $SCRIPTS_DIR)
ANALYSIS_DIR=$SCRIPTS_DIR/analysis
pip install -e $ANALYSIS_DIR
pip install pytest-json-report
pip install $PARENT_DIR
uniqueID=$(python -c "import uuid; print(uuid.uuid4())")
export DYNAPYT_SESSION_ID=$uniqueID
echo "DYNAPYT_SESSION_ID=$DYNAPYT_SESSION_ID"
temp_dir="${TMPDIR:-/tmp}"
file_path=$temp_dir/dynapyt_analyses-$uniqueID.txt
touch $file_path
echo "analysis.analysis.Analysis" > $file_path
cat $file_path
python $SCRIPTS_DIR/test.py
deactivate
rm $temp_dir/dynapyt_analyses-$uniqueID.txt
rm -rf venv

