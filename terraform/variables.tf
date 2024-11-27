variable "lambda_ecr_uri" {
    description = "ECR image URI for the minute pipeline"
    type = string
}

variable "DB_HOST" {
  description = "host for the database"
  type        = string
  sensitive = true
}

variable "DB_PORT" {
  description = "port that the database is hosted on"
  type        = string
  sensitive = true
}

variable "DB_PASSWORD" {
  description = "database password"
  type        = string
  sensitive = true
}

variable "DB_USER" {
  description = "database username"
  type        = string
  sensitive = true
}

variable "DB_NAME" {
  description = "database name"
  type        = string
  sensitive = true
}

variable "SCHEMA_NAME" {
  description = "database schema name"
  type        = string
  sensitive = true
}

variable "S3_BUCKET" {
  description = "S3 storage bucket name"
  type        = string
  sensitive = true
}

variable "environment_variables" {
  description = "List of environment variables for the container"
  type        = map(string)
}


# DB_HOST="c14-plants.c57vkec7dkkx.eu-west-2.rds.amazonaws.com"
# DB_PORT="1433"
# DB_PASSWORD="gamma1"
# DB_USER="gamma"
# DB_NAME="plants"
# SCHEMA_NAME="gamma"
