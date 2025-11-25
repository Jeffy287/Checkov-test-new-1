import os
import re
import json
import argparse

# Improved regex: detects :<number> at the end of ARN, regardless of whitespace/quote
VERSION_PATTERN = re.compile(r'arn:aws:[^"\']*:\d+\b')

# Directories to exclude from scan
EXCLUDED_DIRS = {'.venv', '.git', '__pycache__'}

def find_python_files(root_dir="."):
    py_files = []
    for root, dirs, files in os.walk(root_dir):
        # Exclude unwanted directories in-place
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for f in files:
            if f.endswith(".py"):
                py_files.append(os.path.join(root, f))
    return py_files

def scan_file_for_pinned_arns(file_path, logger=None):
    matches = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                found = VERSION_PATTERN.findall(line)
                if found:
                    matches.append((line_no, line.strip(), found))
    except (UnicodeDecodeError, PermissionError) as e:
        if logger:
            logger.write(f"Skipping unreadable file: {file_path} ({e})\n")
    return matches

def main():
    parser = argparse.ArgumentParser(description="Scan Python files for version-pinned ARNs.")
    parser.add_argument("directory", nargs="?", default=".", help="Root directory to scan (default: current directory)")
    args = parser.parse_args()
    
    # For local logging of unreadable files
    logger = open("scan_debug.log", "w", encoding="utf-8")

    py_files = find_python_files(args.directory)
    issues = []

    for py_file in py_files:
        matches = scan_file_for_pinned_arns(py_file, logger)
        for line_no, line, arns in matches:
            for arn in arns:
                issues.append({
                    "file": os.path.relpath(py_file, args.directory),
                    "line": line_no,
                    "msg": f"Version-pinned ARN detected: {arn}\n{line}"
                })

    with open("arn_results.json", "w", encoding="utf-8") as outfile:
        json.dump(issues, outfile, indent=2)

    logger.close()

    if issues:
        print(f"Found {len(issues)} version-pinned ARN(s): see arn_results.json for details.")
    else:
        print("No version-pinned ARNs found.")

if __name__ == "__main__":
    main()
