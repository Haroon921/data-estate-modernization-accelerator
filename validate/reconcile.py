#!/usr/bin/env python3
"""Compare row counts and column checksums between source and target SQL endpoints.
Usage: python reconcile.py config.json
config.json: {"source": "<odbc conn str>", "target": "<odbc conn str>", "tables": ["dbo.Orders", ...]}
Requires: pip install pyodbc. Use Entra auth in the connection strings; never hardcode secrets.
"""
import json, sys, time, pyodbc

def stats(cn, table):
    cur = cn.cursor(); t0 = time.time()
    cur.execute(f"SELECT COUNT_BIG(*) FROM {table}")
    n = cur.fetchone()[0]
    cur.execute(f"SELECT CHECKSUM_AGG(CHECKSUM(*)) FROM {table}")
    cs = cur.fetchone()[0]
    return n, cs, round(time.time() - t0, 2)

def main(cfg_path):
    cfg = json.load(open(cfg_path))
    src, tgt = pyodbc.connect(cfg["source"]), pyodbc.connect(cfg["target"])
    print("table,src_rows,tgt_rows,rows_match,checksum_match,src_sec,tgt_sec")
    bad = 0
    for t in cfg["tables"]:
        sn, sc, ss = stats(src, t); tn, tc, ts = stats(tgt, t)
        ok_r, ok_c = sn == tn, sc == tc
        bad += (not ok_r) or (not ok_c)
        print(f"{t},{sn},{tn},{ok_r},{ok_c},{ss},{ts}")
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main(sys.argv[1])
