# s3.tf

resource "aws_s3_bucket" "long_term_storage" {
  bucket = "c14-team-growth-storage"                   

  tags = {
    Name        = "LongTermStorage"
  }
}