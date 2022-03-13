# python-dynamic-analysis

Run `pip install .` in the root directory.
To run the instrumentation:
`python -m dynapyt.instrument.instrument --files <target file(s)> --analysis <analysis name>`
To run the analysis:
`python -m dynapyt.run_analysis --entry <entry file> --analysis <analysis name>`
To instrument and run the analysis on a project:
`python -m dynapyt.run_all --directory <directory of project> --entry <entry file> --analysis <analysis name>`