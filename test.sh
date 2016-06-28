#!/bin/bash

if [ "$(expr substr $(uname -s) 1 10)" == "MINGW32_NT" ]; then
    PATH=$PATH:/c/Python27
fi

python -m unittest `ls *_tests.py | sed 's/\.py//g'`
