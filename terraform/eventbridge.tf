resource "aws_scheduler_schedule" "pipeline_schedule" {
  name                = "c14-team-growth-daily-etl" 
  description         = "Triggers the ECS task every 24 hours at midnight"
  schedule_expression = "cron(0 0 * * ? *)"
  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn = "arn:aws:ecs:eu-west-2:129033205317:cluster/c14-ecs-cluster"
    role_arn = aws_iam_role.eventbridge_role.arn
    ecs_parameters {
        task_definition_arn = "arn:aws:ecs:eu-west-2:129033205317:task-definition/c14-team-growth-rds-to-s3-etl:7"
        task_count = 1
        launch_type = "FARGATE"  
        network_configuration {
            subnets = [
                "subnet-0497831b67192adc2",
                "subnet-0acda1bd2efbf3922",
                "subnet-0465f224c7432a02e"
            ]
            security_groups = ["sg-0b286fb0ae9e93094"] 
            assign_public_ip = true 
        }
    }
  }
}

resource "aws_iam_role" "eventbridge_role" {
  name = "EventBridgeEcsInvokeRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "scheduler.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy" "eventbridge_ecs_policy" {
  name = "EventBridgeECSPolicy"
  role = aws_iam_role.eventbridge_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "ecs:RunTask",
        ],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = [
          "iam:PassRole"
        ],
        Resource = "*"
      },

      {
        Effect = "Allow",
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchGetImage",
          "ecr:BatchCheckLayerAvailability",
        ],
        Resource = "arn:aws:ecr:eu-west-2:129033205317:repository/c14-team-growth-lmnh"
      }
    ]
  })
}
resource "aws_iam_role_policy" "run_task_permission" {
  name = "c14-team-growth-run_task-policy"
  role = aws_iam_role.eventbridge_role.name

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "ecs:RunTask"
        ],
        Resource = [
          "arn:aws:ecs:eu-west-2:129033205317:task-definition/c14-team-growth-rds-to-s3-etl:*",
          "arn:aws:ecs:eu-west-2:129033205317:task-definition/c14-team-growth-rds-to-s3-etl"
        ],
        Condition = {
          ArnLike = {
            "ecs:cluster" = "arn:aws:ecs:eu-west-2:129033205317:cluster/c14-ecs-cluster"
          }
        }
      },
      {
        Effect = "Allow",
        Action = "iam:PassRole",
        Resource = "*",
        Condition = {
          StringLike = {
            "iam:PassedToService" = "ecs-tasks.amazonaws.com"
          }
        }
      }
    ]
  })
}
