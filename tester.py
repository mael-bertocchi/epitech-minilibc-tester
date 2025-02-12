from jsonschema import validate, ValidationError
from os import getcwd, remove
from json import load
import subprocess

CWD = getcwd()

TEMPORARY_FILEPATH = f"{CWD}/tests/test.c"
RESULT_FILEPATH = f"{CWD}/tests/res.txt"
TESTS_FILEPATH = f"{CWD}/tests/tests.json"
RUN_SCRIPT_FILEPATH = f"{CWD}/tests/run.sh"
SCHEMA_FILEPATH = f"{CWD}/tests/schema.json"

def validate_json(json_data, schema):
    try:
        validate(instance=json_data, schema=schema)
        print("The tests file is valid.")
    except ValidationError as e:
        print(f"The tests file contains an error: {e.message}")
        exit(1)

def load_json(filepath):
    with open(filepath, 'r') as file:
        return load(file)

def create_prototype(return_type, function_name, args):
    args_str = ', '.join(f"{arg['type']} {arg['name']}" for arg in args)
    return f"{return_type} {function_name}({args_str})"

def create_function(function_name, inputs):
    inputs_str = ', '.join(inputs)
    return f"{function_name}({inputs_str})"

def execute_test(name, args, result, test):
    with open(TEMPORARY_FILEPATH, 'w') as file:
        file.write("#include <unistd.h>\n")
        file.write("#include <stdio.h>\n")
        file.write("#include <fcntl.h>\n")

        prototype = create_prototype(result['type'], name, args)

        file.write(f"extern {prototype};")

        func = create_function(name, test['input'])

        file.write(f"int main(void) {{ int fd = open(\"{RESULT_FILEPATH}\", O_WRONLY | O_CREAT, 0644); {result['type']} res = {func}; dprintf(fd, \"{result['flag']}\", res); close(fd); return 0; }}\n")
        file.close()

    subprocess.run(RUN_SCRIPT_FILEPATH)

    with open(RESULT_FILEPATH, 'r') as file:
        res = file.read()
        if res != test['expect']:
            print(f"\tRunning {test['name']:<40} \033[91mKO\033[0m (Expected: '{test['expect']}', Got: '{res}')")
        else:
            print(f"\tRunning {test['name']:<40} \033[92mOK\033[0m")

    remove(TEMPORARY_FILEPATH)
    remove(RESULT_FILEPATH)

def main():
    try:
        schema = load_json(SCHEMA_FILEPATH)
        tests_data = load_json(TESTS_FILEPATH)

        validate_json(tests_data, schema)

        subprocess.run(["make", "re", "--silent"])

        for section in tests_data:
            print(f"Testing '{section['name']}'")
            for test in section["tests"]:
                execute_test(section['name'], section['args'], section['result'], test)
    except FileNotFoundError as e:
        print(f"{e.strerror}: {e.filename}")
    except KeyboardInterrupt:
        print("\nUnexpected interruption.")

if __name__ == "__main__":
    main()
