from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.comments import Comment

F = "Arial"
blue = Font(name=F, color="0000FF"); blk = Font(name=F); bold = Font(name=F, bold=True)
hdr = Font(name=F, bold=True, color="FFFFFF"); hfill = PatternFill("solid", fgColor="0F4C81")
yel = PatternFill("solid", fgColor="FFFF00")
USD = '$#,##0;($#,##0);-'; PCT = '0.0%'

wb = Workbook()

def header(ws, row, cols):
    for i, c in enumerate(cols, 1):
        x = ws.cell(row=row, column=i, value=c); x.font = hdr; x.fill = hfill
        x.alignment = Alignment(wrap_text=True, vertical="center")

# ---------- Inputs ----------
ws = wb.active; ws.title = "Inputs"
ws["A1"] = "Modernization Business Case - Inputs"; ws["A1"].font = Font(name=F, bold=True, size=14)
ws["A2"] = "Edit blue cells with yellow fill. All prices are ILLUSTRATIVE placeholders - replace with current Azure pricing / customer quotes."
ws["A2"].font = Font(name=F, italic=True)
header(ws, 4, ["Input", "Value", "Unit / note"])
inputs = [
 ("SQL in-scope cores", 64, "cores (from assessment)"),
 ("Number of databases to migrate", 20, "count"),
 ("On-prem license + SA renewal per core per year", 3500, "$/core/yr (PLACEHOLDER)"),
 ("On-prem infra, DC, ops per core per year", 1800, "$/core/yr (PLACEHOLDER)"),
 ("Azure SQL cost per vCore per month (pay-as-you-go, license included)", 400, "$/vCore/mo (PLACEHOLDER)"),
 ("Azure Hybrid Benefit discount", 0.30, "fraction of PAYG (PLACEHOLDER; confirm)"),
 ("Reserved capacity discount (additional)", 0.25, "fraction (PLACEHOLDER; confirm term)"),
 ("Migration one-time cost per database", 4000, "$/db (services + tooling)"),
 ("Analysis horizon", 3, "years"),
 ("Fabric price per CU-hour (pay-as-you-go)", 0.18, "$/CU-hr (PLACEHOLDER)"),
 ("Hours per month", 730, "hrs"),
 ("Synapse -> Fabric one-time migration cost per workload", 15000, "$/workload"),
]
for i, (a, v, n) in enumerate(inputs, 5):
    ws.cell(row=i, column=1, value=a).font = blk
    c = ws.cell(row=i, column=2, value=v); c.font = blue; c.fill = yel
    c.number_format = PCT if isinstance(v, float) and v < 1 and "discount" in a.lower() else ('$#,##0.00' if "CU-hour" in a else '#,##0')
    ws.cell(row=i, column=3, value=n).font = blk
ws.column_dimensions["A"].width = 64; ws.column_dimensions["B"].width = 14; ws.column_dimensions["C"].width = 40

# named refs by row
R = {k: f"Inputs!$B${i}" for i, k in enumerate(
 ["cores","dbs","lic","infra","azvcore","ahb","ri","migdb","years","cuhr","hrs","migwl"], 5)}

# ---------- SQL TCO ----------
s = wb.create_sheet("SQL_TCO")
s["A1"] = "SQL: Renew vs Migrate (annual and N-year)"; s["A1"].font = Font(name=F, bold=True, size=14)
header(s, 3, ["Line", "Amount ($)", "How calculated"])
rows = [
 ("On-prem annual run cost (renew + infra)", f"={R['cores']}*({R['lic']}+{R['infra']})", "cores x (license + infra)"),
 ("Azure annual cost - pay-as-you-go", f"={R['cores']}*{R['azvcore']}*12", "cores x $/vCore/mo x 12 (assumes 1 core = 1 vCore)"),
 ("Azure annual cost - with Hybrid Benefit", f"=B5*(1-{R['ahb']})", "PAYG x (1 - AHB)"),
 ("Azure annual cost - AHB + reserved", f"=B6*(1-{R['ri']})", "AHB cost x (1 - reservation)"),
 ("One-time migration cost", f"={R['dbs']}*{R['migdb']}", "dbs x cost per db"),
 ("N-year cost: stay on-prem", f"=B4*{R['years']}", "annual x years"),
 ("N-year cost: migrate (AHB + reserved)", f"=B7*{R['years']}+B8", "annual x years + migration"),
 ("N-year savings from migrating", "=B9-B10", "stay minus migrate"),
 ("Annual savings (steady state)", "=B4-B7", "run-rate delta"),
 ("Payback (months)", '=IF(B12>0,B8/(B12/12),"n/a")', "migration cost / monthly savings"),
]
for i, (a, f, n) in enumerate(rows, 4):
    s.cell(row=i, column=1, value=a).font = blk
    c = s.cell(row=i, column=2, value=f); c.font = blk; c.number_format = USD if "Payback" not in a else '0.0'
    s.cell(row=i, column=3, value=n).font = blk
s["A15"] = "Not modeled: security/patching labor, downtime cost, ESU cost for out-of-support versions. Add as inputs when known."
s["A15"].font = Font(name=F, italic=True)
s.column_dimensions["A"].width = 46; s.column_dimensions["B"].width = 16; s.column_dimensions["C"].width = 50

# ---------- Fabric SKUs ----------
k = wb.create_sheet("Fabric_SKUs")
header(k, 1, ["SKU", "Capacity Units (CU)"])
skus = [("F2",2),("F4",4),("F8",8),("F16",16),("F32",32),("F64",64),("F128",128),("F256",256),("F512",512)]
for i, (n, cu) in enumerate(skus, 2):
    k.cell(row=i, column=1, value=n).font = blk
    c = k.cell(row=i, column=2, value=cu); c.font = blue
k["A12"] = "CU = number in SKU name. Source: Microsoft Fabric capacity SKUs (verify on Microsoft Learn)."; k["A12"].font = Font(name=F, italic=True)
k.column_dimensions["A"].width = 12; k.column_dimensions["B"].width = 20

# ---------- Synapse -> Fabric ----------
y = wb.create_sheet("Synapse_to_Fabric")
y["A1"] = "Synapse -> Fabric sizing and cost (fill yellow cells; example rows shown)"; y["A1"].font = Font(name=F, bold=True, size=14)
header(y, 3, ["Workload", "Current Synapse monthly cost ($)", "Target Fabric SKU", "Expected utilization (share of month running)", "CU", "Fabric monthly cost ($)", "Monthly savings ($)", "Annual savings ($)"])
ex = [("EDW dedicated pool (example)", 18000, "F64", 0.6), ("Spark pool (example)", 6000, "F32", 0.4), ("Pipelines/integration (example)", 2500, "F8", 0.5)]
dv = DataValidation(type="list", formula1="=Fabric_SKUs!$A$2:$A$10", allow_blank=False); y.add_data_validation(dv)
for r in range(4, 14):
    for col in (1,2,3,4):
        y.cell(row=r, column=col).fill = yel; y.cell(row=r, column=col).font = blue
    if r - 4 < len(ex):
        for col, v in enumerate(ex[r-4], 1): y.cell(row=r, column=col, value=v)
    dv.add(y.cell(row=r, column=3))
    y.cell(row=r, column=2).number_format = USD; y.cell(row=r, column=4).number_format = PCT
    y.cell(row=r, column=5, value=f'=IFERROR(VLOOKUP(C{r},Fabric_SKUs!$A$2:$B$10,2,FALSE),0)')
    y.cell(row=r, column=6, value=f'=E{r}*{R["cuhr"]}*{R["hrs"]}*D{r}')
    y.cell(row=r, column=7, value=f'=IF(B{r}>0,B{r}-F{r},0)')
    y.cell(row=r, column=8, value=f'=G{r}*12')
    for col in (5,6,7,8):
        y.cell(row=r, column=col).font = blk
        if col > 5: y.cell(row=r, column=col).number_format = USD
y["A15"] = "Total"; y["A15"].font = bold
for col in "BFGH":
    y[f"{col}15"] = f"=SUM({col}4:{col}13)"; y[f"{col}15"].font = bold; y[f"{col}15"].number_format = USD
y["A17"] = "Note: F SKUs can be paused and are billed on running time; reserved pricing may lower cost further. Utilization here is a lever, not a measurement - replace with Capacity Metrics data."
y["A17"].font = Font(name=F, italic=True)
for c, w in zip("ABCDEFGH", (34,20,14,22,8,18,18,18)): y.column_dimensions[c].width = w
y.row_dimensions[3].height = 45

# ---------- Summary ----------
m = wb.create_sheet("Summary", 0)
m["A1"] = "Executive Summary"; m["A1"].font = Font(name=F, bold=True, size=16)
header(m, 3, ["Motion", "Annual savings ($)", "N-year net benefit ($)", "One-time cost ($)"])
m["A4"] = "SQL renew -> migrate to Azure"; m["B4"] = "=SQL_TCO!B12"; m["C4"] = "=SQL_TCO!B11"; m["D4"] = "=SQL_TCO!B8"
m["A5"] = "Synapse -> Fabric"; m["B5"] = "=Synapse_to_Fabric!H15"
m["C5"] = f"=B5*{R['years']}-D5"
m["D5"] = f'={R["migwl"]}*COUNTA(Synapse_to_Fabric!A4:A13)'
m["A6"] = "Total"; m["A6"].font = bold
for col in "BCD":
    m[f"{col}6"] = f"=SUM({col}4:{col}5)"; m[f"{col}6"].font = bold
for r in (4,5,6):
    for col in "BCD":
        m[f"{col}{r}"].number_format = USD
        if r != 6: m[f"{col}{r}"].font = Font(name=F, color="008000")
    if r != 6: m[f"A{r}"].font = blk
m["A8"] = "Numbers are illustrative until Inputs are replaced with customer data. Payback (SQL) months:"; m["A8"].font = Font(name=F, italic=True)
m["D8"] = "=SQL_TCO!B13"; m["D8"].number_format = '0.0'; m["D8"].font = Font(name=F, color="008000")
m["A10"] = "How to use: 1) Fill Inputs  2) List Synapse workloads and target SKUs  3) Read this tab in the customer conversation."
m["A10"].font = blk
m.column_dimensions["A"].width = 44
for c in "BCD": m.column_dimensions[c].width = 22

wb.save("modernization_business_case.xlsx")
