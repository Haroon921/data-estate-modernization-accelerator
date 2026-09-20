## Validation framework
- **Row counts + checksums** - reconcile.py (note: CHECKSUM can differ across collations/types; treat mismatches as a prompt to investigate, not proof of corruption)
- **Performance baseline** - capture top 20 queries (Query Store) before/after; accept within agreed tolerance
- **Job/pipeline parity** - run duration and success rate per job
- **Data quality** - null rates, key uniqueness, referential checks on critical tables
- **Security parity** - roles, RLS/CLS, and access reviews signed off
