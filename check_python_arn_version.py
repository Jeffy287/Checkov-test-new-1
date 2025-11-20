import os
import re

# Regex: matches ARNs ending with :<number>, but skips common Lambda Layer ARNs
pattern = re.compile(r'arn:aws:[^:]+:[^:]*:[^:]*:[^:]+:\d+$')

def is_lambda_layer_arn(arn: str) -> bool:
    # Lambda Layer ARNs have ':layer:' before the version, which is valid
    return ':layer:' in arn

def scan_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        for lineno, line in enumerate(f, 1):
            matches = pattern.findall(line)
            for arn in matches:
                if not is_lambda_layer_arn(arn):
                    print(f"Version-pinned ARN found in {filepath}:{lineno}: {arn}")

def main():
    for root, _, files in os.walk('.'):
        for fname in files:
            if fname.endswith('.py'):
                scan_file(os.path.join(root, fname))

if __name__ == "__main__":
    main()
