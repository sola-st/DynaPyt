# DynaPyt: A Dynamic Analysis Framework for Python
DynaPyt is a dynamic analysis framework designed and developed by [Aryaz Eghbali and Michael Pradel](https://2022.esec-fse.org/details/fse-2022-research-papers/48/DynaPyt-A-Dynamic-Analysis-Framework-for-Python). 
The framework provides hooks for a variety of runtime events in multiple layers of abstraction.
Users can create arbitrary dynamic analyses by implementing relevant hooks.
Beyond observing runtime behavior, DynaPyt also supports manipulation of behavior, e.g., to inject runtime values or modify branching decisions.

--------------------

## Installation

1) Install requirements:  
```
pip install libcst
```
2) Run  
```
pip install .
```
in the root directory.

--------------------

## Instrumentation

To run the instrumentation on a single file:  
```bash
python -m dynapyt.instrument.instrument --files <path to Python file> --analysis <analysis name>
```

To run the instrumentation on all files in a directory:  
```bash
python -m dynapyt.run_instrumentation --directory <path to directory> --analysis <analysis name>
```


## Analysis

To run the analysis:  
```bash
python -m dynapyt.run_analysis --entry <entry file (python)> --analysis <analysis name>
```

To instrument and run the analysis on a project:  
```bash
python -m dynapyt.run_all --directory <directory of project> --entry <entry file (python)> --analysis <analysis name>
```

--------------------

## Reproducing Results
To reproduce results from the paper, follow these instructions:  
We suggest running each experiment in a fresh Python environment.  

First, install DynaPyt using instructions above.

### Analyzing the Python projects (RQ1, RQ2, and RQ4)
For each project (for example `Textualize/rich`):
1) Clone the repository (or download the zip):
```
git clone https://github.com/Textualize/rich.git
cd rich
```
2) Instrument all files in the project (for original execution, skip this step):
```
python -m dynapyt.run_instrumentation --directory . --analysis TraceAll
```
3) Add entry file (`run_all_tests.py`) for running tests in the root directory:
```python
import pytest

pytest.main(['-n', '8', '--import-mode=importlib', './tests'])
```
Replace `'./tests'` with the path to test files in the project.  

4) Install the package (may need extra steps for other packages):
```
pip install .
```
5) Run tests:  
For running the analysis:
```
time python -m dynapyt.run_analysis --entry run_all_tests.py --analysis TraceAll
```
For running the original:
```
time python run_all_tests.py
```

### Running other analyses (RQ3)
To run other DynaPyt analyses, use the appropriate name (the class name) for `--analysis` in both instrumentation and analysis scripts.  

To run Python's `sys.settrace`:  
From the above instructions, follow step 1, skip step 2 and 3, run step 4, and then put the following code in `run_all_tests.py`:
```python
from sys import settrace
from trc import _trace_opcodes_ # or _trace_assignments_ or _trace_all_
import pytest

settrace(_trace_opcodes_)
pytest.main(['-n', '8', '--import-mode=importlib', './tests'])
```
Copy `src/nativetracer/trc.py` beside `run_all_tests.py`.  
Then run
```
time python run_all_tests.py
```



## Citation
To be added
