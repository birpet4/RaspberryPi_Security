#!/bin/bash

echo '=== Compilation of source files'
for script in $( find . -name "*.py" );
do
    echo "Compiling: ${script}"
    python -m py_compile $script
done


echo '=== Running unit-tests'
pytest .
