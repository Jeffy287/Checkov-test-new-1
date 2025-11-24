####################
# Lambda Function
####################
# Added this comment to trigger a change in the diff--enables Checkov inline review
resource "aws_lambda_function" "bad_lambda" {
  function_name = "bad_lambda"
  role          = "arn:aws:iam::123456789012:role/lambda-role:2" # Fails: ':2' version
  handler       = "main.handler"   # ← CHANGED FROM "index.handler"!
  runtime       = "python3.9"
  filename      = "lambda.zip"
}

resource "aws_lambda_function" "good_lambda" {
  function_name = "good_lambda"
  role          = "arn:aws:iam::123456789012:role/lambda-role" # Passes: no version
  handler       = "index.handler"
  runtime       = "python3.9"
  filename      = "lambda.zip"
}

####################
# ECS Task Definition
####################
resource "aws_ecs_task_definition" "bad_ecs" {
  family                   = "bad_ecs"
  execution_role_arn       = "arn:aws:iam::123456789012:role/ecs-role:11" # Fails: ':11' version
  container_definitions    = "[]" # Simplified for example
}

resource "aws_ecs_task_definition" "good_ecs" {
  family                   = "good_ecs"
  execution_role_arn       = "arn:aws:iam::123456789012:role/ecs-role" # Passes: no version
  container_definitions    = "[]"
}

####################
# Batch Job Definition
####################
resource "aws_batch_job_definition" "bad_batch" {
  name = "bad_batch"
  type = "container"
  role = "arn:aws:iam::123456789012:role/batch-role:5" # Fails: ':5' version
}

resource "aws_batch_job_definition" "good_batch" {
  name = "good_batch"
  type = "container"
  role = "arn:aws:iam::123456789012:role/batch-role" # Passes: no version
}

####################
# Auto Scaling Group
####################
resource "aws_autoscaling_group" "bad_asg" {
  name                    = "bad_asg"
  service_linked_role_arn = "arn:aws:iam::123456789012:role/asg-role:8" # Fails: ':8' version
}

resource "aws_autoscaling_group" "good_asg" {
  name                    = "good_asg"
  service_linked_role_arn = "arn:aws:iam::123456789012:role/asg-role" # Passes: no version
}

####################
# Launch Template
####################
resource "aws_launch_template" "bad_lt" {
  name                  = "bad_lt"
  iam_instance_profile  = "arn:aws:iam::123456789012:instance-profile/launch-profile:6" # Fails: ':6' version
}

resource "aws_launch_template" "good_lt" {
  name                  = "good_lt"
  iam_instance_profile  = "arn:aws:iam::123456789012:instance-profile/launch-profile" # Passes: no version
}

####################
# Lambda Layer Version
####################
resource "aws_lambda_layer_version" "bad_layer" {
  layer_name            = "bad_layer"
  compatible_runtimes   = ["python3.9"]
  filename              = "layer.zip"
  # Layer ARN with version
  arn                   = "arn:aws:lambda:us-east-1:123456789012:layer:custom-layer:9" # Fails: ':9' version
}

resource "aws_lambda_layer_version" "good_layer" {
  layer_name            = "good_layer"
  compatible_runtimes   = ["python3.9"]
  filename              = "layer.zip"
  # Layer ARN without version
  arn                   = "arn:aws:lambda:us-east-1:123456789012:layer:custom-layer" # Passes: no version
}

####################
# Step Functions State Machine
####################
resource "aws_sfn_state_machine" "bad_sfn" {
  name     = "bad_sfn"
  role_arn = "arn:aws:iam::123456789012:role/sfn-role:7" # Fails: ':7' version
  definition = jsonencode({
    States = {
      LambdaTask = {
        Type     = "Task"
        Resource = "arn:aws:lambda:us-east-1:123456789012:function:my-fn:5" # Fails: ':5' version inside definition
        End      = true
      }
    }
    StartAt = "LambdaTask"
  })
}

resource "aws_sfn_state_machine" "good_sfn" {
  name     = "good_sfn"
  role_arn = "arn:aws:iam::123456789012:role/sfn-role" # Passes: no version
  definition = jsonencode({
    States = {
      LambdaTask = {
        Type     = "Task"
        Resource = "arn:aws:lambda:us-east-1:123456789012:function:my-fn" # Passes: no version inside definition
        End      = true
      }
    }
    StartAt = "LambdaTask"
  })
}
