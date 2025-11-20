import os
import re

# Regex matches ARNs ending with a colon and number (version-pinned)
VERSION_PATTERN = re.compile(r'arn:aws:[^:]+:[^:]*:[^:]*:[^:]+:\d+$')

def is_lambda_layer_arn(arn: str) -> bool:
    # Lambda Layers have ':layer:' before the version - allow these
    return ":layer:" in arn

def scan_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            matches = VERSION_PATTERN.findall(line)
            for arn in matches:
                if not is_lambda_layer_arn(arn):
                    print(f"Version-pinned ARN found in {filepath}:{lineno}: {arn}")

def main():
    found = False
    for root, _, files in os.walk('.'):
        for fname in files:
            # Scan .py, .tf, .json, .yml, .yaml files
            if fname.endswith(('.py', '.tf', '.json', '.yml', '.yaml')):
                path = os.path.join(root, fname)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    matches = VERSION_PATTERN.findall(content)
                    for match in matches:
                        if not is_lambda_layer_arn(match):
                            found = True
                # Also rescan line by line for line numbers
                scan_file(path)
    if not found:
        print("No version-pinned ARNs found in scanned files.")

if __name__ == "__main__":
    main()
