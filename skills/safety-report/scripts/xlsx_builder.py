#!/usr/bin/env python3
"""
xlsx_builder.py - Excel deliverables safety teams actually keep using: live formulas, dropdowns,
traffic lights, frozen headers, filters, and a heatmap that updates when they edit a score.

from xlsx_builder import build_risk_register, build_scorecard
"""
from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

INK, ACCENT = "1F2430", "5B47E0"
RAGF = {"Low": "C8E6D2", "Medium": "FCE8A6", "High": "F9C99B", "Extreme": "F4B4B4", "Green": "C8E6D2", "Amber": "FCE8A6", "Red": "F4B4B4"}
HDR = PatternFill("solid", fgColor=ACCENT)
THIN = Border(*(Side(style="thin", color="E5E7EB"),) * 4)
WRAP = Alignment(wrap_text=True, vertical="top")

def _header(ws, row, headers, widths=None):
    for j, h in enumerate(headers, 1):
        c = ws.cell(row=row, column=j, value=h)
        c.font = Font(bold=True, color="FFFFFF"); c.fill = HDR; c.alignment = Alignment(wrap_text=True, vertical="center")
        if widths:
            ws.column_dimensions[get_column_letter(j)].width = widths[j - 1]
    ws.freeze_panes = ws.cell(row=row + 1, column=3)

def _title(ws, title, subtitle):
    ws["A1"] = title; ws["A1"].font = Font(bold=True, size=15, color=INK)
    ws["A2"] = subtitle; ws["A2"].font = Font(italic=True, size=9, color="6B7280")

def _band_formula(cell):
    return f'=IF({cell}="","",IF({cell}>=15,"Extreme",IF({cell}>=10,"High",IF({cell}>=5,"Medium","Low"))))'

def _rag_rules(ws, rng):
    for name in ("Extreme", "High", "Medium", "Low", "Red", "Amber", "Green"):
        ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=[f'"{name}"'], fill=PatternFill("solid", fgColor=RAGF[name])))

REG_COLS = [
    ("ID", 7), ("Site / activity", 22), ("Hazard", 22), ("Risk event (what could go wrong)", 34), ("Who is exposed", 16),
    ("Existing controls", 40), ("Control types (hierarchy)", 18), ("Control effectiveness", 14),
    ("Inherent L", 9), ("Inherent C", 9), ("Inherent score", 9), ("Inherent rating", 11),
    ("Residual L", 9), ("Residual C", 9), ("Residual score", 9), ("Residual rating", 11),
    ("Critical risk?", 9), ("Critical controls (must never fail)", 40), ("Additional controls needed", 40),
    ("Owner", 16), ("Review date", 12), ("Status", 11), ("Change notes", 30),
]
KEYS = ["id", "activity", "hazard", "risk_event", "exposed", "existing_controls", "control_types", "effectiveness",
        "inh_l", "inh_c", None, None, "res_l", "res_c", None, None, "critical", "critical_controls", "additional_controls",
        "owner", "review_date", "status", "change_notes"]

def build_risk_register(rows, path, org="", jurisdiction="", matrix_note="", gaps=None, critical_controls=None, summary=None):
    """rows: list of dicts with KEYS. gaps: list of (severity, finding, rows_affected, fix).
    critical_controls: list of dicts {risk, control, performance_standard, verification, frequency, owner}."""
    wb = Workbook()
    # ---- Summary
    s = wb.active; s.title = "Summary"
    _title(s, f"{org} Risk Register".strip(), f"{jurisdiction}  |  {matrix_note}")
    s.column_dimensions["A"].width = 110
    r = 4
    for line in (summary or []):
        s.cell(row=r, column=1, value=line).alignment = WRAP; r += 1
    # ---- Register
    ws = wb.create_sheet("Register")
    _title(ws, "Risk register", "Scores and ratings are live formulas: change L or C and the rating and heatmap update.")
    _header(ws, 4, [c[0] for c in REG_COLS], [c[1] for c in REG_COLS])
    for i, row in enumerate(rows):
        rr = 5 + i
        for j, key in enumerate(KEYS, 1):
            if key:
                v = row.get(key, "")
                c = ws.cell(row=rr, column=j, value=v); c.alignment = WRAP; c.border = THIN
        ws.cell(row=rr, column=11, value=f'=IF(OR(I{rr}="",J{rr}=""),"",I{rr}*J{rr})')
        ws.cell(row=rr, column=12, value=_band_formula(f"K{rr}"))
        ws.cell(row=rr, column=15, value=f'=IF(OR(M{rr}="",N{rr}=""),"",M{rr}*N{rr})')
        ws.cell(row=rr, column=16, value=_band_formula(f"O{rr}"))
        for j in (11, 12, 15, 16):
            ws.cell(row=rr, column=j).border = THIN; ws.cell(row=rr, column=j).alignment = Alignment(horizontal="center", vertical="top")
    last = 4 + max(len(rows), 1)
    _rag_rules(ws, f"L5:L{last + 200}"); _rag_rules(ws, f"P5:P{last + 200}")
    ws.conditional_formatting.add(f"Q5:Q{last + 200}", CellIsRule(operator="equal", formula=['"Y"'], fill=PatternFill("solid", fgColor="F4B4B4")))
    ws.conditional_formatting.add(f"U5:U{last + 200}", FormulaRule(formula=[f'AND(U5<>"",U5<TODAY())'], fill=PatternFill("solid", fgColor="F4B4B4")))
    for col, opts in (("I", "1,2,3,4,5"), ("J", "1,2,3,4,5"), ("M", "1,2,3,4,5"), ("N", "1,2,3,4,5"),
                      ("H", "Effective,Partially effective,Ineffective,Not verified"), ("Q", "Y,N"),
                      ("V", "Open,In progress,Controlled,Closed")):
        dv = DataValidation(type="list", formula1=f'"{opts}"', allow_blank=True); ws.add_data_validation(dv); dv.add(f"{col}5:{col}{last + 200}")
    ws.auto_filter.ref = f"A4:W{last}"
    for rr in range(5, last + 1):
        ws.cell(row=rr, column=21).number_format = "dd-mmm-yyyy"
    # ---- Heatmap (live COUNTIFS)
    hm = wb.create_sheet("Heatmap")
    _title(hm, "Risk heatmap", "Counts update automatically from the Register sheet.")
    labelsC = ["Insignificant", "Minor", "Moderate", "Major", "Catastrophic"]; labelsL = ["Almost certain", "Likely", "Possible", "Unlikely", "Rare"]
    for block, (lcol, ccol, top) in enumerate((("I", "J", 4), ("M", "N", 13))):
        hm.cell(row=top, column=1, value="Inherent risk" if block == 0 else "Residual risk").font = Font(bold=True, color=INK)
        for j, lab in enumerate(labelsC):
            hm.cell(row=top + 6, column=2 + j, value=lab).font = Font(size=9, color="6B7280")
        for i, lab in enumerate(labelsL):
            L = 5 - i
            hm.cell(row=top + 1 + i, column=1, value=lab).font = Font(size=9, color="6B7280")
            for C in range(1, 6):
                c = hm.cell(row=top + 1 + i, column=1 + C, value=f'=COUNTIFS(Register!{lcol}:{lcol},{L},Register!{ccol}:{ccol},{C})')
                sc = L * C
                b = "Extreme" if sc >= 15 else "High" if sc >= 10 else "Medium" if sc >= 5 else "Low"
                c.fill = PatternFill("solid", fgColor=RAGF[b]); c.alignment = Alignment(horizontal="center", vertical="center")
                c.font = Font(bold=True, size=13); c.border = THIN
                hm.row_dimensions[top + 1 + i].height = 30
    hm.column_dimensions["A"].width = 16
    for j in range(2, 7):
        hm.column_dimensions[get_column_letter(j)].width = 12
    # ---- Critical controls
    if critical_controls:
        cc = wb.create_sheet("Critical controls")
        _title(cc, "Critical controls and verification", "The controls that must never fail, and how you prove they are working.")
        hdrs = [("Critical risk", 26), ("Critical control", 34), ("Performance standard (what good looks like)", 40),
                ("How it is verified", 34), ("Frequency", 12), ("Owner", 16), ("Last verified", 12), ("Result", 12)]
        _header(cc, 4, [h[0] for h in hdrs], [h[1] for h in hdrs])
        for i, row in enumerate(critical_controls):
            for j, k in enumerate(["risk", "control", "performance_standard", "verification", "frequency", "owner", "last_verified", "result"], 1):
                c = cc.cell(row=5 + i, column=j, value=row.get(k, "")); c.alignment = WRAP; c.border = THIN
    # ---- Gaps
    if gaps:
        g = wb.create_sheet("Gaps found")
        _title(g, "Gaps found in review", "Most serious first.")
        _header(g, 4, ["Priority", "Finding", "Rows affected", "Recommended fix"], [10, 60, 16, 60])
        for i, (sev, finding, rows_aff, fix) in enumerate(gaps):
            for j, v in enumerate((sev, finding, rows_aff, fix), 1):
                c = g.cell(row=5 + i, column=j, value=v); c.alignment = WRAP; c.border = THIN
        _rag_rules(g, f"A5:A{5 + len(gaps)}")
    wb.save(path)
    return path

def build_scorecard(kris, path, org="", period="", basis="", sections=None):
    """kris: list of dicts {group: 'Lead'|'Lag', kri, this, last, target, status (Green/Amber/Red), note}.
    sections: optional dict sheet_name -> (headers, rows) for extra tabs (e.g. site breakdown, overdue actions)."""
    wb = Workbook(); ws = wb.active; ws.title = "KRI scorecard"
    _title(ws, f"{org} Safety KRI scorecard - {period}".strip(" -"), basis)
    _header(ws, 4, ["Type", "KRI", "This period", "Last period", "Change", "Target", "Status", "What it means"], [8, 36, 12, 12, 10, 10, 10, 60])
    for i, k in enumerate(kris):
        r = 5 + i
        vals = [k.get("group"), k.get("kri"), k.get("this"), k.get("last"), None, k.get("target"), k.get("status"), k.get("note")]
        for j, v in enumerate(vals, 1):
            c = ws.cell(row=r, column=j, value=v); c.alignment = WRAP; c.border = THIN
        ws.cell(row=r, column=5, value=f'=IF(AND(ISNUMBER(C{r}),ISNUMBER(D{r})),C{r}-D{r},"")').border = THIN
    _rag_rules(ws, f"G5:G{5 + len(kris)}")
    ws.freeze_panes = "C5"
    for name, (headers, rows) in (sections or {}).items():
        sh = wb.create_sheet(name[:31])
        _title(sh, name, "")
        _header(sh, 4, headers, [max(12, min(50, len(str(h)) + 10)) for h in headers])
        for i, row in enumerate(rows):
            for j, v in enumerate(row, 1):
                c = sh.cell(row=5 + i, column=j, value=v); c.alignment = WRAP; c.border = THIN
        sh.auto_filter.ref = f"A4:{get_column_letter(len(headers))}{4 + max(len(rows), 1)}"
    wb.save(path)
    return path

def recalc(path):
    """Store calculated values alongside formulas so previews (Mail, Teams, Google Drive, Claude) show numbers,
    not blanks. Uses LibreOffice if available; otherwise leaves the file as is (Excel recalculates on open)."""
    import os, shutil, subprocess, tempfile
    exe = shutil.which("soffice") or shutil.which("libreoffice")
    if not exe:
        return False
    out = tempfile.mkdtemp()
    try:
        subprocess.run([exe, "--headless", "--calc", "--convert-to", "xlsx", "--outdir", out, path],
                       check=True, capture_output=True, timeout=120)
        res = os.path.join(out, os.path.basename(path))
        if os.path.exists(res):
            shutil.move(res, path)
            return True
    except Exception:
        pass
    return False
