from jsonschema import validate, ValidationError
from os import getcwd, remove, path
from json import load
import subprocess
import argparse

CWD = getcwd()

TEMPORARY_FILEPATH = f"{CWD}/tester/test.c"
RESULT_FILEPATH = f"{CWD}/tester/res.txt"
TESTS_FILEPATH = f"{CWD}/tester/tests/tests.json"
SCHEMA_FILEPATH = f"{CWD}/tester/tests/schema.json"
EXECUTER_FILEPATH = f"{CWD}/tester/script/execute.sh"
PREPARER_FILEPATH = f"{CWD}/tester/script/prepare.sh"

ERROR_LABEL = "\033[91mError\033[0m"
WARNING_LABEL = "\033[93mWarning\033[0m"
INFORMATION_LABEL = "\033[36mInformation\033[0m"

def validate_json(json_data, schema):
    try:
        validate(instance=json_data, schema=schema)
        print(f"{INFORMATION_LABEL}: The tests file is valid.")
    except ValidationError as e:
        print(f"{ERROR_LABEL}: The tests file contains an error: {e.message}")
        exit(1)

def load_json(filepath):
    with open(filepath, 'r') as file:
        return load(file)

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

def main():
    parser = argparse.ArgumentParser(description="Run specific sections of the test suite.")
    parser.add_argument('-s', '--section', nargs='+', help="Specify sections to run", required=False)
    parser.add_argument('--no-compile', action='store_true', help="Skip the preparation step", required=False)
    args = parser.parse_args()

    try:
        schema = load_json(SCHEMA_FILEPATH)
        tests_data = load_json(TESTS_FILEPATH)

        validate_json(tests_data, schema)
        sanitize_workspace()

        if not args.no_compile:
            subprocess.run(PREPARER_FILEPATH)
        else:
            print(f"{INFORMATION_LABEL}: Skipping the library (re)compilation.")

        if args.section:
            tests_data = [section for section in tests_data if section['name'] in args.section]

        if not tests_data:
            print(f"{ERROR_LABEL}: There is no section to run.")
            exit(1)

        report = execute_tests(tests_data)

        print("- Report:")
        for (section, passed, total) in report:
            percentage = int(passed / total * 100)
            print(f"\t{section:<40} {passed}/{total} ({percentage}%)")

    except FileNotFoundError as e:
        print(f"{ERROR_LABEL}: {e.strerror}: {e.filename}")
    except KeyboardInterrupt:
        print(f"\n{WARNING_LABEL}: Unexpected interruption.")

if __name__ == "__main__":
    main()
