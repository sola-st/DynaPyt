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

export PYTHONPATH="$PWD/venvs/$venv/lib/python3.9/site-packages"

exactTime=`date +%y%m%d%H%M%S`

# Install DynaPyt
pip install -r requirements.txt
pip install .

# Install requirements for package under test
cp -r ./test/PythonRepos/$1 ./under_test/$1_$3
cd ./under_test/$1_$3
printf "import pytest\n\npytest.main(['-n', '8', '--import-mode=importlib'" > run_all_tests.py
while read line; do
    printf ", '--deselect=$line'" >> run_all_tests.py
done < ../$1_tmp/filtered.txt
printf ", '$(pwd)/$2/'])\n" >> run_all_tests.py
[ -f requirements.txt ] && pip install -r requirements.txt

if [ $3 = "original" ]; then
    # Install package
    [ -f myInstall.sh ] && bash ./myInstall.sh || pip install .
    # Run tests
    python run_all_tests.py > $1_original_${exactTime}_output.txt
    tail -n 3 $1_original_${exactTime}_output.txt
else
    # Instrument code
    python -m dynapyt.run_instrumentation --dir . --analysis $3
    # Install package
    [ -f myInstall.sh ] && bash ./myInstall.sh || pip install .
    # Run tests
    python -m dynapyt.run_analysis --entry run_all_tests.py --analysis $3 > $1_$3_${exactTime}_output.txt
    tail -n 3 $1_$3_${exactTime}_output.txt
fi

cd ../..
source deactivate
rm -rf venvs/$venv
