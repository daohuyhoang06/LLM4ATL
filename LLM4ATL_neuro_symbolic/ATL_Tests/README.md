# ATL Tests

This module contains example transformations written in the **ATLAS Transformation Language (ATL)** and corresponding JUnit tests.  The examples illustrate how to convert models between different metamodels (for instance mapping Amalthea tasks to ASCET tasks, mapping family members to persons, and converting network structures to graphs).

## Structure

- `src/main/atl/` – ATL modules (`*.atl`) that implement the model transformations.  Each transformation defines matched rules and helpers to map concepts between source and target metamodels.
- `src/test/java/` – JUnit test cases that execute the ATL transformations and verify structural and semantic properties of the generated models.

## Building and running

Run the Python test driver from this directory:

```sh
python run_all_tests.py
```

The driver reads the parser report, copies each valid ATL module into `src/main/atl/`, runs the corresponding JUnit test through Maven, and writes the result summaries. The tests load the input models, run the ATL transformation via the Eclipse ATL engine and then assert that the output models meet the expected conditions (for example that elements have been created and attributes mapped correctly).

Consult the test classes for details on how each scenario is configured.
