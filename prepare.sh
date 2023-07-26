#!/bin/bash
# $1: repo name
# $2: test directory in repository root
# $3: analysis name

[ -d venvs ] || mkdir venvs
[ -d under_test ] || mkdir under_test

python -m pip install --user virtualenv

# Create virtual environtment
venv=$1_$3_env
virtualenv --python 3.9.0 venvs/$venv
source venvs/$venv/bin/activate