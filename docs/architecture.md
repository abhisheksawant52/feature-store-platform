# Architecture

The feature store separates two storage tiers that share a single registry:

- **Offline store** (S3 / Parquet) — full feature history used to build
  training datasets with point-in-time-correct joins.
- **Online store** (ElastiCache Redis) — the latest value per entity, served
  with low latency for real-time inference.

## Data flow

1. Feature pipelines write historical rows into the offline store.
2. **Materialization** jobs read the latest value per entity from the offline
   store and upsert it into the online store with a TTL.
3. The **serving API** resolves feature references through the **registry** and
   reads from the online store (`get_online_features`) or offline store
   (`get_historical_features`).

## Components

| Component        | Module                             | Responsibility                                  |
| ---------------- | ---------------------------------- | ----------------------------------------------- |
| Registry         | `feature_store.registry`           | Entities, feature views, reference resolution.  |
| Offline store    | `feature_store.offline_store`      | Parquet-backed batch/historical retrieval.      |
| Online store     | `feature_store.online_store`       | Redis / in-memory low-latency lookups.          |
| Materialization  | `feature_store.materialization`    | Offline → online sync jobs.                     |
| Serving          | `feature_store.serving`            | `get_online_features` / `get_historical_features`. |
| API              | `feature_store.api`                | FastAPI routers and dependency wiring.          |

## Deployment topology

The serving API is packaged as a container and deployed via the Helm chart in
`helm/feature-store`. AWS infrastructure (S3, ECR, ElastiCache Redis) is
provisioned by the Terraform in `terraform/`, with dev and prod environments.
