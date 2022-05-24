# DynaPyt


## Installation

1- Install requirements:  
`pip install libcst`  
2- Run  
`pip install .`  
in the root directory.


## Instrumentation

To run the instrumentation on a single file:  
`python -m dynapyt.instrument.instrument --files <path to Python file> --analysis <analysis name>`  

To run the instrumentation on all files in a directory:  
`python -m dynapyt.run_instrumentation --directory <path to directory> --analysis <analysis name>`  


## Analysis

To run the analysis:  
`python -m dynapyt.run_analysis --entry <entry file (python)> --analysis <analysis name>`  
To instrument and run the analysis on a project:  
`python -m dynapyt.run_all --directory <directory of project> --entry <entry file (python)> --analysis <analysis name>`  
