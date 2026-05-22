locals {
  # Decodifica o secret e extrai apenas a URL
  eks_alb_url = jsondecode(data.aws_secretsmanager_secret_version.pitflow.secret_string)["API_PUBLIC_URL"]
}