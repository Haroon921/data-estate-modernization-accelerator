-- Run per SQL Server instance (SSMS / sqlcmd). Read-only. Export result sets to CSV.
-- Result 1: instance facts
SELECT @@SERVERNAME AS server_name,
       SERVERPROPERTY('ProductVersion') AS version,
       SERVERPROPERTY('Edition') AS edition,
       cpu_count AS logical_cores,
       physical_memory_kb/1024/1024 AS memory_gb
FROM sys.dm_os_sys_info;

-- Result 2: per-database facts
SELECT d.name AS database_name,
       CAST(SUM(mf.size)*8.0/1024/1024 AS DECIMAL(12,2)) AS size_gb,
       d.compatibility_level,
       d.recovery_model_desc
FROM sys.databases d
JOIN sys.master_files mf ON mf.database_id = d.database_id
WHERE d.database_id > 4
GROUP BY d.name, d.compatibility_level, d.recovery_model_desc;

-- Result 3: instance-level dependencies that steer the target choice
SELECT 'sql_agent_jobs' AS feature, COUNT(*) AS cnt FROM msdb.dbo.sysjobs
UNION ALL SELECT 'linked_servers', COUNT(*) FROM sys.servers WHERE is_linked = 1
UNION ALL SELECT 'clr_assemblies', COUNT(*) FROM sys.assemblies WHERE is_user_defined = 1
UNION ALL SELECT 'filestream_dbs', COUNT(DISTINCT database_id) FROM sys.master_files WHERE type_desc = 'FILESTREAM';

-- Also run Azure Migrate / DMA / Azure Arc SQL assessment for readiness and SKU sizing.
