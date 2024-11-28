# Lambda execution role
resource "aws_iam_role" "c14_team_growth_lambda_role" {
  name               = "c14-team-growth-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role_policy.json
}

data "aws_iam_policy_document" "lambda_assume_role_policy" {
  statement {
    actions   = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy_attachment" "lambda_policy" {
  role       = aws_iam_role.c14_team_growth_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_vpc_access" {
  role       = aws_iam_role.c14_team_growth_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

# RDS IAM Policy Document (this grants permissions to connect to RDS)
data "aws_iam_policy_document" "lambda_rds_access" {
  statement {
    effect    = "Allow"
    actions   = ["rds:DescribeDBInstances", "rds:DescribeDBClusters"]
    resources = ["*"]
  }

  statement {
    effect    = "Allow"
    actions   = ["rds-db:connect"]
    resources = ["*"]
  }
}

# Attach RDS Policy to Lambda Role
resource "aws_iam_role_policy" "lambda_rds_access" {
  name   = "c14-team-growth-lambda-rds-policy"
  role   = aws_iam_role.c14_team_growth_lambda_role.id
  policy = data.aws_iam_policy_document.lambda_rds_access.json
}

# Lambda function (removed VPC-specific configurations)
resource "aws_lambda_function" "c14_team_growth_lambda" {
  function_name = "c14-team-growth-lambda"
  role          = aws_iam_role.c14_team_growth_lambda_role.arn
  package_type  = "Image"
  image_uri     = var.lambda_ecr_uri
  memory_size   = 128
  timeout       = 180
  environment {
    variables = var.environment_variables
  }
}

# Log group for Lambda
resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name = "/aws/lambda/c14-team-growth-lambda-report"
}

output "lambda_function_name" {
  value = aws_lambda_function.c14_team_growth_lambda.function_name
}
