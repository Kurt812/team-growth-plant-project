provider "aws" {
  region = "eu-west-2"
}

# ECR Repository
resource "aws_ecr_repository" "c14_team_growth_lmnh" {
  encryption_configuration {
    encryption_type = "AES256"
  }

  image_scanning_configuration {
    scan_on_push = false
  }

  image_tag_mutability = "MUTABLE"
  name                 = "c14-team-growth-lmnh"
}

output "ecr_repository_id" {
  value = aws_ecr_repository.c14_team_growth_lmnh.id
}

# S3 Bucket for Long-Term Storage
resource "aws_s3_bucket" "long_term_storage" {
  bucket = "c14-team-growth-storage"                   

  tags = {
    Name        = "LongTermStorage"
  }
}


resource "aws_iam_role" "c14_team_growth_lambda_role" {
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
    role       = aws_iam_role.c14_team_growth_lambda_role.name
    policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}
resource "aws_iam_role_policy_attachment" "lambda_vpc_access" {
     role       = aws_iam_role.c14_team_growth_lambda_role.name
     policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}


resource "aws_lambda_function" "c14_team_growth_lambda" {
    function_name = "c14-team-growth-lambda"
    role          = aws_iam_role.c14_team_growth_lambda_role.arn
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

# EventBridge Scheduler for Lambda (Every Minute)
resource "aws_scheduler_schedule" "team_growth_every_minute_schedule" {
  name                = "c14-team-growth-lambda-schedule"
  group_name          = aws_scheduler_schedule_group.team_growth_schedule_group.name
  schedule_expression = "cron(0/1 * * * ? *)" # Every minute
  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = aws_lambda_function.c14_team_growth_lambda.arn
    role_arn = aws_iam_role.c14_team_growth_lambda_role.arn
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
}

data "aws_iam_role" "ecs_task_execution_role" {
  name = "ecsTaskExecutionRole"
}

resource "aws_cloudwatch_log_group" "etl_log_group" {
  name              = "/ecs/c14-team-growth-rds-to-s3-etl"
  retention_in_days = 7
}

resource "aws_iam_role" "ecs_task_role" {
  name               = "c14-team-growth-ecs-task-role"
  assume_role_policy = jsonencode({
    Version : "2012-10-17",
    Statement : [
      {
        Effect    : "Allow",
        Principal : {
          Service : "ecs-tasks.amazonaws.com"
        },
        Action    : "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_policy" "ecs_task_s3_policy" {
  name        = "c14-team-growth-ecs-task-s3-policy"
  description = "Allow ECS tasks to upload plant data files to the S3 bucket"

  policy = jsonencode({
    Version : "2012-10-17",
    Statement : [
      {
        Effect   : "Allow",
        Action   : [
          "s3:PutObject",
          "s3:PutObjectAcl"
        ],
        Resource : "arn:aws:s3:::c14-team-growth-storage/*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_s3_policy_attachment" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = aws_iam_policy.ecs_task_s3_policy.arn
}

resource "aws_security_group" "ecs_task_sg" {
  name        = "c14-team-growth-etl-security"
  description = "Security group for SQL Server allowing access only on port 1433"
  vpc_id      = var.vpc_id

  ingress {
    description      = "Allow SQL Server access"
    from_port        = 1433
    to_port          = 1433
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

resource "aws_ecs_task_definition" "c14_team_growth_rds_to_s3_etl" {
  family                   = "c14-team-growth-rds-to-s3-etl"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "1024"
  task_role_arn            = aws_iam_role.ecs_task_role.arn
  execution_role_arn       = data.aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name        = "c14-team-growth-lmnh"
      image       = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c14-team-growth-lmnh:latest"
      cpu         = 256
      memory      = 512
      essential   = true

      environment = [
        { name = "DB_HOST", value = var.DB_HOST },
        { name = "DB_PORT", value = var.DB_PORT },
        { name = "DB_USER", value = var.DB_USER },
        { name = "SCHEMA_NAME", value = var.SCHEMA_NAME },
        { name = "S3_BUCKET", value = var.S3_BUCKET},
        { name = "DB_NAME", value = var.DB_NAME },
        { name = "DB_PASSWORD", value = var.DB_PASSWORD }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/c14-team-growth-rds-to-s3-etl"
          awslogs-region        = "eu-west-2"
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])

  runtime_platform {
    cpu_architecture       = "X86_64"
    operating_system_family = "LINUX"
  }
}

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
        task_definition_arn = "arn:aws:ecs:eu-west-2:129033205317:task-definition/c14-team-growth-rds-to-s3-etl:4"
        launch_type = "FARGATE"  
        network_configuration {
            subnets = [
                "subnet-0497831b67192adc2",
                "subnet-0acda1bd2efbf3922",
                "subnet-0465f224c7432a02e"
            ]
            security_groups = [aws_security_group.ecs_task_sg.id] 
            assign_public_ip = true 
        }
    }
  }
}

# IAM Role for EventBridge to trigger ECS tasks
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

# Attach necessary ECS permissions to the EventBridge role
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
