provider "aws" {
  region = "eu-west-2"
}

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
  description = "Allow ECS tasks to upload files to the S3 bucket"

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


