#!/usr/bin/env python3
"""Generate the Data Estate Modernization business-case workbook."""

from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation


FONT = "Arial"
NAVY = "0B2447"
BLUE = "0078D4"
TEAL = "00B4A6"
INK = "1B2A3A"
MUTED = "5B6B7C"
PALE_BLUE = "EAF3FB"
PALE_TEAL = "E6F7F4"
PALE_YELLOW = "FFF4CE"
WHITE = "FFFFFF"
GREEN = "107C10"
RED = "C50F1F"
GRID = Side(style="thin", color="D9E2EC")

USD = '$#,##0;[Red]($#,##0);-'
PCT = "0.0%"


def set_title(ws, title, subtitle, end_column):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=end_column)
    ws["A1"] = title
    ws["A1"].font = Font(name=FONT, bold=True, size=18, color=WHITE)
    ws["A1"].fill = PatternFill("solid", fgColor=NAVY)
    ws["A1"].alignment = Alignment(vertical="center")
    ws.row_dimensions[1].height = 32

    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=end_column)
    ws["A2"] = subtitle
    ws["A2"].font = Font(name=FONT, italic=True, color=MUTED)
    ws["A2"].alignment = Alignment(wrap_text=True, vertical="center")
    ws.row_dimensions[2].height = 30


def add_header(ws, row, columns):
    for column, value in enumerate(columns, 1):
        cell = ws.cell(row=row, column=column, value=value)
        cell.font = Font(name=FONT, bold=True, color=WHITE)
        cell.fill = PatternFill("solid", fgColor=BLUE)
        cell.alignment = Alignment(wrap_text=True, vertical="center")
        cell.border = Border(bottom=GRID)
    ws.row_dimensions[row].height = 28


def style_table_body(ws, start_row, end_row, end_column):
    for row in ws.iter_rows(
        min_row=start_row,
        max_row=end_row,
        min_col=1,
        max_col=end_column,
    ):
        for cell in row:
            cell.font = Font(name=FONT, color=INK)
            cell.alignment = Alignment(vertical="center", wrap_text=True)
            cell.border = Border(bottom=GRID)


def build_workbook(output_path=None):
    output = (
        Path(output_path)
        if output_path
        else Path(__file__).with_name("modernization_business_case.xlsx")
    )
    wb = Workbook()
    wb.calculation.fullCalcOnLoad = True
    wb.calculation.forceFullCalc = True
    wb.calculation.calcMode = "auto"
    wb.properties.title = "Data Estate Modernization Business Case"
    wb.properties.subject = "SQL and Synapse modernization scenario model"
    wb.properties.creator = "Data Estate Modernization Accelerator"

    inputs = wb.active
    inputs.title = "Inputs"
    inputs.sheet_properties.tabColor = BLUE
    set_title(
        inputs,
        "Modernization Business Case - Inputs",
        "Edit yellow cells, record the evidence source, and mark each assumption as validated before customer use.",
        5,
    )
    add_header(inputs, 4, ["Input", "Value", "Unit / note", "Status", "Evidence source"])

    input_rows = [
        ("SQL in-scope cores", 64, "cores from assessment", "Assessment export"),
        ("Number of databases to migrate", 20, "count", "Assessment export"),
        (
            "On-prem license + SA renewal per core per year",
            3500,
            "$/core/year",
            "Customer agreement",
        ),
        (
            "On-prem infrastructure, datacenter, and operations per core per year",
            1800,
            "$/core/year",
            "Customer finance",
        ),
        (
            "Azure SQL cost per vCore per month",
            400,
            "$/vCore/month",
            "Azure pricing estimate",
        ),
        ("Azure Hybrid Benefit discount", 0.30, "fraction", "Azure pricing estimate"),
        ("Reserved capacity discount", 0.25, "fraction", "Azure pricing estimate"),
        (
            "Migration one-time cost per database",
            4000,
            "$/database",
            "Delivery estimate",
        ),
        ("Analysis horizon", 3, "years", "Customer planning horizon"),
        ("Fabric price per CU-hour", 0.18, "$/CU-hour", "Azure pricing estimate"),
        ("Hours per month", 730, "hours", "Calendar assumption"),
        (
            "Synapse-to-Fabric migration cost per workload",
            15000,
            "$/workload",
            "Delivery estimate",
        ),
    ]
    for row, (label, value, note, source) in enumerate(input_rows, 5):
        inputs.cell(row=row, column=1, value=label)
        value_cell = inputs.cell(row=row, column=2, value=value)
        value_cell.font = Font(name=FONT, bold=True, color=BLUE)
        value_cell.fill = PatternFill("solid", fgColor=PALE_YELLOW)
        value_cell.number_format = (
            PCT
            if isinstance(value, float) and value < 1 and "discount" in label.lower()
            else ('$#,##0.00' if "CU-hour" in label else "#,##0")
        )
        inputs.cell(row=row, column=3, value=note)
        status = inputs.cell(row=row, column=4, value="Placeholder")
        status.fill = PatternFill("solid", fgColor=PALE_YELLOW)
        status.font = Font(name=FONT, bold=True, color=RED)
        inputs.cell(row=row, column=5, value=source)

    status_validation = DataValidation(
        type="list",
        formula1='"Placeholder,Validated"',
        allow_blank=False,
    )
    inputs.add_data_validation(status_validation)
    status_validation.add(f"D5:D{4 + len(input_rows)}")
    style_table_body(inputs, 5, 4 + len(input_rows), 5)
    inputs.freeze_panes = "A5"
    inputs.auto_filter.ref = f"A4:E{4 + len(input_rows)}"
    for column, width in {"A": 62, "B": 16, "C": 24, "D": 16, "E": 28}.items():
        inputs.column_dimensions[column].width = width

    refs = {
        key: f"Inputs!$B${row}"
        for row, key in enumerate(
            [
                "cores",
                "dbs",
                "lic",
                "infra",
                "azvcore",
                "ahb",
                "ri",
                "migdb",
                "years",
                "cuhr",
                "hrs",
                "migwl",
            ],
            5,
        )
    }

    sql_tco = wb.create_sheet("SQL_TCO")
    sql_tco.sheet_properties.tabColor = BLUE
    set_title(
        sql_tco,
        "SQL: Renew vs. Migrate",
        "Compares annual run cost, migration investment, cumulative benefit, and payback.",
        3,
    )
    add_header(sql_tco, 3, ["Line", "Amount", "Calculation"])
    sql_rows = [
        (
            "On-prem annual run cost",
            f"={refs['cores']}*({refs['lic']}+{refs['infra']})",
            "cores x (license + infrastructure)",
        ),
        (
            "Azure annual cost - pay as you go",
            f"={refs['cores']}*{refs['azvcore']}*12",
            "cores x $/vCore/month x 12",
        ),
        (
            "Azure annual cost - Hybrid Benefit",
            f"=B5*(1-{refs['ahb']})",
            "pay-as-you-go x (1 - benefit)",
        ),
        (
            "Azure annual cost - benefit + reservation",
            f"=B6*(1-{refs['ri']})",
            "benefit cost x (1 - reservation)",
        ),
        (
            "One-time SQL migration cost",
            f"={refs['dbs']}*{refs['migdb']}",
            "databases x cost/database",
        ),
        (
            "N-year cost: stay on-premises",
            f"=B4*{refs['years']}",
            "annual cost x horizon",
        ),
        (
            "N-year cost: migrate",
            f"=B7*{refs['years']}+B8",
            "annual Azure cost x horizon + migration",
        ),
        ("N-year net savings", "=B9-B10", "stay minus migrate"),
        ("Annual run-rate savings", "=B4-B7", "on-premises minus Azure"),
        (
            "Payback",
            '=IF(B12>0,B8/(B12/12),"n/a")',
            "migration cost / monthly savings",
        ),
    ]
    for row, (label, formula, calculation) in enumerate(sql_rows, 4):
        sql_tco.cell(row=row, column=1, value=label)
        amount = sql_tco.cell(row=row, column=2, value=formula)
        amount.number_format = "0.0" if label == "Payback" else USD
        sql_tco.cell(row=row, column=3, value=calculation)
    style_table_body(sql_tco, 4, 13, 3)
    for row in (11, 12, 13):
        sql_tco.cell(row=row, column=2).font = Font(
            name=FONT,
            bold=True,
            color=GREEN,
        )
    sql_tco["A15"] = (
        "Not modeled: downtime, application remediation, security operations, "
        "or extended support. Add customer-specific costs where material."
    )
    sql_tco["A15"].font = Font(name=FONT, italic=True, color=MUTED)
    sql_tco.merge_cells("A15:C15")
    sql_tco.column_dimensions["A"].width = 48
    sql_tco.column_dimensions["B"].width = 20
    sql_tco.column_dimensions["C"].width = 48
    sql_tco.freeze_panes = "A4"

    fabric_skus = wb.create_sheet("Fabric_SKUs")
    fabric_skus.sheet_properties.tabColor = TEAL
    set_title(
        fabric_skus,
        "Microsoft Fabric Capacity Reference",
        "Capacity Units shown for scenario modeling; verify current availability and pricing.",
        2,
    )
    add_header(fabric_skus, 4, ["SKU", "Capacity Units"])
    skus = [
        ("F2", 2),
        ("F4", 4),
        ("F8", 8),
        ("F16", 16),
        ("F32", 32),
        ("F64", 64),
        ("F128", 128),
        ("F256", 256),
        ("F512", 512),
    ]
    for row, (sku, capacity_units) in enumerate(skus, 5):
        fabric_skus.cell(row=row, column=1, value=sku)
        fabric_skus.cell(row=row, column=2, value=capacity_units)
    style_table_body(fabric_skus, 5, 13, 2)
    fabric_skus.column_dimensions["A"].width = 18
    fabric_skus.column_dimensions["B"].width = 24

    fabric = wb.create_sheet("Synapse_to_Fabric")
    fabric.sheet_properties.tabColor = TEAL
    set_title(
        fabric,
        "Synapse to Fabric - Workload Economics",
        "Enter current workload cost, choose a target SKU, and adjust expected utilization.",
        8,
    )
    add_header(
        fabric,
        3,
        [
            "Workload",
            "Current monthly cost",
            "Target Fabric SKU",
            "Expected utilization",
            "CU",
            "Fabric monthly cost",
            "Monthly savings",
            "Annual savings",
        ],
    )
    examples = [
        ("EDW dedicated pool", 18000, "F64", 0.60),
        ("Spark pool", 6000, "F32", 0.40),
        ("Pipelines and integration", 2500, "F8", 0.50),
    ]
    sku_validation = DataValidation(
        type="list",
        formula1="=Fabric_SKUs!$A$5:$A$13",
        allow_blank=False,
    )
    fabric.add_data_validation(sku_validation)
    for row in range(4, 14):
        for column in range(1, 5):
            cell = fabric.cell(row=row, column=column)
            cell.fill = PatternFill("solid", fgColor=PALE_YELLOW)
            cell.font = Font(name=FONT, color=BLUE)
        if row - 4 < len(examples):
            for column, value in enumerate(examples[row - 4], 1):
                fabric.cell(row=row, column=column, value=value)
        sku_validation.add(fabric.cell(row=row, column=3))
        fabric.cell(row=row, column=2).number_format = USD
        fabric.cell(row=row, column=4).number_format = PCT
        fabric.cell(
            row=row,
            column=5,
            value=f'=IFERROR(VLOOKUP(C{row},Fabric_SKUs!$A$5:$B$13,2,FALSE),0)',
        )
        fabric.cell(
            row=row,
            column=6,
            value=f'=E{row}*{refs["cuhr"]}*{refs["hrs"]}*D{row}',
        )
        fabric.cell(
            row=row,
            column=7,
            value=f'=IF(B{row}>0,B{row}-F{row},0)',
        )
        fabric.cell(row=row, column=8, value=f"=G{row}*12")
        for column in (6, 7, 8):
            fabric.cell(row=row, column=column).number_format = USD
    fabric["A15"] = "Total"
    for column in "BFGH":
        fabric[f"{column}15"] = f"=SUM({column}4:{column}13)"
        fabric[f"{column}15"].number_format = USD
        fabric[f"{column}15"].font = Font(name=FONT, bold=True, color=GREEN)
    style_table_body(fabric, 4, 15, 8)
    for column, width in zip("ABCDEFGH", (30, 19, 18, 20, 9, 19, 18, 18)):
        fabric.column_dimensions[column].width = width
    fabric.freeze_panes = "A4"

    summary = wb.create_sheet("Summary", 0)
    summary.sheet_properties.tabColor = NAVY
    set_title(
        summary,
        "Executive Summary",
        "Decision-ready view of annual savings, net benefit, investment, and sensitivity.",
        12,
    )
    summary.merge_cells("A3:D3")
    summary["A3"] = (
        f'=IF(COUNTIF(Inputs!$D$5:$D${4 + len(input_rows)},"Placeholder")>0,'
        '"ILLUSTRATIVE - VALIDATE ALL YELLOW INPUTS",'
        '"VALIDATED INPUT SET")'
    )
    summary["A3"].font = Font(name=FONT, bold=True, color=RED)
    summary["A3"].fill = PatternFill("solid", fgColor=PALE_YELLOW)
    summary["A3"].alignment = Alignment(horizontal="center")
    add_header(
        summary,
        5,
        ["Modernization motion", "Annual savings", "N-year net benefit", "One-time investment"],
    )
    summary["A6"] = "SQL renewal -> Azure SQL"
    summary["B6"] = "=SQL_TCO!B12"
    summary["C6"] = "=SQL_TCO!B11"
    summary["D6"] = "=SQL_TCO!B8"
    summary["A7"] = "Synapse -> Microsoft Fabric"
    summary["B7"] = "=Synapse_to_Fabric!H15"
    summary["C7"] = f"=B7*{refs['years']}-D7"
    summary["D7"] = f'={refs["migwl"]}*COUNTA(Synapse_to_Fabric!A4:A13)'
    summary["A8"] = "Combined opportunity"
    for column in "BCD":
        summary[f"{column}8"] = f"=SUM({column}6:{column}7)"
    style_table_body(summary, 6, 8, 4)
    for row in (6, 7, 8):
        for column in "BCD":
            summary[f"{column}{row}"].number_format = USD
    for column in range(1, 5):
        summary.cell(row=8, column=column).font = Font(
            name=FONT,
            bold=True,
            color=GREEN if column > 1 else INK,
        )

    summary["A10"] = "SQL payback"
    summary["B10"] = "=SQL_TCO!B13"
    summary["B10"].number_format = '0.0 "months"'
    summary["C10"] = "Analysis horizon"
    summary["D10"] = f"={refs['years']}"
    summary["D10"].number_format = '0 "years"'
    for cell in ("A10", "C10"):
        summary[cell].font = Font(name=FONT, bold=True, color=TEAL)

    add_header(summary, 12, ["Year", "Stay on-premises", "Migrate to Azure SQL"])
    for row, year in enumerate(range(0, 6), 13):
        summary.cell(row=row, column=1, value=year)
        if year == 0:
            summary.cell(row=row, column=2, value=0)
            summary.cell(row=row, column=3, value="=SQL_TCO!B8")
        else:
            summary.cell(
                row=row,
                column=2,
                value=f'=IF(A{row}<={refs["years"]},A{row}*SQL_TCO!B4,NA())',
            )
            summary.cell(
                row=row,
                column=3,
                value=f'=IF(A{row}<={refs["years"]},SQL_TCO!B8+A{row}*SQL_TCO!B7,NA())',
            )
        summary.cell(row=row, column=2).number_format = USD
        summary.cell(row=row, column=3).number_format = USD
    style_table_body(summary, 13, 18, 3)

    savings_chart = BarChart()
    savings_chart.type = "col"
    savings_chart.style = 10
    savings_chart.title = "Annual savings by motion"
    savings_chart.y_axis.title = "Annual savings ($)"
    savings_chart.height = 7.2
    savings_chart.width = 11.2
    savings_chart.add_data(
        Reference(summary, min_col=2, min_row=5, max_row=7),
        titles_from_data=True,
    )
    savings_chart.set_categories(Reference(summary, min_col=1, min_row=6, max_row=7))
    savings_chart.legend = None
    summary.add_chart(savings_chart, "F5")

    cumulative_chart = LineChart()
    cumulative_chart.style = 13
    cumulative_chart.title = "SQL cumulative cost"
    cumulative_chart.y_axis.title = "Cumulative cost ($)"
    cumulative_chart.x_axis.title = "Year"
    cumulative_chart.height = 7.2
    cumulative_chart.width = 11.2
    cumulative_chart.add_data(
        Reference(summary, min_col=2, max_col=3, min_row=12, max_row=18),
        titles_from_data=True,
    )
    cumulative_chart.set_categories(
        Reference(summary, min_col=1, min_row=13, max_row=18)
    )
    summary.add_chart(cumulative_chart, "F20")
    summary.column_dimensions["A"].width = 34
    for column in "BCD":
        summary.column_dimensions[column].width = 21
    summary.freeze_panes = "A5"

    sensitivity = wb.create_sheet("Sensitivity")
    sensitivity.sheet_properties.tabColor = TEAL
    set_title(
        sensitivity,
        "Scenario Sensitivity",
        "Stress-test the investment case by changing cost and migration assumptions.",
        8,
    )
    add_header(
        sensitivity,
        3,
        [
            "Scenario",
            "On-prem cost factor",
            "Azure SQL cost factor",
            "Migration cost factor",
            "Fabric cost factor",
            "SQL N-year benefit",
            "Fabric annual savings",
            "Combined N-year benefit",
        ],
    )
    scenarios = [
        ("Downside", 0.90, 1.15, 1.25, 1.20),
        ("Base", 1.00, 1.00, 1.00, 1.00),
        ("Upside", 1.10, 0.90, 0.85, 0.85),
    ]
    for row, scenario in enumerate(scenarios, 4):
        for column, value in enumerate(scenario, 1):
            sensitivity.cell(row=row, column=column, value=value)
        sensitivity.cell(
            row=row,
            column=6,
            value=(
                f"=(SQL_TCO!$B$4*B{row}*{refs['years']})"
                f"-(SQL_TCO!$B$7*C{row}*{refs['years']}+SQL_TCO!$B$8*D{row})"
            ),
        )
        sensitivity.cell(
            row=row,
            column=7,
            value=(
                f"=(Synapse_to_Fabric!$B$15*12)"
                f"-(Synapse_to_Fabric!$F$15*12*E{row})"
            ),
        )
        sensitivity.cell(
            row=row,
            column=8,
            value=f"=F{row}+(G{row}*{refs['years']})-(Summary!$D$7*D{row})",
        )
        for column in range(2, 6):
            sensitivity.cell(row=row, column=column).number_format = "0%"
        for column in range(6, 9):
            sensitivity.cell(row=row, column=column).number_format = USD
        if scenario[0] == "Base":
            for column in range(1, 9):
                sensitivity.cell(row=row, column=column).fill = PatternFill(
                    "solid",
                    fgColor=PALE_TEAL,
                )
                sensitivity.cell(row=row, column=column).font = Font(
                    name=FONT,
                    bold=True,
                    color=INK,
                )
    style_table_body(sensitivity, 4, 6, 8)
    sensitivity.conditional_formatting.add(
        "H4:H6",
        ColorScaleRule(
            start_type="min",
            start_color="FDE7E9",
            mid_type="percentile",
            mid_value=50,
            mid_color="FFF4CE",
            end_type="max",
            end_color="DFF6DD",
        ),
    )
    scenario_chart = BarChart()
    scenario_chart.type = "col"
    scenario_chart.style = 10
    scenario_chart.title = "Combined benefit by scenario"
    scenario_chart.y_axis.title = "N-year net benefit ($)"
    scenario_chart.height = 8
    scenario_chart.width = 15
    scenario_chart.add_data(
        Reference(sensitivity, min_col=8, min_row=3, max_row=6),
        titles_from_data=True,
    )
    scenario_chart.set_categories(
        Reference(sensitivity, min_col=1, min_row=4, max_row=6)
    )
    scenario_chart.legend = None
    sensitivity.add_chart(scenario_chart, "A9")
    for column, width in zip("ABCDEFGH", (16, 18, 18, 18, 18, 21, 21, 24)):
        sensitivity.column_dimensions[column].width = width
    sensitivity.freeze_panes = "A4"

    for sheet in wb.worksheets:
        sheet.sheet_view.showGridLines = False

    output.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output)
    return output


if __name__ == "__main__":
    generated = build_workbook()
    print(f"Generated {generated}")
