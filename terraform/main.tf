locals {
  name = "${var.name_prefix}-${var.environment}"
}

# ---------------------------------------------------------------------------
# Offline store: versioned, encrypted S3 bucket holding historical features.
# ---------------------------------------------------------------------------
resource "aws_s3_bucket" "offline_store" {
  bucket = var.offline_bucket_name
  tags   = var.tags
}

resource "aws_s3_bucket_versioning" "offline_store" {
  bucket = aws_s3_bucket.offline_store.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "offline_store" {
  bucket = aws_s3_bucket.offline_store.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "offline_store" {
  bucket                  = aws_s3_bucket.offline_store.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ---------------------------------------------------------------------------
# Container registry: image repository for the serving API.
# ---------------------------------------------------------------------------
resource "aws_ecr_repository" "serving_api" {
  name                 = local.name
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = var.tags
}

# ---------------------------------------------------------------------------
# Online store: ElastiCache Redis, provisioned by the reusable module.
# ---------------------------------------------------------------------------
module "online_store" {
  source = "./modules/online-store"

  name               = local.name
  engine_version     = var.redis_engine_version
  node_type          = var.redis_node_type
  num_cache_clusters = var.redis_num_cache_clusters
  subnet_ids         = var.vpc_subnet_ids
  security_group_ids = var.vpc_security_group_ids
  tags               = var.tags
}
