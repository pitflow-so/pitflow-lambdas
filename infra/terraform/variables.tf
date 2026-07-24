variable "aws_region" {
  description = "AWS region where the Lambda resources will be created."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name used as a prefix for AWS resources."
  type        = string
  default     = "pitflow"
}

variable "lambda_runtime" {
  description = "Python runtime used by the Lambda functions."
  type        = string
  default     = "python3.12"
}

variable "auth_lambda_name" {
  description = "Name of the customer authentication Lambda function."
  type        = string
  default     = "pitflow-auth"
}

variable "budget_form_lambda_name" {
  description = "Name of the budget form Lambda function."
  type        = string
  default     = "pitflow-budget-form"
}

variable "shared_layer_name" {
  description = "Name of the shared Lambda layer."
  type        = string
  default     = "pitflow-shared"
}
