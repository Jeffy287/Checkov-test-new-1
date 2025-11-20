# KMS key for Lambda environment variable encryption
resource "aws_kms_key" "lambda_env_encryption" {
  description          = "KMS key for Lambda env encryption"
  enable_key_rotation  = true
  policy               = <<EOF
{
  "Version": "2012-10-17",
  "Id": "key-default-1",
  "Statement": [
    {
      "Sid": "Enable IAM User Permissions",
      "Effect": "Allow",
      "Principal": { "AWS": "*" },
      "Action": "kms:*",
      "Resource": "*"
    }
  ]
}
EOF
}

# KMS key for SQS encryption
resource "aws_kms_key" "sqs_encryption" {
  description          = "KMS key for SQS encryption"
  enable_key_rotation  = true
  policy               = <<EOF
{
  "Version": "2012-10-17",
  "Id": "key-default-1",
  "Statement": [
    {
      "Sid": "Enable IAM User Permissions",
      "Effect": "Allow",
      "Principal": { "AWS": "*" },
      "Action": "kms:*",
      "Resource": "*"
    }
  ]
}
EOF
}

# SQS Dead Letter Queue (DLQ)
resource "aws_sqs_queue" "my_dlq" {
  name              = "my-dlq-queue"
  kms_master_key_id = aws_kms_key.sqs_encryption.arn
}

# Lambda code signing config
resource "aws_lambda_code_signing_config" "example" {
  allowed_publishers {
    signing_profile_version_arns = ["arn:aws:signer:us-east-1:123456789012:signing-profile/example/00000000000000000000000000000000"]
  }
  policies {
    untrusted_artifact_on_deployment = "Enforce"
  }
}

# VPC networking resources (replace with your own IDs)
resource "aws_subnet" "example" {
  vpc_id            = "vpc-xxxxxxx"
  cidr_block        = "10.0.0.0/24"
  availability_zone = "us-east-1a"
}

resource "aws_security_group" "example" {
  name        = "lambda-sg"
  description = "Security group for Lambda"
  vpc_id      = "vpc-xxxxxxx"
}

# IAM Role for Lambda (no version-pinned ARN)
resource "aws_iam_role" "lambda_exec" {
  name = "lambda_exec_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Principal = { Service = "lambda.amazonaws.com" }
      Effect    = "Allow"
      Sid       = ""
    }]
  })
}

# Lambda function (passes all checks)
resource "aws_lambda_function" "good" {
  function_name    = "good-lambda"
  s3_bucket        = "example-bucket"
  s3_key           = "example-key"
  handler          = "index.handler"
  runtime          = "python3.12"
  role             = aws_iam_role.lambda_exec.arn
  kms_key_arn      = aws_kms_key.lambda_env_encryption.arn
  code_signing_config_arn = aws_lambda_code_signing_config.example.arn
  reserved_concurrent_executions = 5

  # DLQ configuration
  dead_letter_config {
    target_arn = aws_sqs_queue.my_dlq.arn
  }

  # VPC configuration
  vpc_config {
    subnet_ids         = [aws_subnet.example.id]
    security_group_ids = [aws_security_group.example.id]
  }

  # X-Ray tracing
  tracing_config {
    mode = "Active"
  }

  environment {
    variables = {
      foo = "bar"
    }
  }
}
