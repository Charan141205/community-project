# build_complete_mbu_report.py
"""
Master Builder for Mohan Babu University (MBU) TESP Project Report.
Final Refactoring Pass Addressing All 5 Audit Points:
1. Complete removal of leftover "Name of Student4" placeholder on Certificate page.
2. Code indentation strictly preserved with xml:space="preserve" in light grey shaded boxes (Consolas 9.5pt).
3. 4 comprehensive Bio-Data tables for all 4 project members with valid contact details.
4. Consistent 0.5pt grey grid borders for TOC, Acronyms, Figures, and Tables.
5. Synchronized page numbers across the 65+ page document.
"""

import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

import report_data_frontmatter as fm
import report_data_ch1_ch2 as c12
import report_data_ch3_ch4 as c34
import report_data_ch5_ch6_ch7 as c567
import report_data_appendix as appx

TEMPLATE_PATH = r"C:\Users\lagis\.gemini\antigravity\brain\423ccfeb-6e73-4ebd-ac74-a55be441797b\.user_uploaded\media_1794146452121_1c593d55.docx"
OUT_WORKSPACE_DOCX = r"C:\Users\lagis\Documents\Community Project\MBU_TESP_Project_Report_Flood_EWS.docx"
OUT_ARTIFACT_DOCX = r"C:\Users\lagis\.gemini\antigravity\brain\423ccfeb-6e73-4ebd-ac74-a55be441797b\MBU_TESP_Project_Report_Flood_EWS.docx"

# Converted PNG image paths
IMG_DIR = r"C:\Users\lagis\Documents\Community Project\scripts\report_images"
IMG_SCHEMATIC = os.path.join(IMG_DIR, "schematic.png")
IMG_BREADBOARD = os.path.join(IMG_DIR, "breadboard.png")
IMG_SERIAL_LOG = os.path.join(IMG_DIR, "serial_log.png")
IMG_SLIDER_CALIB = os.path.join(IMG_DIR, "slider_calib.png")
IMG_OPS_CRITICAL = os.path.join(IMG_DIR, "ops_critical.png")
IMG_OPS_MODAL = os.path.join(IMG_DIR, "ops_modal.png")
IMG_PUBLIC_MAP = os.path.join(IMG_DIR, "public_map.png")
IMG_STORM_OPS = os.path.join(IMG_DIR, "storm_ops.png")


def set_run_font(run, font_name="Times New Roman", size_pt=12, bold=False, italic=False, color_rgb=(0, 0, 0)):
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = RGBColor(*color_rgb)


def format_paragraph(p, align=WD_ALIGN_PARAGRAPH.JUSTIFY, line_spacing=1.5, space_before=0, space_after=6):
    p.paragraph_format.alignment = align
    p.paragraph_format.line_spacing = line_spacing
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)


def add_p(before_el, text, font_name="Times New Roman", size_pt=12, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY, line_spacing=1.5, space_before=0, space_after=6, color_rgb=(0,0,0)):
    p = before_el.insert_paragraph_before()
    format_paragraph(p, align=align, line_spacing=line_spacing, space_before=space_before, space_after=space_after)
    r = p.add_run(text)
    set_run_font(r, font_name=font_name, size_pt=size_pt, bold=bold, italic=italic, color_rgb=color_rgb)
    return p


def add_bullet_item(before_el, text):
    p = before_el.insert_paragraph_before()
    format_paragraph(p, align=WD_ALIGN_PARAGRAPH.LEFT, line_spacing=1.15, space_before=0, space_after=4)
    p.paragraph_format.left_indent = Inches(0.3)
    p.paragraph_format.first_line_indent = Inches(-0.18)
    r_sym = p.add_run("•  ")
    set_run_font(r_sym, font_name="Times New Roman", size_pt=12, bold=True)
    r_txt = p.add_run(text)
    set_run_font(r_txt, font_name="Times New Roman", size_pt=12, bold=False)
    return p


def add_chapter_heading(before_el, chap_num_str, chap_title_str):
    p1 = before_el.insert_paragraph_before()
    format_paragraph(p1, align=WD_ALIGN_PARAGRAPH.CENTER, line_spacing=1.5, space_before=16, space_after=2)
    r1 = p1.add_run(chap_num_str)
    set_run_font(r1, font_name="Times New Roman", size_pt=14, bold=True, color_rgb=(0, 0, 0))

    p2 = before_el.insert_paragraph_before()
    format_paragraph(p2, align=WD_ALIGN_PARAGRAPH.CENTER, line_spacing=1.5, space_before=0, space_after=14)
    r2 = p2.add_run(chap_title_str)
    set_run_font(r2, font_name="Times New Roman", size_pt=14, bold=True, color_rgb=(0, 0, 0))


def add_h2(before_el, text):
    p = before_el.insert_paragraph_before()
    format_paragraph(p, align=WD_ALIGN_PARAGRAPH.LEFT, line_spacing=1.5, space_before=12, space_after=6)
    r = p.add_run(text)
    set_run_font(r, font_name="Times New Roman", size_pt=12, bold=True, color_rgb=(0, 0, 0))
    return p


def add_h3(before_el, text):
    p = before_el.insert_paragraph_before()
    format_paragraph(p, align=WD_ALIGN_PARAGRAPH.LEFT, line_spacing=1.5, space_before=8, space_after=4)
    r = p.add_run(text)
    set_run_font(r, font_name="Times New Roman", size_pt=12, bold=True, italic=True, color_rgb=(30, 30, 30))
    return p


def add_page_break(before_el):
    p = before_el.insert_paragraph_before()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.add_run().add_break(WD_BREAK.PAGE)


def style_table_borders(tbl, border_color="CCCCCC", sz="4"):
    for row in tbl.rows:
        for cell in row.cells:
            tcPr = cell._tc.get_or_add_tcPr()
            tcBorders = parse_xml(
                r'<w:tcBorders %s>'
                r'<w:top w:val="single" w:sz="%s" w:space="0" w:color="%s"/>'
                r'<w:left w:val="single" w:sz="%s" w:space="0" w:color="%s"/>'
                r'<w:bottom w:val="single" w:sz="%s" w:space="0" w:color="%s"/>'
                r'<w:right w:val="single" w:sz="%s" w:space="0" w:color="%s"/>'
                r'</w:tcBorders>' % (nsdecls('w'), sz, border_color, sz, border_color, sz, border_color, sz, border_color)
            )
            tcPr.append(tcBorders)


def add_table_data(doc, before_el, headers, rows_data, col_widths=None):
    tbl = doc.add_table(rows=len(rows_data) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Format Headers
    for c_idx, h_text in enumerate(headers):
        cell = tbl.cell(0, c_idx)
        cell.text = h_text
        tcPr = cell._tc.get_or_add_tcPr()
        shd = parse_xml(r'<w:shd %s w:fill="D9D9D9"/>' % nsdecls('w'))
        tcPr.append(shd)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(2)
        if len(p.runs) > 0:
            set_run_font(p.runs[0], font_name="Times New Roman", size_pt=10, bold=True, color_rgb=(0, 0, 0))

    # Format Data Rows
    for r_idx, row_vals in enumerate(rows_data):
        row_num = r_idx + 1
        for c_idx, val in enumerate(row_vals):
            cell = tbl.cell(row_num, c_idx)
            cell.text = str(val)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx != 0 else WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_after = Pt(2)
            if len(p.runs) > 0:
                set_run_font(p.runs[0], font_name="Times New Roman", size_pt=9.5, bold=False, color_rgb=(0, 0, 0))

    # Apply 0.5pt subtle grey borders
    style_table_borders(tbl, border_color="000000", sz="4")

    # Set Column Widths if provided
    if col_widths:
        for row in tbl.rows:
            for c_idx, w in enumerate(col_widths):
                if c_idx < len(row.cells):
                    row.cells[c_idx].width = Inches(w)

    # Move table before before_el
    before_el._p.addprevious(tbl._tbl)

    # Spacer after table
    p_sp = before_el.insert_paragraph_before()
    p_sp.paragraph_format.space_before = Pt(4)
    p_sp.paragraph_format.space_after = Pt(6)


def add_figure(before_el, img_path, fig_no, caption_text, width_inches=5.2):
    if not os.path.exists(img_path):
        print(f"[WARN] Image path does not exist: {img_path}")
        return

    p_img = before_el.insert_paragraph_before()
    p_img.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(8)
    p_img.paragraph_format.space_after = Pt(4)
    r_img = p_img.add_run()
    r_img.add_picture(img_path, width=Inches(width_inches))

    p_cap = before_el.insert_paragraph_before()
    p_cap.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(2)
    p_cap.paragraph_format.space_after = Pt(10)
    r_cap = p_cap.add_run(f"Figure {fig_no}: {caption_text}")
    set_run_font(r_cap, font_name="Times New Roman", size_pt=10, bold=True, italic=True, color_rgb=(0, 0, 0))


def add_code_box(doc, before_el, rel_path):
    """
    Inserts complete, unabridged source code inside a light grey shaded box (5% tint)
    with a 0.5pt border and strictly preserved 4-space indentation using xml:space="preserve".
    """
    full_path = os.path.join(r"C:\Users\lagis\Documents\Community Project", rel_path)
    if not os.path.exists(full_path):
        add_p(before_el, f"[ERROR] Code file {rel_path} not found.")
        return

    with open(full_path, "r", encoding="utf-8", errors="replace") as f:
        code_lines = f.readlines()

    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    tcPr = cell._tc.get_or_add_tcPr()

    # 5% tint light gray background (#F8F9FA)
    shd = parse_xml(r'<w:shd %s w:fill="F8F9FA"/>' % nsdecls('w'))
    tcPr.append(shd)

    # 0.5pt subtle grey border with left accent (#1B365D)
    tcBorders = parse_xml(
        r'<w:tcBorders %s>'
        r'<w:top w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>'
        r'<w:left w:val="single" w:sz="12" w:space="0" w:color="1B365D"/>'
        r'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>'
        r'<w:right w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>'
        r'</w:tcBorders>' % nsdecls('w')
    )
    tcPr.append(tcBorders)

    # Cell padding
    tcMar = parse_xml(
        r'<w:tcMar %s>'
        r'<w:top w:w="120" w:type="dxa"/>'
        r'<w:bottom w:w="120" w:type="dxa"/>'
        r'<w:left w:w="160" w:type="dxa"/>'
        r'<w:right w:w="160" w:type="dxa"/>'
        r'</w:tcMar>' % nsdecls('w')
    )
    tcPr.append(tcMar)

    for i, line in enumerate(code_lines):
        line_clean = line.rstrip("\r\n")
        if i == 0:
            p = cell.paragraphs[0]
        else:
            p = cell.add_paragraph()
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT

        r = p.add_run(line_clean if line_clean else " ")
        set_run_font(r, font_name="Consolas", size_pt=9.5, bold=False, color_rgb=(25, 25, 25))
        t = r._element.find(qn('w:t'))
        if t is not None:
            t.set(qn('xml:space'), 'preserve')

    # Move table before before_el
    before_el._p.addprevious(tbl._tbl)

    p_sp = before_el.insert_paragraph_before()
    p_sp.paragraph_format.space_before = Pt(4)
    p_sp.paragraph_format.space_after = Pt(8)


def main():
    print("[1/6] Loading base docx template...")
    doc = docx.Document(TEMPLATE_PATH)

    # Apply 1-inch margins to all sections
    for sec in doc.sections:
        sec.top_margin = Inches(1.0)
        sec.bottom_margin = Inches(1.0)
        sec.left_margin = Inches(1.0)
        sec.right_margin = Inches(1.0)

    # 1. Update Title across Cover page, Certificate, and Declaration
    for p in doc.paragraphs:
        if "Title of the Project" in p.text:
            p.text = p.text.replace("Title of the Project", fm.PROJECT_TITLE)
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.bold = True

    # 2. Update Student Names on Cover Page
    for i, p in enumerate(doc.paragraphs[:30]):
        if "Submitted by" in p.text:
            for j in range(1, 5):
                idx = i + j
                if idx < len(doc.paragraphs):
                    st_name, st_roll = fm.STUDENTS[j-1]
                    doc.paragraphs[idx].text = f"\t{st_name}\t-\t{st_roll}"
                    for r in doc.paragraphs[idx].runs:
                        set_run_font(r, font_name="Times New Roman", size_pt=11, bold=True)
            break

    # 3. Update Supervisor on Cover Page
    for i, p in enumerate(doc.paragraphs[:30]):
        if "Under the Esteemed Supervision of" in p.text:
            if i + 1 < len(doc.paragraphs):
                doc.paragraphs[i+1].text = fm.SUPERVISOR_NAME
                set_run_font(doc.paragraphs[i+1].runs[0], font_name="Times New Roman", size_pt=11, bold=True)
            if i + 2 < len(doc.paragraphs):
                doc.paragraphs[i+2].text = fm.SUPERVISOR_DESIG
                set_run_font(doc.paragraphs[i+2].runs[0], font_name="Times New Roman", size_pt=11)
            if i + 3 < len(doc.paragraphs):
                doc.paragraphs[i+3].text = fm.SUPERVISOR_DEPT
                set_run_font(doc.paragraphs[i+3].runs[0], font_name="Times New Roman", size_pt=11)
            break

    # 4. FIX CERTIFICATE PAGE: Populate 4 students and REMOVE leftover Name of Student4
    for i, p in enumerate(doc.paragraphs[30:50]):
        actual_idx = 30 + i
        if "is the Bonafide work done by" in p.text:
            # Lines 38, 39, 40, 41 get students 1, 2, 3, 4
            for j in range(4):
                idx = actual_idx + 1 + j
                if idx < len(doc.paragraphs):
                    st_name, st_roll = fm.STUDENTS[j]
                    doc.paragraphs[idx].text = f"\t{st_name}\t-\t{st_roll}"
                    for r in doc.paragraphs[idx].runs:
                        set_run_font(r, font_name="Times New Roman", size_pt=11, bold=True)
            # Line 42 was the leftover "Name of Student4" placeholder -> COMPLETELY CLEAR IT
            leftover_idx = actual_idx + 5
            if leftover_idx < len(doc.paragraphs) and "Name of Student4" in doc.paragraphs[leftover_idx].text:
                doc.paragraphs[leftover_idx].text = ""
                # remove any residual runs
                for r in doc.paragraphs[leftover_idx].runs:
                    r.text = ""
            break

    # Update Table 0 (Supervisor / HOD in Certificate)
    tbl0 = doc.tables[0]
    tbl0.rows[1].cells[0].text = f"{fm.SUPERVISOR_NAME}\n{fm.SUPERVISOR_DESIG}\n{fm.SUPERVISOR_DEPT}"
    tbl0.rows[1].cells[1].text = f"{fm.HOD_NAME}\n{fm.HOD_DESIG}\n{fm.HOD_DEPT}"
    for cell in tbl0.rows[1].cells:
        for p in cell.paragraphs:
            p.paragraph_format.line_spacing = 1.15
            for r in p.runs:
                set_run_font(r, font_name="Times New Roman", size_pt=10)

    # 5. Update Acknowledgement Page
    for p in doc.paragraphs[50:65]:
        if "Name of Faculty Supervisor" in p.text:
            p.text = p.text.replace("Name of Faculty Supervisor, Designation, Department of ECE", f"{fm.SUPERVISOR_NAME}, {fm.SUPERVISOR_DESIG} {fm.SUPERVISOR_DEPT}")
            for r in p.runs:
                set_run_font(r, font_name="Times New Roman", size_pt=11)

    ack_st_start = None
    for i, p in enumerate(doc.paragraphs[55:70]):
        actual_idx = 55 + i
        if "Name of Student1" in p.text or "Lagisetty" in p.text:
            ack_st_start = actual_idx
            break

    if ack_st_start:
        for j in range(4):
            idx = ack_st_start + j
            if idx < len(doc.paragraphs):
                st_name, st_roll = fm.STUDENTS[j]
                doc.paragraphs[idx].text = f"\t{st_name}\t{st_roll}"
                for r in doc.paragraphs[idx].runs:
                    set_run_font(r, font_name="Times New Roman", size_pt=11, bold=True)

    # 6. Update Declaration Page
    decl_st_start = None
    for i, p in enumerate(doc.paragraphs[65:80]):
        actual_idx = 65 + i
        if "Name of Student1" in p.text or "Lagisetty" in p.text:
            decl_st_start = actual_idx
            break

    if decl_st_start:
        for j in range(4):
            idx = decl_st_start + j
            if idx < len(doc.paragraphs):
                st_name, st_roll = fm.STUDENTS[j]
                doc.paragraphs[idx].text = f"\t{st_name}\t{st_roll}"
                for r in doc.paragraphs[idx].runs:
                    set_run_font(r, font_name="Times New Roman", size_pt=11, bold=True)

    # 7. Update Abstract Text
    for p in doc.paragraphs:
        if "All the text should be in font: verdana" in p.text or "Urban flash flooding presents an escalating hazard" in p.text:
            p.text = fm.ABSTRACT_TEXT
            format_paragraph(p, align=WD_ALIGN_PARAGRAPH.JUSTIFY, line_spacing=1.5)
            for r in p.runs:
                set_run_font(r, font_name="Times New Roman", size_pt=12, bold=False)
            break

    # 8. Populate Table 5 (Acronyms) with 0.5pt Grey Grid Borders
    tbl_acronyms = doc.tables[5]
    while len(tbl_acronyms.rows) > 1:
        tbl_acronyms._tbl.remove(tbl_acronyms.rows[1]._tr)
    for acronym, definition in fm.ACRONYMS:
        row = tbl_acronyms.add_row()
        row.cells[0].text = acronym
        row.cells[1].text = definition
        for cell in row.cells:
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_after = Pt(2)
            if len(p.runs) > 0:
                set_run_font(p.runs[0], font_name="Times New Roman", size_pt=10)
    style_table_borders(tbl_acronyms, border_color="CCCCCC", sz="4")

    # 9. Populate Table 6 (Figures) with 0.5pt Grey Grid Borders & Right-aligned Page No
    tbl_figures = doc.tables[6]
    while len(tbl_figures.rows) > 1:
        tbl_figures._tbl.remove(tbl_figures.rows[1]._tr)
    for fig_no, caption, page_no in fm.FIGURES:
        row = tbl_figures.add_row()
        row.cells[0].text = fig_no
        row.cells[1].text = caption
        row.cells[2].text = page_no
        for c_idx, cell in enumerate(row.cells):
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_after = Pt(2)
            if c_idx == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            elif c_idx == 1:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            if len(p.runs) > 0:
                set_run_font(p.runs[0], font_name="Times New Roman", size_pt=10)
    style_table_borders(tbl_figures, border_color="CCCCCC", sz="4")

    # 10. Populate Table 7 (Tables) with 0.5pt Grey Grid Borders & Right-aligned Page No
    tbl_tables = doc.tables[7]
    while len(tbl_tables.rows) > 1:
        tbl_tables._tbl.remove(tbl_tables.rows[1]._tr)
    for tbl_no, caption, page_no in fm.TABLES:
        row = tbl_tables.add_row()
        row.cells[0].text = tbl_no
        row.cells[1].text = caption
        row.cells[2].text = page_no
        for c_idx, cell in enumerate(row.cells):
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_after = Pt(2)
            if c_idx == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            elif c_idx == 1:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            if len(p.runs) > 0:
                set_run_font(p.runs[0], font_name="Times New Roman", size_pt=10)
    style_table_borders(tbl_tables, border_color="CCCCCC", sz="4")

    # 11. Populate Table 4 (Table of Contents) with 0.5pt Grey Grid Borders & Right-aligned Page No
    tbl_toc = doc.tables[4]
    while len(tbl_toc.rows) > 1:
        tbl_toc._tbl.remove(tbl_toc.rows[1]._tr)
    for chapter_title, page_no in fm.TOC_ENTRIES:
        row = tbl_toc.add_row()
        row.cells[0].text = chapter_title
        row.cells[1].text = page_no
        row.cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT
        row.cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
        for cell in row.cells:
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_after = Pt(1)
            if len(p.runs) > 0:
                is_bold = not chapter_title.startswith("  ")
                set_run_font(p.runs[0], font_name="Times New Roman", size_pt=10, bold=is_bold)
    style_table_borders(tbl_toc, border_color="CCCCCC", sz="4")

    print("[2/6] Cleaning up placeholder elements between Table 7 and Bio-Data...")
    bio_idx = None
    for i, el in enumerate(doc.element.body):
        if el.tag.endswith('p'):
            p = docx.text.paragraph.Paragraph(el, doc)
            if p.text.strip() == 'Bio-Data':
                bio_idx = i
                break

    tbl7_idx = None
    for i in range(bio_idx - 1, -1, -1):
        el = doc.element.body[i]
        if el.tag.endswith('tbl'):
            tbl7_idx = i
            break

    to_remove = [doc.element.body[j] for j in range(tbl7_idx + 1, bio_idx)]
    for el in to_remove:
        doc.element.body.remove(el)

    bio_p = None
    for p in doc.paragraphs:
        if p.text.strip() == "Bio-Data":
            bio_p = p
            break

    print("[3/6] Inserting Chapter 1 & Chapter 2...")
    add_page_break(bio_p)
    add_chapter_heading(bio_p, "CHAPTER 1", "INTRODUCTION")

    add_h2(bio_p, "1.1 Introduction")
    for para in c12.CH1_INTRO:
        add_p(bio_p, para)

    add_h2(bio_p, "1.2 Regional Catchment Analysis: Swarnamukhi Basin & Foothills")
    for para in c12.CH1_REGIONAL_ANALYSIS:
        add_p(bio_p, para)

    add_p(bio_p, "Table 1.1 details the 6 primary drainage flashpoints instrumented in this project:", bold=True)
    add_table_data(
        doc, bio_p,
        headers=["Node ID", "Flashpoint Name", "Latitude", "Longitude", "Ward", "Mount Ht", "Capacity", "Hydrological Context"],
        rows_data=c12.TABLE_1_1_DATA,
        col_widths=[0.8, 1.3, 0.7, 0.7, 0.8, 0.6, 0.6, 1.5]
    )

    add_h2(bio_p, "1.3 Problem Statement")
    for para in c12.CH1_PROBLEM_STATEMENT:
        add_p(bio_p, para)
    for item in c12.CH1_PROBLEM_ITEMS:
        add_bullet_item(bio_p, item)

    add_h2(bio_p, "1.4 Objectives of the Investigation")
    add_p(bio_p, c12.CH1_OBJECTIVES_INTRO)
    for item in c12.CH1_OBJECTIVES_ITEMS:
        add_bullet_item(bio_p, item)

    add_h2(bio_p, "1.5 Scope of the Project")
    add_p(bio_p, c12.CH1_SCOPE)

    add_h2(bio_p, "1.6 Real-World Applications & Societal Value")
    add_p(bio_p, c12.CH1_APPLICATIONS_INTRO)
    for item in c12.CH1_APPLICATIONS_ITEMS:
        add_bullet_item(bio_p, item)

    add_h2(bio_p, "1.7 Limitations & Operational Constraints")
    add_p(bio_p, c12.CH1_LIMITATIONS_INTRO)
    for item in c12.CH1_LIMITATIONS_ITEMS:
        add_bullet_item(bio_p, item)

    # Chapter 2: Literature Survey
    add_page_break(bio_p)
    add_chapter_heading(bio_p, "CHAPTER 2", "LITERATURE SURVEY")

    for title, paras in c12.CH2_LITERATURE_SURVEY:
        add_h2(bio_p, title)
        for p in paras:
            add_p(bio_p, p)
        if "2.4" in title:
            add_p(bio_p, c12.CH2_MQTT_TIERS_INTRO)
            for tier in c12.CH2_MQTT_TIERS:
                add_bullet_item(bio_p, tier)
            add_p(bio_p, c12.CH2_MQTT_CONCLUSION)

    for title, paras in c12.CH2_REMAINING_SECTIONS:
        add_h2(bio_p, title)
        for p in paras:
            add_p(bio_p, p)

    add_h2(bio_p, "2.8 Summary of Research Gaps and Problem Formulation")
    add_p(bio_p, c12.CH2_RESEARCH_GAPS_INTRO)
    for gap in c12.CH2_RESEARCH_GAPS:
        add_bullet_item(bio_p, gap)
    add_p(bio_p, c12.CH2_RESEARCH_GAPS_CONCLUSION)

    add_p(bio_p, "Table 2.1 presents a comparative synthesis of existing flood monitoring paradigms against flood-ews:", bold=True)
    add_table_data(
        doc, bio_p,
        headers=["Monitoring Paradigm", "Sensor Type", "Telemetry Protocol", "Processing Tier", "Edge Actuation", "Dynamic Routing", "Database Storage", "Citizen Alerts", "Deployment Cost"],
        rows_data=c12.TABLE_2_1_DATA,
        col_widths=[0.9, 0.8, 0.8, 0.8, 0.8, 0.5, 0.8, 0.8, 0.8]
    )

    print("[4/6] Inserting Chapter 3 & Chapter 4...")
    # Chapter 3: Analysis & Design
    add_page_break(bio_p)
    add_chapter_heading(bio_p, "CHAPTER 3", "ANALYSIS & DESIGN")

    add_h2(bio_p, "3.1 Requirement Analysis")
    add_p(bio_p, c34.CH3_REQ_INTRO)
    add_p(bio_p, c34.CH3_FR_INTRO, bold=True)
    for item in c34.CH3_FR_ITEMS:
        add_bullet_item(bio_p, item)
    add_p(bio_p, c34.CH3_NFR_INTRO, bold=True)
    for item in c34.CH3_NFR_ITEMS:
        add_bullet_item(bio_p, item)

    add_h2(bio_p, "3.2 Overall System Architecture & Data Flow")
    add_p(bio_p, c34.CH3_ARCH_INTRO)
    for layer in c34.CH3_ARCH_LAYERS:
        add_bullet_item(bio_p, layer)

    add_h2(bio_p, "3.3 Hardware Subsystem Design")
    for para in c34.CH3_HARDWARE[:3]:
        add_p(bio_p, para)

    add_h2(bio_p, "3.4 Pin Configuration and Circuit Schematic Design")
    add_p(bio_p, c34.CH3_HARDWARE[3])
    add_p(bio_p, "Table 3.1 details the ESP32 GPIO pin assignments and peripheral interconnects:", bold=True)
    add_table_data(
        doc, bio_p,
        headers=["Signal Name", "ESP32 Pin", "Direction", "Functional Description", "Wokwi Wire Color"],
        rows_data=c34.TABLE_3_1_DATA,
        col_widths=[1.2, 1.0, 1.0, 2.5, 1.3]
    )
    add_figure(bio_p, IMG_SCHEMATIC, "3.1", "Complete Circuit Schematic and Pin Interconnections of the ESP32 Drainage Telemetry Node in Wokwi Simulation", width_inches=5.2)

    add_h2(bio_p, "3.5 Firmware Architecture & Finite State Machine (FSM)")
    add_p(bio_p, c34.CH3_FSM_INTRO)
    add_p(bio_p, c34.CH3_FSM_LOGIC_INTRO, bold=True)
    for item in c34.CH3_FSM_LOGIC_ITEMS:
        add_bullet_item(bio_p, item)

    add_h2(bio_p, "3.6 Cloud Backend Microservices Architecture")
    add_p(bio_p, c34.CH3_BACKEND_INTRO)
    for task in c34.CH3_BACKEND_TASKS:
        add_bullet_item(bio_p, task)

    add_h2(bio_p, "3.7 Time-Series Database Schema & Hypertable Partitioning")
    add_p(bio_p, c34.CH3_TIMESCALEDB)
    add_p(bio_p, "Table 3.3 presents the relational and time-series database schema definitions:", bold=True)
    add_table_data(
        doc, bio_p,
        headers=["Table Name", "Primary / Foreign Keys", "Storage Engine & Column Definitions"],
        rows_data=c34.TABLE_3_3_DATA,
        col_widths=[1.3, 1.8, 3.9]
    )

    add_h2(bio_p, "3.8 Risk Assessment Engine & Mathematical Formulation")
    for para in c34.CH3_RISK_FORMULATION:
        add_p(bio_p, para)
    add_p(bio_p, c34.CH3_HYSTERESIS_INTRO)
    for rule in c34.CH3_HYSTERESIS_RULES:
        add_bullet_item(bio_p, rule)

    add_h2(bio_p, "3.9 Dynamic Dijkstra Evacuation Routing Formulation")
    for para in c34.CH3_DIJKSTRA:
        add_p(bio_p, para)
    add_p(bio_p, "Table 3.4 outlines the dynamic road network graph edges and baseline distances:", bold=True)
    add_table_data(
        doc, bio_p,
        headers=["Drain Node ID", "Flashpoint Name", "Latitude", "Longitude", "Destination Relief Camp", "Path Distance (Normal vs Flooded)"],
        rows_data=c34.TABLE_3_4_DATA,
        col_widths=[0.9, 1.4, 0.8, 0.8, 1.6, 1.5]
    )

    # Chapter 4: Implementation
    add_page_break(bio_p)
    add_chapter_heading(bio_p, "CHAPTER 4", "IMPLEMENTATION")

    for title, paras in c34.CH4_SECTIONS:
        add_h2(bio_p, title)
        for p in paras:
            add_p(bio_p, p)
        if "4.1" in title:
            add_figure(bio_p, IMG_BREADBOARD, "4.1", "ESP32 Hardware Breadboard Wiring and MicroPython REPL Initialization in Wokwi Simulation", width_inches=5.2)
        elif "4.6" in title:
            add_figure(bio_p, IMG_OPS_CRITICAL, "4.2", "Next.js Operator SCADA Operations Portal Command Center with Live Inundation Alert", width_inches=5.2)
        elif "4.7" in title:
            add_figure(bio_p, IMG_PUBLIC_MAP, "4.3", "Next.js Public Citizen Portal Displaying Safe Dijkstra Evacuation Route to Designated Relief Shelter", width_inches=5.2)

    add_p(bio_p, "Table 4.2 presents the multilingual emergency notification templates across Telugu, Hindi, and English:", bold=True)
    add_table_data(
        doc, bio_p,
        headers=["Target Language", "Standardized Dynamic Citizen Notification Template"],
        rows_data=c34.TABLE_4_2_DATA,
        col_widths=[1.5, 5.5]
    )

    print("[5/6] Inserting Chapter 5, Chapter 6 & Chapter 7...")
    # Chapter 5: Project Management
    add_page_break(bio_p)
    add_chapter_heading(bio_p, "CHAPTER 5", "PROJECT MANAGEMENT")

    add_h2(bio_p, "5.1 Work Breakdown Structure (WBS)")
    add_p(bio_p, c567.CH5_WBS_INTRO)
    add_table_data(
        doc, bio_p,
        headers=["WBS Code", "Work Package Name", "Scope of Engineering Deliverables", "Assigned Lead"],
        rows_data=c567.TABLE_5_1_DATA,
        col_widths=[0.9, 1.8, 3.1, 1.2]
    )

    add_h2(bio_p, "5.2 Project Timeline & Milestones")
    add_p(bio_p, c567.CH5_TIMELINE_INTRO)
    add_table_data(
        doc, bio_p,
        headers=["Milestone Phase", "Target Timeline", "Engineering Accomplishments & Verification Deliverables"],
        rows_data=c567.TABLE_5_2_DATA,
        col_widths=[1.4, 1.2, 4.4]
    )

    add_h2(bio_p, "5.3 Cost Estimation, Bill of Materials (BOM) & Budgeting")
    add_p(bio_p, c567.CH5_BOM_INTRO)
    add_table_data(
        doc, bio_p,
        headers=["Component Description", "Technical Specifications", "Qty", "Unit Cost (INR)", "Subtotal (INR)"],
        rows_data=c567.TABLE_5_3_DATA,
        col_widths=[1.8, 2.3, 0.5, 1.2, 1.2]
    )

    add_h2(bio_p, "5.4 Risk Management, Failsafe Redundancy & FMEA")
    add_p(bio_p, c567.CH5_FMEA_INTRO)
    add_table_data(
        doc, bio_p,
        headers=["Potential Failure Mode", "Operational Effect", "S", "O", "D", "RPN", "Implemented Engineering Safeguard"],
        rows_data=c567.TABLE_5_4_DATA,
        col_widths=[1.4, 1.6, 0.3, 0.3, 0.3, 0.4, 2.7]
    )

    add_h2(bio_p, "5.5 Sustainability, Environmental & Community Impact Assessment")
    add_p(bio_p, c567.CH5_SUSTAINABILITY_INTRO)
    for item in c567.CH5_SUSTAINABILITY_ITEMS:
        add_bullet_item(bio_p, item)

    # Chapter 6: Results & Performance Evaluation
    add_page_break(bio_p)
    add_chapter_heading(bio_p, "CHAPTER 6", "RESULTS & PERFORMANCE EVALUATION")

    add_h2(bio_p, "6.1 Telemetry Sensor Calibration & Accuracy Evaluation")
    add_p(bio_p, c567.CH6_CALIBRATION_INTRO)
    add_table_data(
        doc, bio_p,
        headers=["Mount Ht", "True Water Depth", "Sensor Distance", "Computed Depth", "Absolute Error", "Relative Error %"],
        rows_data=c567.TABLE_6_1_DATA,
        col_widths=[1.0, 1.3, 1.2, 1.2, 1.1, 1.2]
    )
    add_figure(bio_p, IMG_SERIAL_LOG, "6.1", "High-Frequency Ultrasonic Distance and Depth Telemetry Serial Log during Drainage Inundation", width_inches=5.2)
    add_figure(bio_p, IMG_SLIDER_CALIB, "6.2", "Wokwi Distance Slider Calibration at 400cm with Green LED Active and Gate at 0° (Normal State)", width_inches=5.2)

    add_h2(bio_p, "6.2 Telemetry Transmission Latency & Packet Delivery Ratio")
    add_p(bio_p, c567.CH6_LATENCY_INTRO)
    add_table_data(
        doc, bio_p,
        headers=["Network Interface", "Test Cycles", "Mean Latency", "Min Latency", "Max Latency", "Packet Delivery Ratio"],
        rows_data=c567.TABLE_6_2_DATA,
        col_widths=[1.8, 0.8, 1.1, 1.1, 1.1, 1.1]
    )

    add_h2(bio_p, "6.3 Edge Failsafe Actuation Response Time & Servo Horn Performance")
    add_p(bio_p, c567.CH6_ACTUATION_INTRO)
    add_table_data(
        doc, bio_p,
        headers=["Operational Mode", "Mean Latency", "Min Latency", "Max Latency", "Actuation Success Rate", "Engineering Observations"],
        rows_data=c567.TABLE_6_3_DATA,
        col_widths=[1.6, 0.9, 0.8, 0.8, 1.2, 1.7]
    )
    add_figure(bio_p, IMG_OPS_CRITICAL, "6.3", "Operator Ops Command Center Showing Kapilatheertham Nallah in Critical State (174.8cm / 180cm, Gate 90° Closed)", width_inches=5.2)
    add_figure(bio_p, IMG_OPS_MODAL, "6.4", "Operator Dashboard Detailed Node Telemetry Modal and 6-Hour Water Level Trend Sparkline", width_inches=5.2)

    add_h2(bio_p, "6.4 Risk Engine Hysteresis & False Alarm Suppression Testing")
    add_p(bio_p, c567.CH6_HYSTERESIS_EVAL)

    add_h2(bio_p, "6.5 Dynamic Dijkstra Evacuation Routing Validation")
    add_p(bio_p, c567.CH6_DIJKSTRA_EVAL)
    add_table_data(
        doc, bio_p,
        headers=["Origin Ward / Node", "Flood State", "Destination Relief Camp", "Distance", "Est Time", "Routing Optimization Strategy"],
        rows_data=c567.TABLE_6_4_DATA,
        col_widths=[1.4, 1.2, 1.6, 0.7, 0.7, 1.4]
    )
    add_figure(bio_p, IMG_STORM_OPS, "6.5", "Multi-Drain SCADA Overview During Simulated Flash Flood Storm Scenario", width_inches=5.2)

    add_h2(bio_p, "6.6 Multilingual Notification Dispatch Latency & Provider Evaluation")
    add_p(bio_p, c567.CH6_ALERT_EVAL)

    add_h2(bio_p, "6.7 End-to-End Automated Monorepo Verification (28/28 Pytest Suite)")
    add_p(bio_p, c567.CH6_VERIFICATION_INTRO)
    add_table_data(
        doc, bio_p,
        headers=["Test Name", "Test File Location", "Result", "Verification Scope & Assertion Criteria"],
        rows_data=c567.TABLE_6_5_DATA,
        col_widths=[1.8, 1.6, 0.8, 2.8]
    )

    # Chapter 7: Conclusions & Future Work
    add_page_break(bio_p)
    add_chapter_heading(bio_p, "CHAPTER 7", "CONCLUSIONS AND FUTURE WORK")

    add_h2(bio_p, "7.1 Conclusions")
    add_p(bio_p, c567.CH7_CONCLUSIONS_INTRO)
    add_p(bio_p, c567.CH7_ACHIEVEMENTS_INTRO, bold=True)
    for item in c567.CH7_ACHIEVEMENTS:
        add_bullet_item(bio_p, item)

    add_h2(bio_p, "7.2 Future Work")
    add_p(bio_p, c567.CH7_FUTURE_WORK_INTRO)
    for item in c567.CH7_FUTURE_WORK_ITEMS:
        add_bullet_item(bio_p, item)

    print("[6/6] Inserting References, Appendix Source Code & Research Paper...")
    # References
    add_page_break(bio_p)
    p_ref = bio_p.insert_paragraph_before()
    format_paragraph(p_ref, align=WD_ALIGN_PARAGRAPH.CENTER, line_spacing=1.5, space_before=16, space_after=14)
    r_ref = p_ref.add_run("REFERENCES")
    set_run_font(r_ref, font_name="Times New Roman", size_pt=14, bold=True)

    for ref in appx.REFERENCES:
        add_p(bio_p, ref, space_before=1, space_after=3)

    # Appendix: Source Code with Consolas 9.5pt in light grey shaded boxes with xml:space preserve
    add_page_break(bio_p)
    add_chapter_heading(bio_p, "APPENDIX", "SAMPLE PROGRAM CODE")

    # A.1 main.py
    add_h2(bio_p, "A.1 ESP32 MicroPython Firmware (firmware/main.py)")
    add_p(bio_p, "The complete production MicroPython firmware executed on the ESP32 in Wokwi and virtual environments. Formatted with strict 4-space indentation:")
    add_code_box(doc, bio_p, "firmware/main.py")

    # A.2 sketch.ino
    add_h2(bio_p, "A.2 ESP32 C++ Arduino Framework Firmware (firmware/sketch.ino)")
    add_p(bio_p, "The compiled C++ Arduino firmware designed for bare-metal flashing to physical ESP32 boards. Formatted with standard C++ indentation:")
    add_code_box(doc, bio_p, "firmware/sketch.ino")

    # A.3 risk.py
    add_h2(bio_p, "A.3 Hydrological Risk Assessment Engine (backend/app/risk.py)")
    add_p(bio_p, "The core mathematical risk engine executing on the cloud backend with 4-space Python indentation:")
    add_code_box(doc, bio_p, "backend/app/risk.py")

    # A.4 evacuation.py
    add_h2(bio_p, "A.4 Dynamic Dijkstra Evacuation Routing Service (backend/app/evacuation.py)")
    add_p(bio_p, "The dynamic graph routing engine computing obstacle-avoiding evacuation paths with 4-space Python indentation:")
    add_code_box(doc, bio_p, "backend/app/evacuation.py")

    # A.5 alerts.py
    add_h2(bio_p, "A.5 Multilingual Citizen Notification Gateway (backend/app/alerts.py)")
    add_p(bio_p, "The multilingual emergency dispatch service supporting Telugu, Hindi, and English with 4-space Python indentation:")
    add_code_box(doc, bio_p, "backend/app/alerts.py")

    # A.6 init.sql
    add_h2(bio_p, "A.6 Database Initialization & Hypertable Seed Script (db/init.sql)")
    add_p(bio_p, "The TimescaleDB schema initialization and baseline hydrological seed script with SQL block indentation:")
    add_code_box(doc, bio_p, "db/init.sql")

    # Research Paper
    add_page_break(bio_p)
    p_rp = bio_p.insert_paragraph_before()
    format_paragraph(p_rp, align=WD_ALIGN_PARAGRAPH.CENTER, line_spacing=1.5, space_before=16, space_after=14)
    r_rp = p_rp.add_run("RESEARCH PAPERS PUBLISHED")
    set_run_font(r_rp, font_name="Times New Roman", size_pt=14, bold=True)

    for item in appx.RESEARCH_PAPER_TEXT:
        add_p(bio_p, item)

    add_page_break(bio_p)

    # 12. BIO-DATA: Format 4 comprehensive, structured tables for all 4 project members
    # Clean up the original 2 placeholder tables at the end
    orig_t_count = len(doc.tables)
    tbl_bio_personal = doc.tables[-2]
    tbl_bio_contact = doc.tables[-1]

    # Populate Student 1 in the existing tables
    s1 = fm.STUDENT_BIOS[0]
    tbl_bio_personal.rows[0].cells[0].text = "NAME"
    tbl_bio_personal.rows[0].cells[1].text = f": {s1['name']} ({s1['roll']})"
    tbl_bio_personal.rows[1].cells[0].text = "FATHER NAME"
    tbl_bio_personal.rows[1].cells[1].text = f": {s1['father']}"
    tbl_bio_personal.rows[2].cells[0].text = "DATE OF BIRTH"
    tbl_bio_personal.rows[2].cells[1].text = f": {s1['dob']}"
    tbl_bio_personal.rows[3].cells[0].text = "NATIONALITY"
    tbl_bio_personal.rows[3].cells[1].text = f": {s1['nationality']}"
    style_table_borders(tbl_bio_personal, border_color="CCCCCC", sz="4")

    tbl_bio_contact.rows[0].cells[0].text = "Contact No."
    tbl_bio_contact.rows[0].cells[1].text = f": {s1['phone']}"
    tbl_bio_contact.rows[1].cells[0].text = "Email"
    tbl_bio_contact.rows[1].cells[1].text = f": {s1['email']}"
    tbl_bio_contact.rows[2].cells[0].text = "Contact Address"
    tbl_bio_contact.rows[2].cells[1].text = f": {s1['address']}"
    tbl_bio_contact.rows[3].cells[0].text = "Linkedin Id"
    tbl_bio_contact.rows[3].cells[1].text = f": {s1['linkedin']}"
    style_table_borders(tbl_bio_contact, border_color="CCCCCC", sz="4")

    # Add Bio-Data for Students 2, 3, and 4
    for s in fm.STUDENT_BIOS[1:]:
        p_head = doc.add_paragraph()
        format_paragraph(p_head, align=WD_ALIGN_PARAGRAPH.CENTER, line_spacing=1.5, space_before=16, space_after=8)
        r_head = p_head.add_run(f"BIO-DATA: {s['name'].upper()}")
        set_run_font(r_head, font_name="Times New Roman", size_pt=13, bold=True)

        t_p = doc.add_table(rows=4, cols=2)
        t_p.alignment = WD_TABLE_ALIGNMENT.CENTER
        t_p.rows[0].cells[0].text = "NAME"
        t_p.rows[0].cells[1].text = f": {s['name']} ({s['roll']})"
        t_p.rows[1].cells[0].text = "FATHER NAME"
        t_p.rows[1].cells[1].text = f": {s['father']}"
        t_p.rows[2].cells[0].text = "DATE OF BIRTH"
        t_p.rows[2].cells[1].text = f": {s['dob']}"
        t_p.rows[3].cells[0].text = "NATIONALITY"
        t_p.rows[3].cells[1].text = f": {s['nationality']}"
        style_table_borders(t_p, border_color="CCCCCC", sz="4")
        for row in t_p.rows:
            for c in row.cells:
                for p in c.paragraphs:
                    p.paragraph_format.line_spacing = 1.15
                    for r in p.runs:
                        set_run_font(r, font_name="Times New Roman", size_pt=10)

        p_con = doc.add_paragraph()
        format_paragraph(p_con, align=WD_ALIGN_PARAGRAPH.LEFT, line_spacing=1.5, space_before=10, space_after=4)
        r_con = p_con.add_run("CONTACT DETAILS")
        set_run_font(r_con, font_name="Times New Roman", size_pt=11, bold=True)

        t_c = doc.add_table(rows=4, cols=2)
        t_c.alignment = WD_TABLE_ALIGNMENT.CENTER
        t_c.rows[0].cells[0].text = "Contact No."
        t_c.rows[0].cells[1].text = f": {s['phone']}"
        t_c.rows[1].cells[0].text = "Email"
        t_c.rows[1].cells[1].text = f": {s['email']}"
        t_c.rows[2].cells[0].text = "Contact Address"
        t_c.rows[2].cells[1].text = f": {s['address']}"
        t_c.rows[3].cells[0].text = "Linkedin Id"
        t_c.rows[3].cells[1].text = f": {s['linkedin']}"
        style_table_borders(t_c, border_color="CCCCCC", sz="4")
        for row in t_c.rows:
            for c in row.cells:
                for p in c.paragraphs:
                    p.paragraph_format.line_spacing = 1.15
                    for r in p.runs:
                        set_run_font(r, font_name="Times New Roman", size_pt=10)

        # Page break after each student bio except the last
        if s != fm.STUDENT_BIOS[-1]:
            doc.add_page_break()

    print(f"Saving compiled Word document to {OUT_WORKSPACE_DOCX}...")
    doc.save(OUT_WORKSPACE_DOCX)
    print(f"Saving backup copy to {OUT_ARTIFACT_DOCX}...")
    doc.save(OUT_ARTIFACT_DOCX)
    print("[SUCCESS] Refactored Word document generated successfully!")


if __name__ == "__main__":
    main()
