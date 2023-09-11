# Tutorial
This is the tutorial page for ASE 2023.
Slides: [Google slides](https://docs.google.com/presentation/d/14eeGZm4gIznsqtAEYI5o5Ayyp2vRepdKzUTjFTksJaI/edit?usp=sharing)

Table of contents:
- Task 0: [Setup](#setup)
- Task 1: [Getting started](#getting-started)
- Task 2: [Branch coverage](#branch-coverage)
- Task 3: [Dynamic call graph](#dynamic-call-graph)
- Task 4: [Analysis hook hierarchy](#hook-hierarchy)
- Task 5: [Modify execution](#modify-execution)

## Setup
To isolate the packages that you install during this tutorial either [use Docker](#docker), or [use a virtual environment](#virtual-environment).

### Docker
1. Install Docker (if it is your first time using Docker, [Docker Desktop](https://docs.docker.com/desktop/) is recommended)
2. Build the image: `docker build -t dynapyt_tutorial .`
3. Run bash in the container: `docker run -it dynapyt_tutorial /bin/bash`

### Virtual Environment
1. Install virtual environment: 
   - With pipx: `pipx install virtualenv`
   - With pip: `python -m pip install --user virtualenv`
2. Create a directory for the virtual environment: `mkdir ~/.dynapyt_virtualenv`
3. Create the virtual environment: `virtualenv dynapyt_virtualenv ~/.dynapyt_virtualenv`
4. Activate the virtual environment: `source ~/.dynapyt_virtualenv/bin/activate`

## Getting Started

### Install DynaPyt
- Install the latest release:
    ```bash
    pip install dynapyt
    ```
    Or
- Install from source: 
    ```bash
    git clone https://github.com/sola-st/DynaPyt.git
    cd DynaPyt
    pip install .
    ```


### First Instrumentation
```bash
python -m dynapyt.run_instrumentation \
 --analysis dynapyt.analyses.TraceAll.TraceAll \
 --directory task1
```
- Checkout the instrumented code in `task1/main.py` and compare it to the original code in `task1/main.py.orig`.
- Checkout the metadata file `task1/main-dynapyt.json`.

### First Analysis
```bash
python -m dynapyt.run_analysis \
 --analysis dynapyt.analyses.TraceAll.TraceAll \
 --entry task1/main.py
```
- Checkout the [TraceAll analysis](https://github.com/sola-st/DynaPyt/blob/main/src/dynapyt/analyses/TraceAll.py). 

## Branch Coverage
Generate a log of branches taken and their truth values.

### Implement the analysis
1. Create a file under `tutorial-analyses/src/tutorial_analyses` called `BranchCoverageAnalysis.py`.
2. Implement the analysis class as a subclass of `dynapyt.analyses.BaseAnalysis`.
3. Build the analysis: `pip install ./tutorial-analyses`

### Instrument the code
```bash
python -m dynapyt.run_instrumentation \
 --analysis tutorial_analyses.BranchCoverageAnalysis.BranchCoverageAnalysis \
 --directory task2
```

### Run the analysis
```bash
python -m dynapyt.run_analysis \
 --analysis tutorial_analyses.BranchCoverageAnalysis.BranchCoverageAnalysis \
 --entry task2/main.py
```

## Dynamic Call Graph
Generate the graph of dynamic function calls.

### Implement the analysis
1. Create a file under `tutorial-analyses/src/tutorial_analyses` called `CallGraphAnalysis.py`.
2. Implement the analysis class as a subclass of `dynapyt.analyses.BaseAnalysis`.
3. Build the analysis: `pip install ./tutorial-analyses`

### Instrument the code
```bash
python -m dynapyt.run_instrumentation \
 --analysis tutorial_analyses.CallGraphAnalysis.CallGraphAnalysis \
 --directory task3
```

### Run the analysis
```bash
python -m dynapyt.run_analysis \
 --analysis tutorial_analyses.CallGraphAnalysis.CallGraphAnalysis \
 --entry task3/main.py
```

## Hook Hierarchy
String concatenation with `+=` is slower than `"".join()`. Find cases that a string gets appended in a loop.

### Implement the analysis
1. Create a file under `tutorial-analyses/src/tutorial_analyses` called `SlowStringConcatAnalysis.py`.
2. Implement the analysis class as a subclass of `dynapyt.analyses.BaseAnalysis`.
3. Build the analysis: `pip install ./tutorial-analyses`

### Instrument the code
```bash
python -m dynapyt.run_instrumentation \
 --analysis tutorial_analyses.SlowStringConcatAnalysis.SlowStringConcatAnalysis \
 --directory task4
```

### Run the analysis
```bash
python -m dynapyt.run_analysis \
 --analysis tutorial_analyses.SlowStringConcatAnalysis.SlowStringConcatAnalysis \
 --entry task4/main.py
```

## Modify Execution
Force the execution to always take the opposite branch.

### Implement the analysis
1. Create a file under `tutorial-analyses/src/tutorial_analyses` called `OppositeBranchAnalysis.py`.
2. Implement the analysis class as a subclass of `dynapyt.analyses.BaseAnalysis`.
3. Build the analysis: `pip install ./tutorial-analyses`

### Instrument the code
```bash
python -m dynapyt.run_instrumentation \
 --analysis tutorial_analyses.OppositeBranchAnalysis.OppositeBranchAnalysis \
 --directory task5
```

### Run the analysis
```bash
python -m dynapyt.run_analysis \
 --analysis tutorial_analyses.OppositeBranchAnalysis.OppositeBranchAnalysis \
 --entry task5/main.py
```
