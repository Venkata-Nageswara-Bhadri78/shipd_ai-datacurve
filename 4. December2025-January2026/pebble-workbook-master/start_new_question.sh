#!/bin/bash

# This script creates a project directory with a solution file and a test file
# based on the specified language.
#
# Usage: ./create.sh <language> <entrypoint>
#
# Supported languages: Java, JavaScript, C++, Python

if [ "$#" -ne 2 ]; then
	echo "Usage: $0 <language> <entrypoint>"
	exit 1
fi

LANG="$1"
ENTRYPOINT="$2"
ID=$(uuidgen)

case "$LANG" in
	java)
		SEEDS_DIR="seeds/java"
		SOLUTION_FILE="Solution.java"
		TEST_FILE="Test.java"
		PROMPT_TEMPLATE="prompt_template.md"
		;;
	javascript)
		SEEDS_DIR="seeds/javascript"
		SOLUTION_FILE="solution.mjs"
		TEST_FILE="test.solution.mjs"
		PROMPT_TEMPLATE="prompt_template.md"
		;;
	cpp)
		SEEDS_DIR="seeds/cpp"
		SOLUTION_FILE="solution.cpp"
		TEST_FILE="test.cpp"
		PROMPT_TEMPLATE="prompt_template.md"
		;;
	python)
		SEEDS_DIR="seeds/python"
		SOLUTION_FILE="solution.py"
		TEST_FILE="test_solution.py"
		PROMPT_TEMPLATE="prompt_template.md"
		;;
	*)
		echo "Unsupported language: $LANG"
		exit 1
		;;
esac

# Check if seeds directory exists
if [ ! -d "$SEEDS_DIR" ]; then
	echo "Error: Seeds directory '$SEEDS_DIR' not found."
	exit 1
fi

# Check if the directory already exists
if [ -d "$ID" ]; then
	echo "Error: Directory '$ID' already exists. Aborting."
	exit 1
fi

# Create the project directory
mkdir "$ID" || { echo "Failed to create directory '$ID'."; exit 1; }

# Copy and process template files
sed "s/{entrypoint}/$ENTRYPOINT/g" "$SEEDS_DIR/$SOLUTION_FILE" > "$ID/$SOLUTION_FILE"
sed "s/{entrypoint}/$ENTRYPOINT/g" "$SEEDS_DIR/$TEST_FILE" > "$ID/$TEST_FILE"

# Copy the language-specific prompt template instead of creating a generic one
cp "$SEEDS_DIR/$PROMPT_TEMPLATE" "$ID/prompt.md"

echo "Project directory '$ID' created successfully."
echo "Created files:"
echo "  - $SOLUTION_FILE"
echo "  - $TEST_FILE"
echo "  - prompt.md"
echo "Directory: $ID"
