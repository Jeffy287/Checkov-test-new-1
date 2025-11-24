import os
import re
import json

# REGEX: matches ARN ending with :<number>
VERSION_PATTERN = re.compile(r'arn:aws:[^"\']*:[0-9]+(?=["\'\\s])')

def find_python_files(root_dir="."):
    py_files = []
    for root, _, files in os.walk(root_dir):
        for f in files:
            if f.endswith(".py"):
                py_files.append(os.path.join(root, f))
    return py_files

def scan_file_for_pinned_arns(file_path):
    matches = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                found = VERSION_PATTERN.findall(line)
                if found:
                    matches.append((line_no, line.strip(), found))
    except (UnicodeDecodeError, PermissionError):
        pass
    return matches

def main():
    py_files = find_python_files(".")
    issues = []

    for py_file in py_files:
        matches = scan_file_for_pinned_arns(py_file)
        for line_no, line, arns in matches:
            for arn in arns:
                issues.append({
                    "file": os.path.relpath(py_file, "."),
                    "line": line_no,
                    "msg": f"Version-pinned ARN detected: {arn}\n{line}"
                })

    # Write output (JSON array)
    with open("arn_results.json", "w", encoding="utf-8") as outfile:
        json.dump(issues, outfile, indent=2)

    # Optional: console messages for local debugging
    if issues:
        print(f"Found {len(issues)} version-pinned ARN(s): see arn_results.json for details.")
    else:
        print("No version-pinned ARNs found.")

if __name__ == "__main__":
    main()
