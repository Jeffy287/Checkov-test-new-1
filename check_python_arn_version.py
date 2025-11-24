import os
import re
import json

# FIXED REGEX: matches ANY ARN ending with :<number>
VERSION_PATTERN = re.compile(r'arn:aws:[^"\']*:\d+(?=["\'\s])')

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
                    for arn in found:
                        matches.append({
                            "file": file_path,
                            "line": line_no,
                            "issue": f"Version-pinned ARN found: {arn}"
                        })
    except (UnicodeDecodeError, PermissionError):
        pass
    return matches

def main():
    py_files = find_python_files(".")
    failures = []
    for py_file in py_files:
        failures.extend(scan_file_for_pinned_arns(py_file))
    output = {"failures": failures}
    with open("pyarn-report.json", "w") as f:
        json.dump(output, f, indent=2)
    if failures:
        print(f"Version-pinned ARNs detected in {len(failures)} place(s):")
        for fail in failures:
            print(f"- {fail['file']}:{fail['line']} | {fail['issue']}")
        print("\nRecommendation: Remove version pinning from ARNs.")
    else:
        print("No version-pinned ARNs found in any .py file.")

if __name__ == "__main__":
    main()
