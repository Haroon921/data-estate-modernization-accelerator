#!/usr/bin/env python3
"""Route each inventoried workload to a recommended Azure/Fabric target.
Usage: python router.py inventory.csv > routed.csv
Rules are deliberately simple and explainable. Always confirm with DMA / Azure Migrate readiness.
"""
import csv, sys

def b(v): return str(v).strip().lower() == "true"

def route(r):
    t, size = r["source_type"], float(r.get("size_gb") or 0)
    if t == "sql_server":
        inst = any(b(r[k]) for k in ("uses_sql_agent", "uses_cross_db", "uses_clr", "uses_linked_servers"))
        if b(r["uses_filestream"]):
            return ("SQL Server on Azure VM", "FILESTREAM/OS-level dependency", "Consider moving blob data to Azure Storage first", True)
        if size > 4096 and not inst:
            return ("Azure SQL Database Hyperscale", "Large single DB, no instance-scoped features", "Validate log rate and cost vs MI", True)
        if inst:
            return ("Azure SQL Managed Instance", "Instance-scoped features (Agent/cross-DB/CLR/linked servers)", "Best lift-and-shift fit", True)
        return ("Azure SQL Database", "Standalone DB, no instance-scoped features", "Lowest ops overhead", True)
    if t == "synapse_dedicated":
        return ("Fabric Warehouse", "Dedicated SQL pool maps to Fabric Warehouse", "Review unsupported T-SQL and distribution/index design; size capacity from real usage", False)
    if t == "synapse_spark":
        return ("Fabric Spark (Lakehouse)", "Spark notebooks/jobs map to Fabric notebooks", "Check library versions and linked service usage", False)
    if t == "synapse_pipeline":
        return ("Fabric Data Factory", "Pipelines map to Fabric pipelines", "Self-hosted IR -> on-premises data gateway; review unsupported activities", False)
    if t == "ssis":
        return ("Azure-SSIS IR (interim), then Fabric pipelines/dataflows", "Packages need rewrite or a hosted runtime", "Lift first, modernize later", False)
    return ("Manual review", "Unknown source type", "", False)

def main(path):
    rows = list(csv.DictReader(open(path)))
    out = csv.writer(sys.stdout)
    out.writerow(["workload_id", "name", "source_type", "target", "rationale", "watch_out", "mirror_to_onelake_candidate"])
    for r in rows:
        tgt, why, warn, mirror = route(r)
        out.writerow([r["workload_id"], r["name"], r["source_type"], tgt, why, warn,
                      "yes (verify current mirroring support)" if mirror else "n/a"])

if __name__ == "__main__":
    main(sys.argv[1])
