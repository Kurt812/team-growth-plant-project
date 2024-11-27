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
