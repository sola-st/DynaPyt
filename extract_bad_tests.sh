#!/bin/bash
# $1: repo name
# $2: test directory in repository root

[ -d venvs ] || mkdir venvs
[ -d under_test ] || mkdir under_test

python -m pip install --user virtualenv

# Create virtual environtment
venv=$1_tmp_env
virtualenv --python 3.9.0 venvs/$venv
source venvs/$venv/bin/activate

# Install requirements for package under test
cp -r ./test/PythonRepos/$1 ./under_test/$1_tmp
cp filter_tests.py ./under_test/$1_tmp
cd ./under_test/$1_tmp

pip install pytest

[ -f requirements.txt ] && pip install -r requirements.txt

# Install package
[ -f myInstall.sh ] && bash ./myInstall.sh || pip install .
# Run tests
python filter_tests.py $(pwd) $2

cd ../..
source deactivate
rm -rf venvs/$venv
