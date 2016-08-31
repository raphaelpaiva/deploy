#!/bin/bash

for f in `git ls-files */*.py | grep -v _tests\.py`; do
    python -m pep8 $f;
done

