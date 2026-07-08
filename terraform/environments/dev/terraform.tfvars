aws_region          = "us-east-1"
environment         = "dev"
name_prefix         = "feature-store"
offline_bucket_name = "feature-store-offline-dev-123456789012"

redis_node_type          = "cache.t4g.small"
redis_num_cache_clusters = 1
redis_engine_version     = "7.1"

vpc_subnet_ids         = ["subnet-dev-a", "subnet-dev-b"]
vpc_security_group_ids = ["sg-dev-online-store"]

tags = {
  CostCenter = "ml-platform-dev"
}
