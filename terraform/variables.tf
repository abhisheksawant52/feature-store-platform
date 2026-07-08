variable "aws_region" {
  description = "AWS region for all resources."
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment name (e.g. dev, prod)."
  type        = string
  default     = "dev"
}

variable "name_prefix" {
  description = "Prefix applied to resource names."
  type        = string
  default     = "feature-store"
}

variable "offline_bucket_name" {
  description = "S3 bucket name for the offline feature store."
  type        = string
}

variable "redis_node_type" {
  description = "ElastiCache node type for the online store."
  type        = string
  default     = "cache.t4g.small"
}

variable "redis_num_cache_clusters" {
  description = "Number of cache clusters (nodes) in the replication group."
  type        = number
  default     = 2
}

variable "redis_engine_version" {
  description = "Redis engine version for the online store."
  type        = string
  default     = "7.1"
}

variable "vpc_subnet_ids" {
  description = "Subnet IDs for the ElastiCache subnet group."
  type        = list(string)
  default     = []
}

variable "vpc_security_group_ids" {
  description = "Security group IDs attached to the ElastiCache replication group."
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "Additional tags applied to all resources."
  type        = map(string)
  default     = {}
}
