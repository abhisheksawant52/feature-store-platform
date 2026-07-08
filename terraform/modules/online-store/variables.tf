variable "name" {
  description = "Name used for the replication group and related resources."
  type        = string
}

variable "engine_version" {
  description = "Redis engine version."
  type        = string
  default     = "7.1"
}

variable "node_type" {
  description = "ElastiCache node type."
  type        = string
  default     = "cache.t4g.small"
}

variable "num_cache_clusters" {
  description = "Number of nodes in the replication group."
  type        = number
  default     = 2
}

variable "port" {
  description = "Redis port."
  type        = number
  default     = 6379
}

variable "subnet_ids" {
  description = "Subnet IDs for the cache subnet group."
  type        = list(string)
  default     = []
}

variable "security_group_ids" {
  description = "Security group IDs for the replication group."
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "Tags applied to module resources."
  type        = map(string)
  default     = {}
}
