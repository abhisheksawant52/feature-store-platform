terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.66"
    }
  }

  # Configure remote state per environment (see environments/*/backend.hcl):
  #   terraform init -backend-config=environments/dev/backend.hcl
  # backend "s3" {}
}
