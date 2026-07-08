# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-07-08

### Added

- FastAPI serving application with `/health` and `/ready` probes and
  `/api/v1` routes for online feature retrieval and feature-view inspection.
- Feature registry with entities, feature views, and reference resolution.
- Offline store abstraction (Parquet) with point-in-time-correct historical
  retrieval and latest-value scans.
- Online store abstraction with Redis and in-memory backends.
- Offline-to-online materialization jobs.
- Multi-stage, non-root Dockerfile with a `/health` HEALTHCHECK.
- Helm chart (`helm/feature-store`) with deployment, service, ingress, HPA,
  service account, config map, and Redis secret placeholder.
- Terraform for AWS: S3 offline store, ECR repository, and an ElastiCache
  Redis online-store module, with dev and prod environments.
- CI workflow (lint, test matrix, Docker build, Terraform validate, Helm lint),
  pre-commit hooks, and full open-source project hygiene.

[0.1.0]: https://github.com/abhisheksawant52/feature-store-platform/releases/tag/v0.1.0
