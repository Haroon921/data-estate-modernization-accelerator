## Governance baseline (Fabric + OneLake)

A minimum checklist to run once mirrored/migrated data lands in Fabric, before opening access broadly or building AI on top of it.

**Discovery and classification**
- Run a Microsoft Purview scan across the Fabric tenant and connected sources
- Apply sensitivity labels to Lakehouse/Warehouse items containing sensitive data
- Confirm lineage is visible from source -> mirrored/bronze -> silver -> gold

**Access and workspace hygiene**
- Review Fabric workspace roles (Admin/Member/Contributor/Viewer) against least privilege
- Confirm Entra ID groups (not individual accounts) are used for role assignments
- Review and remove stale guest/external access

**Data quality gates**
- Null-rate and key-uniqueness checks on Silver/Gold tables (align with validate/README.md)
- Referential integrity checks on critical fact/dimension tables
- Agreed data quality owner per Gold table

**AI readiness**
- Only expose curated Gold tables / documented semantic models as grounding data for Copilot or agents
- Document known limitations, refresh cadence and owner for each semantic model
- Re-run the sensitivity/label review before any table is used as AI grounding data

This is a starting checklist, not a compliance attestation. Confirm current Purview/Fabric governance capabilities and your organization's compliance requirements before customer use.
