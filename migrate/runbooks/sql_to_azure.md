## Runbook: SQL Server -> Azure SQL (DB / MI / VM)

**Pre-flight**
- Assessment complete (/assess), target chosen (/decide)
- Azure Migrate / DMA readiness issues triaged
- Landing zone deployed (/migrate), networking + Entra admin verified
- Azure Hybrid Benefit eligibility confirmed; reservation decision made
- Baseline captured: top queries, wait stats, job runtimes (/validate)

**Migrate** (pick the method by downtime tolerance)
- Online: Azure Database Migration Service (online) or MI Link for MI
- Offline: DMS offline, backup/restore (MI/VM), BACPAC (small DBs)

**Cutover**
- Freeze writes, confirm final sync/log backup applied
- Run reconciliation (validate/reconcile.py), compare to baseline
- Repoint connection strings; enable Entra auth; disable legacy SQL logins as planned
- Smoke test critical paths; keep rollback window (source read-only) for N days

**Post**: enable Defender for SQL, backups/retention review, cost check vs business case, then mirror to Fabric (/modernize).
