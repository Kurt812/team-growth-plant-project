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

