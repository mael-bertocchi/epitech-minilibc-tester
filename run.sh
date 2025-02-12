#!/bin/bash

export LD_LIBRARY_PATH=. ; gcc -L. -lasm -fno-builtin -o test tests/test.c
export LD_PRELOAD=libasm.so ; ./test
rm -f test
