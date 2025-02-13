#!/bin/bash

# Compile the library
gcc -o test tester/test.c -Wall -Wextra -fno-builtin

LD_PRELOAD=./libasm.so ./test

# Remove the executable
rm -f test
