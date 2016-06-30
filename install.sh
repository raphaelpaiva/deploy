#!/bin/bash

git submodule init
git submodule update --remote --recursive

python -m pip install -r requirements.txt
