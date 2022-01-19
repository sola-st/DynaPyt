# python-dynamic-analysis

Run `pip install .` in the root directory.
To run the instrumentation:
`python -m dynapyt.instrument.instrument --files <target file(s)> --analysis <analysis file name>`
To run the analysis:
`python -m dynapyt.run_analysis --entry <entry module (X.y)> --analysis <analysis file name>`