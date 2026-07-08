output "offline_bucket_name" {
  description = "Name of the S3 bucket backing the offline store."
  value       = aws_s3_bucket.offline_store.bucket
}

output "offline_bucket_arn" {
  description = "ARN of the offline store S3 bucket."
  value       = aws_s3_bucket.offline_store.arn
}

output "ecr_repository_url" {
  description = "URL of the ECR repository for the serving API image."
  value       = aws_ecr_repository.serving_api.repository_url
}

output "online_store_endpoint" {
  description = "Primary endpoint of the ElastiCache Redis online store."
  value       = module.online_store.primary_endpoint_address
}

output "online_store_port" {
  description = "Port of the ElastiCache Redis online store."
  value       = module.online_store.port
}
