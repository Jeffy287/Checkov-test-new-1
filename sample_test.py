# Version-pinned IAM Role (should be flagged)
my_bad_role_arn = "arn:aws:iam::123456789012:role/lambda-role:6"

# Normal IAM Role (should NOT be flagged)
my_good_role_arn = "arn:aws:iam::123456789012:role/lambda-role"

# Lambda layer ARN (should NOT be flagged)
my_layer_arn = "arn:aws:lambda:us-east-1:123456789012:layer:my-layer:8"

# Random text (should not be flagged)
foo = "hello world"

# In a list (should be flagged if version-pinned)
role_arns = [
    "arn:aws:iam::123456789012:role/application-role:6",  # should be flagged
    "arn:aws:iam::123456789012:role/application-role"
]
