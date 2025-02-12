#!/bin/bash

# Compile the library
gcc -L. -lasm -fno-builtin -o test tester/test.c

# Export the library path
export LD_LIBRARY_PATH=.

# Export the library preload
export LD_PRELOAD=libasm.so

# Execute the test
./test

# Remove the executable
rm -f test
