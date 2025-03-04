from jsonschema import validate, ValidationError
from os import getcwd, remove, path
from json import load, JSONDecodeError
import subprocess
import argparse

CWD = getcwd()

TEMPORARY_FILEPATH = f"{CWD}/tester/test.c"
RESULT_FILEPATH = f"{CWD}/tester/res.txt"
TESTS_FILEPATH = f"{CWD}/tester/tests/tests.json"
SCHEMA_FILEPATH = f"{CWD}/tester/tests/schema.json"
EXECUTER_FILEPATH = f"{CWD}/tester/script/execute.sh"
COMPILER_FILEPATH = f"{CWD}/tester/script/compile.sh"

ERROR_LABEL = "\033[91mError:\033[0m"
WARNING_LABEL = "\033[93mWarning:\033[0m"
INFORMATION_LABEL = "\033[36mInformation:\033[0m"

def validate_JSON(json_data, schema):
    try:
        validate(instance=json_data, schema=schema)
        print(f"{INFORMATION_LABEL} The tests file is valid.")
    except ValidationError as e:
        print(f"{ERROR_LABEL} '{TESTS_FILEPATH}' contains an error: {e.message}")
        exit(1)

def open_JSON(filepath):
    try:
        with open(filepath, 'r') as file:
            return load(file)
    except JSONDecodeError as e:
        print(f"{ERROR_LABEL} '{filepath}' is not a valid JSON file: {e}")
        exit(1)

def create_prototype(return_type, name, args):
    args_str = ', '.join(f"{arg['type']} {arg['name']}" for arg in args)
    return f"{return_type} {name}({args_str})"

def create_function_call(name, inputs):
    inputs_str = ', '.join(inputs)
    return f"{name}({inputs_str})"

def sanitize_workspace():
    for file_path in [TEMPORARY_FILEPATH, RESULT_FILEPATH]:
        if path.exists(file_path):
            remove(file_path)

def execute_test(name, args, result, test):
    try:
        with open(TEMPORARY_FILEPATH, 'w') as file:
            function_call = create_function_call(name, test['input'])
            prototype = create_prototype(result['type'], name, args)

            catch_return_value = test.get('catch_return_value', True)
            prerequisite = test.get('prerequisite', '')

            begin_code = f"#include <unistd.h>\n#include <stdio.h>\n#include <fcntl.h>\nextern {prototype}; int main(void) {{ {prerequisite}; int fd = open(\"{RESULT_FILEPATH}\", O_WRONLY | O_CREAT, 0644);"
            if catch_return_value:
                specific_code = f"{result['type']} res = {function_call}; dprintf(fd, \"{result['flag']}\", res);"
            else:
                specific_code = f"{function_call}; dprintf(fd, \"{result['flag']}\", var);"
            end_code = "close(fd); return 0;}\n"

            file.write(begin_code + specific_code + end_code)
            file.close()

        subprocess.run(EXECUTER_FILEPATH)

        with open(RESULT_FILEPATH, 'r') as file:
            res = file.read().strip()
            if res != test['expect']:
                print(f"\tRunning {test['name']:<40} \033[91mKO\033[0m (Expected: '{test['expect']}', Got: '{res}')")
                return False
            else:
                print(f"\tRunning {test['name']:<40} \033[92mOK\033[0m")
                return True
    except Exception as e:
        print(f"\tRunning {test['name']:<40} \033[91mKO\033[0m (Error: {e})")
        return False

def execute_tests(tests_data):
    report = []

    for section in tests_data:
        passed = 0
        total = 0

        print(f"- Testing {section['name']}:")
        for test in section["tests"]:
            if execute_test(section['name'], section['args'], section['result'], test):
                passed += 1
            total += 1
            sanitize_workspace()
        report.append((section['name'], passed, total))
    return report

def create_report(report):
    success = True

    print("- Report:")
    for (section, passed, total) in report:
        percentage = int(passed / total * 100)
        print(f"\t{section:<40} {passed}/{total} ({percentage}%)")
        if passed != total:
            success = False
    if not success:
        exit(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--test', nargs='+', help="Specify a list of function to test", required=False)
    parser.add_argument('-s', '--skip-compile', action='store_true', help="Skip the library compilation step", required=False)
    args = parser.parse_args()

    try:
        schema = open_JSON(SCHEMA_FILEPATH)
        tests_data = open_JSON(TESTS_FILEPATH)

        validate_JSON(tests_data, schema)
        sanitize_workspace()

        if not args.skip_compile:
            subprocess.run(COMPILER_FILEPATH)
        else:
            print(f"{INFORMATION_LABEL} Skipping library compilation.")

        if args.test:
            tests_data = [test for test in tests_data if test['name'] in args.test]

        if not tests_data:
            print(f"{ERROR_LABEL} There is no section to run.")
            exit(1)

        report = execute_tests(tests_data)
        create_report(report)
    except FileNotFoundError as e:
        print(f"{ERROR_LABEL} {e.strerror}: {e.filename}")
    except KeyboardInterrupt:
        print(f"\n{WARNING_LABEL} Unexpected interruption.")

if __name__ == "__main__":
    main()
