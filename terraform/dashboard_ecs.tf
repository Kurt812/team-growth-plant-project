data "aws_ecs_cluster" "cluster" {
  cluster_name = "c14-ecs-cluster"
}

resource "aws_iam_role" "ecs_service_role" {
  name               = "c14-team-growth-ecs-service-role"
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

resource "aws_iam_policy" "ecs_service_s3_policy" {
  name        = "c14-team-growth-ecs-service-s3-policy"
  description = "Allow ECS service to upload plant data files to the S3 bucket"
  lifecycle {
    prevent_destroy = false
  }

  policy = jsonencode({
    Version : "2012-10-17",
    Statement : [
      {
        Effect   : "Allow",
        Action   : [
          "s3:GetObject"
        ],
        Resource : "arn:aws:s3:::c14-team-growth-storage/*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_service_s3_policy_attachment" {
  role       = aws_iam_role.ecs_service_role.name
  policy_arn = aws_iam_policy.ecs_service_s3_policy.arn
}

resource "aws_cloudwatch_log_group" "dashboard_log_group" {
  name              = "/ecs/c14-team-growth-dashboard"
  lifecycle {
    prevent_destroy = false
  }
  retention_in_days = 7
}

resource "aws_ecs_task_definition" "c14_team_growth_dashboard" {
  family                   = "c14-team-growth-dashboard"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "1024"
  task_role_arn            = aws_iam_role.ecs_service_role.arn
  execution_role_arn       = data.aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name        = "c14-team-growth-lmnh-dashboard" 
      image       = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c14-team-growth-lmnh-dashboard:latest" 
      cpu         = 256
      memory      = 512
      essential   = true
      portMappings = [
        {
          containerPort = 8501
          hostPort      = 8501
          protocol      = "tcp"
        }
      ]
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
          awslogs-group         = "/ecs/c14-team-growth-dashboard"
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

resource "aws_security_group" "ecs_service_sg" {
  name = "c14-team-growth-streamlit-sg"
  description = "Allow access to Streamlit app"
  vpc_id      = var.vpc_id

  lifecycle {
    prevent_destroy = false
  }

  ingress {
      description = "Allows access to streamlit"  
      from_port   = 8501
      to_port     = 8501
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }
  

  egress {
      description = "Allows all outbound traffic"  
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_blocks = ["0.0.0.0/0"]
    }
}

resource "aws_ecs_service" "service" {
  name            = "c14-team-growth-dashboard-service"
  cluster         = data.aws_ecs_cluster.cluster.id
  task_definition = aws_ecs_task_definition.c14_team_growth_dashboard.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = ["subnet-0497831b67192adc2",
                "subnet-0acda1bd2efbf3922",
                "subnet-0465f224c7432a02e"] 
    security_groups = [aws_security_group.ecs_service_sg.id]
    assign_public_ip = true
  }
}