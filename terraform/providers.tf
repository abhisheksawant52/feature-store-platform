provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "feature-store-platform"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}
