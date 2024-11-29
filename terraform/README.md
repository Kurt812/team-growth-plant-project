# Terraform Infrastructure for Team Growth ETL and Dashboard Pipeline

This repository contains Terraform configurations to set up the infrastructure required for the `c14-team-growth` project. It provisions and manages resources on AWS, including ECS, Lambda, IAM roles, S3, and supporting services.

---

## Table of Contents

1. [Overview](#overview)
2. [Infrastructure Components](#infrastructure-components)
   - [Providers](#providers)
   - [Security Groups](#security-groups)
   - [ECR Repository](#ecr-repository)
   - [IAM Roles and Policies](#iam-roles-and-policies)
   - [ECS Task Definitions](#ecs-task-definitions)
   - [CloudWatch Log Groups](#cloudwatch-log-groups)
   - [Lambda](#lambda)
   - [EventBridge Scheduler](#eventbridge-scheduler)
   - [S3 Bucket](#s3-bucket)
3. [How It Works](#how-it-works)
4. [Usage](#usage)
5. [Outputs](#outputs)

---

## Overview

This Terraform setup provisions an AWS infrastructure to support an ETL pipeline and a Streamlit dashboard. The ETL pipeline transfers data from RDS to S3, while the dashboard is deployed as an ECS service for data visualization. Key services include:

- **ECS (Elastic Container Service)**: Executes the ETL process as a Fargate task and hosts the dashboard.
- **Lambda**: Handles additional processing tasks triggered by EventBridge.
- **S3**: Stores long-term data.
- **EventBridge**: Manages scheduled execution of tasks and functions.
- **CloudWatch**: Captures logs for monitoring.

---

## Infrastructure Components

### Providers
- **AWS**: Configured to deploy resources in the `eu-west-2` region.

### Security Groups
- **ETL Security Group (`ecs_task_sg`)**: Allows:
  - Inbound traffic on port `1433` (SQL Server).
  - Inbound traffic on port `433` (API).
  - All outbound traffic.
- **Dashboard Security Group (`ecs_service_sg`)**: Allows:
  - Inbound traffic on port `8501` (Streamlit app).
  - All outbound traffic.

### ECR Repositories
- **ETL Repository (`c14-team-growth-lmnh`)**: Stores Docker images for the ETL pipeline.
- **Dashboard Repository (`c14-team-growth-lmnh-dashboard`)**: Stores Docker images for the Streamlit dashboard.

### IAM Roles and Policies
- **ECS Task Role**: Grants permissions to upload files to S3.
- **ECS Service Role**: Grants permissions to access S3 resources required by the dashboard.
- **Lambda Role**: Includes policies for basic execution, VPC access, and RDS access.
- **EventBridge Role**: Allows EventBridge to trigger ECS tasks and Lambda functions.

### ECS Task Definitions
- **ETL Task (`c14-team-growth-rds-to-s3-etl`)**: Runs the ETL container with environment variables like `DB_HOST`, `S3_BUCKET`, etc.
- **Dashboard Task (`c14-team-growth-dashboard`)**: Runs the Streamlit dashboard with port mappings for `8501`.

### ECS Service
- **Dashboard Service**: Runs the `c14-team-growth-dashboard` task definition on Fargate with:
  - Subnets and security groups for network configuration.
  - Public IP assignment for external access.

### CloudWatch Log Groups
- **ETL Log Group (`/ecs/c14-team-growth-rds-to-s3-etl`)**: Captures ETL task logs.
- **Dashboard Log Group (`/ecs/c14-team-growth-dashboard`)**: Captures dashboard task logs.
- **Lambda Log Group**: Captures logs for the Lambda function.

### Lambda
- A Lambda function (`c14-team-growth-lambda`) is deployed with:
  - Required IAM role and policies.
  - Environment variables.
  - Docker image stored in ECR.

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

2. **Dashboard Deployment**:
   - The Streamlit dashboard is hosted as an ECS Fargate service, accessible via port `8501`.
   - The service runs on a schedule or can be scaled manually.

3. **Lambda Processing**:
   - The Lambda function handles periodic tasks, invoked every minute by EventBridge.

4. **Infrastructure Support**:
   - CloudWatch Log Groups capture logs for ECS tasks, dashboard, and Lambda to ensure smooth monitoring and debugging.
   - Security groups restrict access to ECS tasks and the database while exposing necessary endpoints for public use.

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
    •   To run the code successfully a terraform.tfvars file is needed, containing the relevant secret variables.
	•	Ensure Docker images are pushed to the respective ECR repositories before deploying ECS tasks.
	•	Logs for debugging can be found in the CloudWatch Log Groups.
