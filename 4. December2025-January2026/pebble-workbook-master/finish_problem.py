#!/usr/bin/env python3

import sys
import os
import csv

# Map of supported languages and their file extensions
LANGUAGE_EXTENSIONS = {
    'cpp': '.cpp',
    'python': '.py',
    'javascript': '.js',
    'java': '.java'
}

def read_file_content(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""

def find_solution_file(base_path):
    for lang, ext in LANGUAGE_EXTENSIONS.items():
        solution_path = os.path.join(base_path, f"solution{ext}")
        test_path = os.path.join(base_path, f"test{ext}")
        if os.path.exists(solution_path):
            return solution_path, test_path, lang
    return None, None, None

def bundle_problem(target_uuid):
    # Define paths
    base_path = target_uuid
    prompt_path = os.path.join(base_path, "prompt.md")
    
    # Find the correct solution and test files
    solution_path, test_path, lang = find_solution_file(base_path)
    
    if not solution_path:
        print(f"❌ No solution file found in supported languages")
        sys.exit(1)
    
    # Read contents
    prompt = read_file_content(prompt_path)
    solution = read_file_content(solution_path)
    test = read_file_content(test_path)
    
    # Create CSV
    output_file = f"{target_uuid}_bundle.csv"
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        # Write header
        writer.writerow(['id', 'language', 'prompt', 'solution', 'test'])
        # Write data
        writer.writerow([target_uuid, lang, prompt, solution, test])
    
    print(f"✅ Bundle created: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python bundle_problem.py <uuid>")
        sys.exit(1)
    
    uuid = sys.argv[1]
    if not os.path.exists(uuid):
        print(f"❌ Directory {uuid} not found")
        sys.exit(1)
        
    bundle_problem(uuid) 