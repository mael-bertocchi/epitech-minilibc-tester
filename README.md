# Epitech MiniLibC tester

This script is a simple tester for the MiniLibC project at Epitech.

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Options](#options)
- [How to write tests](#how-to-write-tests)
  - [Test File structure](#test-file-structure)
  - [Adding New Tests](#adding-new-tests)
  - [Test validation](#test-validation)
- [Continuous Integration Example](#continuous-integration-example)
- [Author](#author)

## Requirements

Before using this tester, make sure you have the following installed on your system:

- Python
- Gnu Compiler Collection
- Netwide Assembler
- Make

## Installation

Clone this repository into a `tester` folder located at the root of your project. It is essential to follow this directory structure:

```
.
├── Makefile
├── src
│    └── ...
└── tester
    └── script
    │    ├── execute.sh
    │    └── prepare.sh
    └── tests
    │    ├── schema.json
    │    ├── tests.json
    └── tester.py
```

> **Note**: If your project is set up correctly, your Makefile should compile the `libasm.so` library in the root of your project.

You may also need to install the `jsonschema` package for Python. You can achieve this by running the following command:

```bash
pip3 install jsonschema
```

## Usage

Run the tester using the following command:

```bash
python3 tester/tester.py
```

The tester will compile your project and execute the tests, displaying the results in the terminal.

## Options

The tester script accepts the following options:

- `-h` or `--help`: Display the help message.
- `-s` or `--skip-compile`: Skip the library compilation step.
- `-t` or `--test`: Specify a list of function to test. The tester will only run the tests for the specified functions.

## How to write tests

The tests are defined in the `tests.json` file and follow a specific schema to ensure consistency and correctness. You can find some examples already written in that file.

### Test File structure

- `name`: The name of the function to be tested.
- `args`: An array of argument objects, each containing:
  - `name`: The name of the argument.
  - `type`: The type of the argument.
- `result`: An object describing the expected result, containing:
  - `type`: The type of the result.
  - `flag`: The format flag used by printf to print the result.
- `tests`: An array of test cases, each containing:
  - `name`: The name of the test case.
  - `prerequisite`: An optional string containing the code to execute before the test. This code must not contain any function definition.
  - `input`: An array of input values for the function.
  - `expect`: The expected output of the function.

### Adding New Tests

To add new tests, follow these steps:

1. Open the `tests.json` file.
2. Add a new object to the array, following the structure defined above.
3. Define the function name, arguments, result type, and test cases.

### Test validation

By default, the function's return value is compared to the expected result.
If the function modifies a pointer instead of returning a value, you can set `catch_return_value` to `false` and name the pointer `var` to indicate that validation will check for pointer modification instead.

## Continuous Integration Example

You can use GitHub Actions to run the tester automatically on each push. Here is an example of a workflow file:

```yml
name: Build and test

env:
  TESTER_URL: "https://github.com/mael-bertocchi/epitech-minilibc-tester.git"

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

jobs:
  build_and_test:
    runs-on: ubuntu-latest
    container:
      image: epitechcontent/epitest-docker:latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Clone tester repository
        run: git clone $TESTER_URL tester

      - name: Build
        run: make
        timeout-minutes: 2

      - name: Test
        run: python3 tester/tester.py --skip-compile
        timeout-minutes: 5

      - name: Cleanup
        run: make fclean
```

## Author

- Mael Bertocchi
