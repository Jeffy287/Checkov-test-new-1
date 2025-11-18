# Failing Lambda (bad) - ARN contains version pinning
resource "aws_lambda_function" "bad" {
  function_name = "test_bad"
  role          = "arn:aws:iam::123456789012:role/lambda-role:2" # <-- FAILS custom check
  handler       = "index.handler"
  runtime       = "python3.9"
  filename      = "lambda_function.zip"
}

# Passing Lambda (good) - ARN without version pinning
resource "aws_lambda_function" "good" {
  function_name = "test_good"
  role          = "arn:aws:iam::123456789012:role/lambda-role" # <-- PASSES custom check
  handler       = "index.handler"
  runtime       = "python3.9"
  filename      = "lambda_function.zip"
}
