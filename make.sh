#!/bin/bash

# ---------------------------------------------
echo '=== Compilation of source files'
errors=0

for script in $( find . -name "*.py" );
do
    echo 'Compiling: ' $script
    python -m py_compile $script

    if [ 0 -ne $? ]
    then
        ((errors=errors+1))
    fi
done

if [ 0 -ne $errors ]
then
    echo 'Failed to compile' $errors 'files'
	exit $errors
fi


# ---------------------------------------------
echo '=== Running unit-tests'
pytest .

# if no tests were found, don't fail
if [ 5 -eq $? ]
then
	exit 0
fi
