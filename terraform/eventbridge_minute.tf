resource "aws_iam_role" "c14_team_growth_lambda_eventbridge_role" {
  name = "c14_team_growth_lambda_eventbridge_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      },
      {
        Effect = "Allow",
        Principal = {
          Service = "scheduler.amazonaws.com" 
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# Attach AWS Lambda Basic Execution Role to the IAM Role (Renamed)
resource "aws_iam_role_policy_attachment" "lambda_basic_execution_eventbridge" {
  role       = aws_iam_role.c14_team_growth_lambda_eventbridge_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Attach AWS Lambda VPC Access Execution Role to the IAM Role (Renamed)
resource "aws_iam_role_policy_attachment" "lambda_vpc_access_eventbridge" {
  role       = aws_iam_role.c14_team_growth_lambda_eventbridge_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

# Attach custom Invoke Lambda policy
resource "aws_iam_role_policy" "invoke_lambda_permission" {
  name = "c14-team-growth-lambda-invoke-policy"
  role = aws_iam_role.c14_team_growth_lambda_eventbridge_role.name

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "lambda:InvokeFunction"
        ],
        Resource = [
          "arn:aws:lambda:eu-west-2:129033205317:function:c14-team-growth-lambda:*",
          "arn:aws:lambda:eu-west-2:129033205317:function:c14-team-growth-lambda"
        ]
      }
    ]
  })
}

resource "aws_scheduler_schedule" "team_growth_every_minute_schedule" {
  name                = "c14-team-growth-lambda-schedule"
  schedule_expression = "cron(* * * * ? *)" # Every minute
  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = "arn:aws:lambda:eu-west-2:129033205317:function:c14-team-growth-lambda"
    role_arn = aws_iam_role.c14_team_growth_lambda_eventbridge_role.arn  # Using the renamed IAM role
    input    = jsonencode({
      action = "Invoke Lambda"
    })
  }
}

resource "aws_lambda_permission" "team_growth_allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.c14_team_growth_lambda.function_name
  principal     = "scheduler.amazonaws.com"
  source_arn    = aws_scheduler_schedule.team_growth_every_minute_schedule.arn
  depends_on    = [aws_lambda_function.c14_team_growth_lambda]
}