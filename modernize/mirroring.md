## Modernize: mirror to OneLake, then build for analytics and AI

**Why**: after migration, mirroring gives a near-real-time copy of operational data in OneLake with no ETL to build, feeding the same Fabric environment your Synapse workloads land in.

**Steps**
- Confirm the source is supported for mirroring (Azure SQL DB / MI / others - check current Microsoft Learn list and prerequisites)
- In the Fabric workspace: New -> Mirrored database -> select source, tables, and authentication (Entra / managed identity where supported)
- Start mirroring; monitor replication status and lag
- Build Silver/Gold on top (medallion_starter.py), expose a semantic model (Direct Lake)
- Governance baseline: Purview scan of Fabric + sources, sensitivity labels, lineage review, workspace roles reviewed
- AI-ready: curated Gold tables + documented semantic model as grounding data for Copilot / agents (Azure AI Foundry, Fabric data agents)

**Capacity note**: mirroring storage/compute rules change - check current Fabric pricing docs before quoting.
