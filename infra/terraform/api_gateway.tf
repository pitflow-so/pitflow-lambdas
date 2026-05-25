# 1. Criação do API Gateway (HTTP API)
resource "aws_apigatewayv2_api" "pitflow_api" {
  name          = "pitflow-api-gateway"
  protocol_type = "HTTP"
}

# 2. Integração com a Lambda 1 (Auth)
resource "aws_apigatewayv2_integration" "lambda_auth" {
  api_id           = aws_apigatewayv2_api.pitflow_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.auth.invoke_arn
}

resource "aws_apigatewayv2_route" "route_auth_post" {
  api_id    = aws_apigatewayv2_api.pitflow_api.id
  route_key = "POST /auth/customer"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_auth.id}"
}

# 3. Integração com a Lambda 2 (Budget Form)
resource "aws_apigatewayv2_integration" "lambda_budget" {
  api_id           = aws_apigatewayv2_api.pitflow_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.budget_form.invoke_arn
}

resource "aws_apigatewayv2_route" "route_budget_get" {
  api_id    = aws_apigatewayv2_api.pitflow_api.id
  route_key = "GET /customer/budget"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_budget.id}"
}

resource "aws_apigatewayv2_route" "route_budget_post" {
  api_id    = aws_apigatewayv2_api.pitflow_api.id
  route_key = "POST /customer/budget/confirm"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_budget.id}"
}

# 4. Integração Catch-all (Proxy para o EKS)
resource "aws_apigatewayv2_integration" "eks_backend" {
  api_id             = aws_apigatewayv2_api.pitflow_api.id
  integration_type   = "HTTP_PROXY"
  integration_uri    = "${local.eks_alb_url}/{proxy+}"
  integration_method = "ANY"

  request_parameters = {
    "overwrite:header.host" = replace(local.eks_alb_url, "http://", "")
  }
}

resource "aws_apigatewayv2_route" "route_eks_proxy" {
  api_id    = aws_apigatewayv2_api.pitflow_api.id
  route_key = "ANY /{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.eks_backend.id}"
}

resource "aws_apigatewayv2_route" "route_root" {
  api_id    = aws_apigatewayv2_api.pitflow_api.id
  route_key = "ANY /"
  target    = "integrations/${aws_apigatewayv2_integration.eks_backend.id}"
}

# 5. Deploy do API Gateway (Stage default)
resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.pitflow_api.id
  name        = "$default"
  auto_deploy = true
}

# 6. Permissões para o API Gateway invocar as Lambdas
resource "aws_lambda_permission" "apigw_invoke_auth" {
  statement_id  = "AllowAPIGatewayInvokeAuth"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.auth.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.pitflow_api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "apigw_invoke_budget" {
  statement_id  = "AllowAPIGatewayInvokeBudget"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.budget_form.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.pitflow_api.execution_arn}/*/*"
}