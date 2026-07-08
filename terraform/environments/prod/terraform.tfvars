aws_region          = "us-east-1"
environment         = "prod"
name_prefix         = "feature-store"
offline_bucket_name = "feature-store-offline-prod-123456789012"

redis_node_type          = "cache.r7g.large"
redis_num_cache_clusters = 3
redis_engine_version     = "7.1"

vpc_subnet_ids         = ["subnet-prod-a", "subnet-prod-b", "subnet-prod-c"]
vpc_security_group_ids = ["sg-prod-online-store"]

tags = {
  CostCenter = "ml-platform-prod"
}
