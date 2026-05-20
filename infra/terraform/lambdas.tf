locals {
  artifacts_dir = "${path.module}/artifacts"

  auth_zip_path         = "${local.artifacts_dir}/pitflow-auth.zip"
  budget_form_zip_path  = "${local.artifacts_dir}/pitflow-budget-form.zip"
  shared_layer_zip_path = "${local.artifacts_dir}/pitflow-shared-layer.zip"
}

resource "aws_lambda_layer_version" "shared" {
  layer_name          = var.shared_layer_name
  filename            = local.shared_layer_zip_path
  source_code_hash    = filebase64sha256(local.shared_layer_zip_path)
  compatible_runtimes = [var.lambda_runtime]
}

resource "aws_lambda_function" "auth" {
  function_name = var.auth_lambda_name
  role          = data.aws_iam_role.lab_role.arn
  runtime       = var.lambda_runtime
  handler       = "handler.lambda_handler"
  filename      = local.auth_zip_path

  source_code_hash = filebase64sha256(local.auth_zip_path)
  layers           = [aws_lambda_layer_version.shared.arn]
  timeout          = 30
  memory_size      = 256

  environment {
    variables = {
      IS_LOCAL = "false"
    }
  }
}

resource "aws_lambda_function" "budget_form" {
  function_name = var.budget_form_lambda_name
  role          = data.aws_iam_role.lab_role.arn
  runtime       = var.lambda_runtime
  handler       = "handler.lambda_handler"
  filename      = local.budget_form_zip_path

  source_code_hash = filebase64sha256(local.budget_form_zip_path)
  layers           = [aws_lambda_layer_version.shared.arn]
  timeout          = 30
  memory_size      = 256

  environment {
    variables = {
      IS_LOCAL = "false"
    }
  }
}
