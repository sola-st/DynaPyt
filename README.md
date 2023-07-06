# DynaPyt: A Dynamic Analysis Framework for Python
DynaPyt is a dynamic analysis framework designed and developed by [Aryaz Eghbali and Michael Pradel](https://2022.esec-fse.org/details/fse-2022-research-papers/48/DynaPyt-A-Dynamic-Analysis-Framework-for-Python). 
The framework provides hooks for a variety of runtime events in multiple layers of abstraction.
Users can create arbitrary dynamic analyses by implementing relevant hooks.
Beyond observing runtime behavior, DynaPyt also supports manipulation of behavior, e.g., to inject runtime values or modify branching decisions.

--------------------

## Installation

### Installation with pip

Run
```
pip install dynapyt
```

### Installation from source

1) Download source:
```
git clone https://github.com/sola-st/DynaPyt.git
```
2) Install requirements:  
```
pip install libcst
# or
cd DynaPyt
pip install -r requirements.txt
```
3) Install DynaPyt:  
```
cd DynaPyt
pip install .
```


--------------------

## Implementing an Analysis

An analysis is a subclass of BaseAnalysis. See the [analysis folder](src/dynapyt/analyses) for examples. To add your own analysis, add a file with a new analysis class to this folder. The name of the class is refered to as \<analysis name\> below.

## Instrumenting Python Code

**Note:** DynaPyt instruments code in-place (it keeps a `.py.orig` for each file it instruments to keep the original code). But for more convenience in analyzing, we suggest to instrument a copy of the code under analysis.  
To run the instrumentation on a single file:  
```
python -m dynapyt.instrument.instrument --files <path to Python file> --analysis <analysis class full dotted path>
```

To run the instrumentation on all files in a directory:  
```
python -m dynapyt.run_instrumentation --directory <path to directory> --analysis <analysis class full dotted path>
```

Note that instrumented files might not be portable.


## Running an Analysis

To run an analysis:  
```
python -m dynapyt.run_analysis --entry <entry file (python)> --analysis <analysis class full dotted path>
```

**Note:** The analysis name should either match the analysis name used for the instrumentation, or the analysis should have a subset of hooks used in the instrumentation analysis.

Single command to instrument and run an analysis on a project:  
```
python -m dynapyt.run_all --directory <directory of project> --entry <entry file (python)> --analysis <analysis class full dotted path>
```

## Available Hooks

Check out [this auto-generated API reference](https://sola-st.github.io/DynaPyt/) for available hooks.

--------------------

## Reproducing the Results in the Paper

To reproduce results from the paper, follow these instructions:  
We suggest running each experiment in a fresh Python environment.  

First, install DynaPyt using the instructions above.

### Analyzing the Python Projects (RQ1, RQ2, and RQ4)

**Option 1-** Run using the `experiment.sh` script:  
First, download the desired project from GitHub (`git clone ...`), and put it under `./test/PythonRepos/<package name>`.  
Then, if the project can be installed with just `pip install .`, ignore this step and move to the next. Otherwise, place a `myInstall.sh` script in the root directory of the project with all steps required for installing the package.  
Finally, run
```
bash ./experiment.sh <package name> <test directory> <analysis class full dotted path>
# E.g. for "rich" repository located at test/PythonRepos/rich:
bash ./experiment.sh rich test TraceAll
```
to run the analysis, or
```
bash ./experiment.sh <package name> <test directory> original
```
to run the original code (uninstrumented and unanalyzed).

**Option 2-** Run manually:
For each project (for example `Textualize/rich`):
1) Clone the repository (or download the zip):
```
git clone https://github.com/Textualize/rich.git
cd rich
```
2) Instrument all files in the project (for original execution, skip this step):
```
python -m dynapyt.run_instrumentation --directory . --analysis dynapyt.analyses.TraceAll.TraceAll
```
3) Add an entry file (`run_all_tests.py`) that runs all tests into the root directory:
```python
import pytest

pytest.main(['-n', '8', '--import-mode=importlib', './tests'])
```
Replace `'./tests'` with the path to test files in the project.

4) Install the package of the project-under-analysis (may need extra steps for other packages):
```
pip install .
```
5) Run tests:  
For running the analysis:
```
time python -m dynapyt.run_analysis --entry run_all_tests.py --analysis dynapyt.analyses.TraceAll.TraceAll
```

To replicate the results for the original execution (not instrumented and analyzed through DynaPyt), perform steps 1, 3, and 4. Then run
```
python run_all_tests.py
```

### Running Other Analyses (RQ3)
**DynaPyt Analyses**  
To run other DynaPyt analyses, use the appropriate name (the class name) for `--analysis` in both the instrumentation and the analysis scripts.  

**Python's built-in trace**  
To run Python's `sys.settrace` (used as a baseline in the paper):  
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

--------------------
## Citation

Please refer to DynaPyt via our FSE'22 paper:

```
@InProceedings{fse2022-DynaPyt,
  author    = {Aryaz Eghbali and Michael Pradel},
  title     = {Dyna{P}yt: A Dynamic Analysis Framework for {P}ython},
  booktitle = {{ESEC/FSE} '22: 30th {ACM} Joint European Software Engineering Conference and Symposium on the Foundations of Software Engineering},
  year      = {2022},
  publisher = {{ACM}},
}
```
