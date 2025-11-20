import os
import re

# Regex: matches ARNs ending with :<number>, skips common Lambda Layer ARNs
VERSION_PATTERN = re.compile(r'arn:aws:[^:]+:[^:]*:[^:]*:[^:]+:\d+$')

def is_lambda_layer_arn(arn: str) -> bool:
    # Lambda Layer ARNs have ':layer:' before the version, which is OK
    return ':layer:' in arn

def scan_file(filepath):
    found = False
    with open(filepath, 'r', encoding='utf-8') as f:
        for lineno, line in enumerate(f, 1):
            matches = VERSION_PATTERN.findall(line)
            for arn in matches:
                if not is_lambda_layer_arn(arn):
                    print(f"Version-pinned ARN found in {filepath}:{lineno}: {arn}")
                    found = True
    return found

def main():
    found_any = False
    for root, _, files in os.walk('.'):
        for fname in files:
            # Scan typical code and config files; add/remove extensions as needed
            if fname.endswith(('.py', '.tf', '.json', '.yml', '.yaml')):
                path = os.path.join(root, fname)
                if scan_file(path):
                    found_any = True
    if not found_any:
        print("No version-pinned ARNs found in scanned files.")

if __name__ == "__main__":
    main()
