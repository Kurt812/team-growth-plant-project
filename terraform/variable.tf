variable "lambda_ecr_uri" {
    description = "ECR image URI for the minute pipeline"
    type = string
}

variable "environment_variables" {
  description = "List of environment variables for the container"
  type        = map(string)
}

variable "DB_HOST" {
  description = "host for the database"
  type        = string
}

variable "DB_PORT" {
  description = "port that the database is hosted on"
  type        = string
}

variable "DB_PASSWORD" {
  description = "database password"
  type        = string
}

variable "DB_USER" {
  description = "database username"
  type        = string
}

variable "DB_NAME" {
  description = "database name"
  type        = string
}

variable "SCHEMA_NAME" {
  description = "database schema name"
  type        = string
}

variable "S3_BUCKET" {
  description = "S3 storage bucket name"
  type        = string
}
