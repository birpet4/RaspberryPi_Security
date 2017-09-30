#!/bin/bash

for script in $( find . -name "*.py" );
do
    echo "Compiling: ${script}"
    python -m py_compile $script
done