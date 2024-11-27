variable "lambda_ecr_uri" {
    description = "ECR image URI for the minute pipeline"
    type = string
}

variable "environment_variables" {
  description = "List of environment variables for the container"
  type        = map(string)
}
