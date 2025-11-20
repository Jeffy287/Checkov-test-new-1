resource "aws_lambda_function" "good" {
  function_name = "good-lambda"
  s3_bucket     = "example-bucket"
  s3_key        = "example-key"
  handler       = "index.handler"
  runtime       = "python3.12"
  role          = aws_iam_role.lambda_exec.arn

  # Ensure DLQ is set
  dead_letter_config {
    target_arn = "arn:aws:sqs:us-east-1:123456789012:my-dlq-queue"
  }

  # VPC configuration (required by CKV_AWS_117)
  vpc_config {
    subnet_ids         = [aws_subnet.example.id]
    security_group_ids = [aws_security_group.example.id]
  }

  # X-Ray tracing (required by CKV_AWS_50)
  tracing_config {
    mode = "Active"
  }

  # Concurrency limit (required by CKV_AWS_115)
  reserved_concurrent_executions = 5

  # Code signing config (required by CKV_AWS_272)
  code_signing_config_arn = aws_lambda_code_signing_config.example.arn

  environment {
    variables = {
      foo = "bar"
    }
  }
}

resource "aws_iam_role" "lambda_exec" {
  name = "lambda_exec_role"
  assume_role_policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [{
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }]
  })
}

resource "aws_sqs_queue" "my_dlq" {
  name = "my-dlq-queue"
}

resource "aws_lambda_code_signing_config" "example" {
  allowed_publishers {
    signing_profile_version_arns = ["arn:aws:signer:us-east-1:123456789012:signing-profile/example/00000000000000000000000000000000"]
  }
  policies {
    untrusted_artifact_on_deployment = "Enforce"
  }
}

resource "aws_subnet" "example" {
  # Fill in real values for your network
  vpc_id            = "vpc-xxxxxxx"
  cidr_block        = "10.0.0.0/24"
  availability_zone = "us-east-1a"
}

resource "aws_security_group" "example" {
  name        = "lambda-sg"
  description = "Security group for Lambda"
  vpc_id      = "vpc-xxxxxxx"
}
