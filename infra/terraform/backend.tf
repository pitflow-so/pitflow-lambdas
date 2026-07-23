terraform {
  backend "s3" {
    bucket = "tfstate-backend-pitflow-bootstrap"
    key    = "infra/terraform/lambdas/terraform.tfstate"
    region = "us-east-1"
  }
}
