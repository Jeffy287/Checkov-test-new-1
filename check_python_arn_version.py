import os
import re

# FIXED REGEX: matches ANY ARN ending with :<number>
VERSION_PATTERN = re.compile(
    r'arn:aws:[^"\']*:\d+(?=["\'\s])'
)

def find_python_files(root_dir="."):
    """Recursively collect all .py files."""
    py_files = []
    for root, _, files in os.walk(root_dir):
        for f in files:
            if f.endswith(".py"):
                py_files.append(os.path.join(root, f))
    return py_files

def scan_file_for_pinned_arns(file_path):
    """Return all version-pinned ARNs found in a file."""
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
    print("\nScanning Python files for version-pinned ARNs...\n")

    py_files = find_python_files(".")
    report = {}

    for py_file in py_files:
        matches = scan_file_for_pinned_arns(py_file)
        if matches:
            report[py_file] = matches

    if not report:
        print("No version-pinned ARNs found in any .py file.")
        return

    print("Version-pinned ARNs detected:\n")

    for file_path, entries in report.items():
        print(f"File: {file_path}")
        for line_no, line, arns in entries:
            print(f"  - Line {line_no}: {line}")
            for arn in arns:
                print(f"      -> {arn}")
        print()

    print("Recommendation: Remove version pinning from ARNs.\n")

if __name__ == "__main__":
    main()
