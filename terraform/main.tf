provider "aws" {
  region = "eu-west-2"
}

resource "aws_security_group" "ecs_task_sg" {
  name        = "c14-team-growth-etl-security"
  description = "Security group for SQL Server allowing access only on port 1433"
  vpc_id      = var.vpc_id
  lifecycle {
    prevent_destroy = false
  }

  ingress {
    description      = "Allow SQL Server access"
    from_port        = 1433
    to_port          = 1433
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
  }

  ingress {
    description      = "Allows API"
    from_port        = 433
    to_port          = 433
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
  }

  egress {
    description      = "Allow all outbound traffic"
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
  }

  tags = {
    Name = "ecs_task_sg"
  }
}

resource "aws_iam_role" "c14-team-growth-lambda-role" {
    name = "c14-team-growth-lambda-role"
    assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
        {
        "Effect" : "Allow",
        "Principal" : {
            "Service" : "lambda.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
        }
    ]
    })
}

resource "aws_iam_role_policy_attachment" "lambda_policy" {
    role       = aws_iam_role.c14-team-growth-lambda-role.name
    policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}
resource "aws_iam_role_policy_attachment" "lambda_vpc_access" {
     role       = aws_iam_role.c14-team-growth-lambda-role.name
     policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

# Lambda Function
resource "aws_lambda_function" "c14-team-growth-lambda" {
    function_name = "c14-team-growth-lambda"
    role          = aws_iam_role.c14-team-growth-lambda-role.arn
    package_type  = "Image" 
    image_uri = var.lambda_ecr_uri
    environment {
      variables = var.environment_variables
    }
    vpc_config {
    subnet_ids         = ["subnet-0497831b67192adc2","subnet-0acda1bd2efbf3922","subnet-0465f224c7432a02e"]
    security_group_ids = ["sg-09f0012e36bb2a877"]
  }
}

resource "aws_scheduler_schedule_group" "team_growth_schedule_group" {
  name = "team-growth-schedule-group"
}


resource "aws_scheduler_schedule" "team_growth_every_minute_schedule" {
  name                = "c14-team-growth-lambda-schedule"
  group_name          = aws_scheduler_schedule_group.team_growth_schedule_group.name
  schedule_expression = "cron(0/1 * * * ? *)" 
  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = aws_lambda_function.c14_team_growth_lambda.arn
    role_arn = aws_iam_role.c14-team-growth-lambda-role.arn
    input    = jsonencode({
      action = "Invoke Lambda"
    })
  }
}

resource "aws_lambda_permission" "team_growth_allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.c14_team_growth_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.every_minute_schedule.arn
}
