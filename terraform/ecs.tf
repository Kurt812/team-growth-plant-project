data "aws_iam_role" "ecs_task_execution_role" {
  name = "ecsTaskExecutionRole"
}

resource "aws_iam_role" "ecs_task_role" {
  name               = "c14-team-growth-ecs-task-role"
  lifecycle {
    prevent_destroy = false
  }
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
  lifecycle {
    prevent_destroy = false
  }

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

resource "aws_cloudwatch_log_group" "etl_log_group" {
  name              = "/ecs/c14-team-growth-rds-to-s3-etl"
  lifecycle {
    prevent_destroy = false
  }
  retention_in_days = 7
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



