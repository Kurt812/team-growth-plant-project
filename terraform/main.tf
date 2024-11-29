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
