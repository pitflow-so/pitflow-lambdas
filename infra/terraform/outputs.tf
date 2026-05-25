output "auth_lambda_name" {
  description = "Name of the customer authentication Lambda function."
  value       = aws_lambda_function.auth.function_name
}

output "auth_lambda_arn" {
  description = "ARN of the customer authentication Lambda function."
  value       = aws_lambda_function.auth.arn
}

output "auth_lambda_runtime" {
  description = "Runtime of the auth Lambda function."
  value       = aws_lambda_function.auth.runtime
}

output "budget_form_lambda_name" {
  description = "Name of the budget form Lambda function."
  value       = aws_lambda_function.budget_form.function_name
}

output "budget_form_lambda_arn" {
  description = "ARN of the budget form Lambda function."
  value       = aws_lambda_function.budget_form.arn
}

output "budget_form_lambda_runtime" {
  description = "Runtime of the budget_form Lambda function."
  value       = aws_lambda_function.budget_form.runtime
}

output "shared_layer_name" {
  description = "Name of the shared Lambda layer."
  value       = aws_lambda_layer_version.shared.layer_name
}

output "shared_layer_arn" {
  description = "ARN of the shared Lambda layer."
  value       = aws_lambda_layer_version.shared.arn
}

output "shared_layer_version" {
  description = "Version of the shared Lambda layer."
  value       = aws_lambda_layer_version.shared.version
}

output "deployment_info" {
  description = "Informações de deploy"
  value = {
    auth_lambda = {
      name    = aws_lambda_function.auth.function_name
      arn     = aws_lambda_function.auth.arn
      runtime = aws_lambda_function.auth.runtime
      layers  = aws_lambda_function.auth.layers
    }
    budget_form_lambda = {
      name    = aws_lambda_function.budget_form.function_name
      arn     = aws_lambda_function.budget_form.arn
      runtime = aws_lambda_function.budget_form.runtime
      layers  = aws_lambda_function.budget_form.layers
    }
    shared_layer = {
      name    = aws_lambda_layer_version.shared.layer_name
      arn     = aws_lambda_layer_version.shared.arn
      version = aws_lambda_layer_version.shared.version
    }
  }
}


output "eks_alb_url_resolved" {
  description = "URL do Load Balancer do EKS extraída do Secrets Manager"
  value       = local.eks_alb_url
  sensitive   = true
}

output "api_gateway_endpoint" {
  description = "URL base de invocação do API Gateway"
  value       = aws_apigatewayv2_api.pitflow_api.api_endpoint
}