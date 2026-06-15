#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <directory_id> <language>"
    exit 1
fi

ID="$1"
LANG="$2"

# Check if directory exists
if [ ! -d "$ID" ]; then
    echo "Error: Directory '$ID' not found."
    exit 1
fi

case "$LANG" in
    java)
        echo "Running Java tests..."
        docker run --rm \
            -v "$(pwd)/$ID:/app" \
            java-test-runner
        ;;
    python)
        echo "Running Python tests..."
        docker run --rm \
            -v "$(pwd)/$ID:/app" \
            python-test-runner
        ;;
    javascript)
        echo "Running JavaScript tests..."
        docker run --rm \
            -v "$(pwd)/$ID:/app" \
            javascript-test-runner
        ;;
    cpp)
        echo "Running C++ tests..."
        docker run --rm \
            -v "$(pwd)/$ID:/app" \
            cpp-test-runner
        ;;
    *)
        echo "Unsupported language: $LANG. Currently supporting: java, python, javascript, cpp"
        exit 1
        ;;
esac 