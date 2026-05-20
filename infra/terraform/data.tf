data "aws_caller_identity" "current" {}

data "aws_iam_role" "lab_role" {
  name = "LabRole"
}

data "aws_secretsmanager_secret" "pitflow" {
  name = var.secret_name
}
