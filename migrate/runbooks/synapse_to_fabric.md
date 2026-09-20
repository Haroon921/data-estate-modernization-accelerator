## Runbook: Synapse -> Fabric

**Per workload type**
- Dedicated SQL pool -> Fabric Warehouse: extract DDL, remediate unsupported T-SQL, load via OneLake/COPY or pipelines, rebuild security (RLS/CLS), repoint Power BI to Direct Lake where suitable
- Spark -> Fabric Spark: move notebooks, align runtime/libs, replace linked services/mounts with OneLake shortcuts
- Pipelines -> Fabric Data Factory: re-create/convert pipelines; self-hosted IR -> on-premises data gateway
- Serverless SQL -> Lakehouse SQL endpoint

**Steps**
- Size capacity from real usage (Capacity Metrics), start small, autoscale by pause/resume or scale-up windows
- Stand up workspaces per environment (dev/test/prod) with Git integration + deployment pipelines
- Migrate in waves: low-risk read workloads first, then ETL, then critical marts
- Run in parallel; reconcile outputs (/validate); cut over consumers
- Decommission Synapse pools only after sign-off (stop the meter)

**Watch**: unsupported features, capacity throttling at peak, permission model differences.
