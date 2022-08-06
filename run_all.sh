#!/bin/bash
# $1: repo name
# $2: test directory in repository root
# $3: analysis name
cd ./test/PythonRepos/$1
#exactTime=`date +%y%m%d%H%M%S`

printf "import pytest\n\npytest.main(['-n', '8', '--import-mode=importlib', '$(pwd)/$2/'])\n" > run_all_tests.py
[ -f requirements.txt ] && pip install --user -r requirements.txt

if [ $3 = "original" ]; then
    [ -f myInstall.sh ] && bash ./myInstall.sh || pip install --user .
    python run_all_tests.py #> ../../results/$1_original_${exactTime}_output.txt
else
    python -m dynapyt.run_instrumentation --dir . --analysis $3
    pip show dynapyt
    [ -f myInstall.sh ] && bash ./myInstall.sh || pip install --user .

    python -m dynapyt.run_analysis --entry run_all_tests.py --analysis $3 #> ../../results/$1_$2_${exactTime}_output.txt
fi
