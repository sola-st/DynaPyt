# End-to-end Tests
This directory holds the projects and scripts used for testing DynaPyt end-to-end.
The `projects` directory contains the projects used for testing.
Each project should also have an `analysis` module from its root. For example, a project named `foo` should have `foo.analysis`, which is the analysis class used for the tests.
The `scripts` directory contains the scripts required to run the tests.

To run the end-to-end tests:
- Install `hatch` with `pip install hatch`.
- Run `hatch run end2end:run`.
- Since the execution does not use pytest, the success of the tests depend on the exit code of the previous step.