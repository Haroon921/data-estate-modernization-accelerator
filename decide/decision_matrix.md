## Decision matrix

### SQL Server

| Situation | Target | When NOT to use |
|---|---|---|
| Standalone DB, no Agent/cross-DB/CLR/linked servers | Azure SQL Database | Needs instance-level features |
| Instance-scoped features, high compatibility needed | Azure SQL Managed Instance | Very large single DB may suit Hyperscale better |
| FILESTREAM, OS access, 3rd-party agents | SQL Server on Azure VM | Ops overhead unacceptable; remove the dependency instead |
| Multi-TB, fast scale/restore needs | Azure SQL DB Hyperscale | Heavy instance-scoped dependencies |
| Not ready to move; need cost/security relief | Renew with SA + Azure Arc, or ESU | Only defers the decision |

### Synapse -> Fabric

| Source | Target | When NOT to (yet) |
|---|---|---|
| Dedicated SQL pool | Fabric Warehouse | Heavy reliance on unsupported T-SQL/features; stable workload with no roadmap driver |
| Spark pools/notebooks | Fabric Spark | Pinned to old runtime or custom libs needing rework |
| Pipelines | Fabric Data Factory | Unsupported activities or complex self-hosted IR topology |
| Serverless SQL | Lakehouse SQL endpoint | Uses features the endpoint lacks |

Always run Azure Migrate / DMA readiness and confirm current feature support on Microsoft Learn before committing.
