#!/bin/bash

cd ./test/PythonRepos/$1

exactTime=`date +%y%m%d%H%M%S`

printf "import pytest\n\npytest.main(['-n', '8', '--import-mode=importlib', '$(pwd)/tests/'])\n" > run_all_tests.py

if [ $2 = "original" ]; then
    pip install -r requirements.txt
    pip install .
    python run_all_tests.py #> ../../results/$1_original_${exactTime}_output.txt
else
    pip install -r requirements.txt

    python -m dynapyt.run_instrumentation --dir . --analysis $2

    pip install .

    python -m dynapyt.run_analysis --entry run_all_tests.py --analysis $2 #> ../../results/$1_$2_${exactTime}_output.txt
fi