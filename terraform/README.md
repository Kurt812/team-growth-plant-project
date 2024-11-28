# Terraform Infrastructure for Team Growth ETL Pipeline

This repository contains Terraform configurations to set up the infrastructure required for the `c14-team-growth` project. It provisions and manages resources on AWS, including ECS, Lambda, IAM roles, S3, and supporting services.

---

## Table of Contents

1. [Overview](#overview)
2. [Infrastructure Components](#infrastructure-components)
   - [Providers](#providers)
   - [Security Groups](#security-groups)
   - [ECR Repository](#ecr-repository)
   - [IAM Roles and Policies](#iam-roles-and-policies)
   - [ECS Task Definition](#ecs-task-definition)
   - [CloudWatch Log Groups](#cloudwatch-log-groups)
   - [Lambda](#lambda)
   - [EventBridge Scheduler](#eventbridge-scheduler)
   - [S3 Bucket](#s3-bucket)
3. [How It Works](#how-it-works)
4. [Usage](#usage)
5. [Additional Notes](#additional-notes)

---

## Overview

This Terraform setup provisions an AWS infrastructure to support an ETL pipeline for transferring data from RDS to S3 and running scheduled tasks. Key services include:

- **ECS (Elastic Container Service)**: Executes the ETL process as a Fargate task.
- **Lambda**: Handles additional processing tasks triggered by EventBridge.
- **S3**: Stores long-term data.
- **EventBridge**: Manages scheduled execution of tasks and functions.
- **CloudWatch**: Captures logs for monitoring.

---

## Infrastructure Components

### Providers
- **AWS**: Configured to deploy resources in the `eu-west-2` region.

### Security Groups
- A security group (`ecs_task_sg`) is created to allow:
  - Inbound traffic on port `1433` (SQL Server).
  - Inbound traffic on port `433` (API).
  - All outbound traffic.

### ECR Repository
- An ECR repository (`c14-team-growth-lmnh`) is provisioned for storing Docker images for the ETL pipeline.

### IAM Roles and Policies
- **ECS Task Role**: Grants permissions to upload files to S3.
- **Lambda Role**: Includes policies for basic execution, VPC access, and RDS access.
- **EventBridge Role**: Allows EventBridge to trigger ECS tasks and Lambda functions.

### ECS Task Definition
- An ECS Fargate task (`c14-team-growth-rds-to-s3-etl`) runs the ETL container with the required CPU, memory, and environment variables (e.g., `DB_HOST`, `DB_PORT`, `S3_BUCKET`).

### CloudWatch Log Groups
- Log groups capture logs for:
  - ECS tasks (`/ecs/c14-team-growth-rds-to-s3-etl`).
  - Lambda functions (`/aws/lambda/c14-team-growth-lambda-report`).

### Lambda
- A Lambda function (`c14-team-growth-lambda`) is deployed with the required IAM role and environment variables.
- The function uses an ECR image and is triggered by EventBridge.

### EventBridge Scheduler
- **ETL Scheduler**: Executes the ECS task daily at midnight.
- **Lambda Scheduler**: Invokes the Lambda function every minute.

### S3 Bucket
- A bucket (`c14-team-growth-storage`) is created for storing ETL output.

---

## How It Works

1. **ETL Process**:
   - The ECS Fargate task (`c14-team-growth-rds-to-s3-etl`) is triggered by EventBridge daily.
   - The task extracts data from RDS, processes it, and uploads it to the S3 bucket.

2. **Lambda Processing**:
   - The Lambda function handles periodic tasks, invoked every minute by EventBridge.

3. **Infrastructure Support**:
   - CloudWatch Log Groups capture logs for ECS and Lambda to ensure smooth monitoring and debugging.
   - Security groups restrict access to ECS tasks and the database.

4. **ECR Repository**:
   - Docker images for the ETL pipeline and Lambda functions are stored in the ECR repository.

---

## Usage

### Prerequisites

1. Install Terraform.
2. Configure AWS credentials with access to your AWS account.

### Steps

1. Clone this repository:
```bash
   git clone <repository-url>
   cd <repository-folder>
```

2. Initialize Terraform:
```bash
    terraform init
```

3.	Review the plan:  
```bash
    terraform plan
```  

4.	Apply the configuration:
```bash
    terraform apply
```

5.	Verify resources in the AWS Management Console.

## Additional Notes

	•	Modify variables in variables.tf to customize the setup (e.g., vpc_id, database configurations).
	•	Ensure Docker images are pushed to the ECR repository before deploying the ECS task or Lambda.
	•	Logs for debugging can be found in the CloudWatch Log Groups.
