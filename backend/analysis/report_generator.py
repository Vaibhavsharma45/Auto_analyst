"""
backend/analysis/report_generator.py
Professional PDF Report Generator using ReportLab + FPDF2
"""

import pandas as pd
import numpy as np
from datetime import datetime
import io
import os
import base64

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                     TableStyle, Image, HRFlowable, PageBreak)
    from reportlab.platypus import KeepTogether
    from reportlab.graphics.shapes import Drawing, Rect
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class ReportGenerator:
    def __init__(self, df: pd.DataFrame, analysis: dict, charts: dict, filename: str = "dataset"):
        self.df = df
        self.analysis = analysis
        self.charts = charts
        self.filename = filename
        self.generated_at = datetime.now().strftime("%B %d, %Y at %I:%M %p")

        # Color palette
        self.DARK = colors.HexColor("#0d1117")
        self.ACCENT = colors.HexColor("#58a6ff")
        self.GREEN = colors.HexColor("#3fb950")
        self.ORANGE = colors.HexColor("#d29922")
        self.RED = colors.HexColor("#f85149")
        self.LIGHT = colors.HexColor("#c9d1d9")
        self.MUTED = colors.HexColor("#8b949e")
        self.CARD = colors.HexColor("#161b22")
        self.BORDER = colors.HexColor("#30363d")

    def generate_pdf(self, output_path: str) -> str:
        if not REPORTLAB_AVAILABLE:
            return self._generate_fallback_txt(output_path)

        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        styles = getSampleStyleSheet()
        story = []

        # Custom styles
        title_style = ParagraphStyle("Title", fontName="Helvetica-Bold", fontSize=26,
                                      textColor=self.ACCENT, spaceAfter=6, alignment=TA_CENTER)
        subtitle_style = ParagraphStyle("Subtitle", fontName="Helvetica", fontSize=11,
                                         textColor=self.MUTED, spaceAfter=4, alignment=TA_CENTER)
        h1_style = ParagraphStyle("H1", fontName="Helvetica-Bold", fontSize=16,
                                   textColor=self.ACCENT, spaceBefore=20, spaceAfter=8)
        h2_style = ParagraphStyle("H2", fontName="Helvetica-Bold", fontSize=13,
                                   textColor=self.LIGHT, spaceBefore=14, spaceAfter=6)
        body_style = ParagraphStyle("Body", fontName="Helvetica", fontSize=9,
                                     textColor=self.LIGHT, spaceAfter=4, leading=14)
        code_style = ParagraphStyle("Code", fontName="Courier", fontSize=8,
                                     textColor=self.GREEN, spaceAfter=2, leading=12)
        warn_style = ParagraphStyle("Warn", fontName="Helvetica", fontSize=9,
                                     textColor=self.ORANGE, spaceAfter=3)
        error_style = ParagraphStyle("Error", fontName="Helvetica", fontSize=9,
                                      textColor=self.RED, spaceAfter=3)

        # ── COVER PAGE ──────────────────────────────
        story.append(Spacer(1, 2 * cm))
        story.append(Paragraph("⚡ DataMind Pro", title_style))
        story.append(Paragraph("Automated Data Analysis Report", subtitle_style))
        story.append(Spacer(1, 0.3 * cm))
        story.append(HRFlowable(width="100%", thickness=1, color=self.ACCENT))
        story.append(Spacer(1, 0.5 * cm))

        overview = self.analysis.get("overview", {})
        shape = overview.get("shape", {})

        meta_data = [
            ["Dataset", self.filename],
            ["Generated", self.generated_at],
            ["Total Rows", f"{shape.get('rows', 'N/A'):,}"],
            ["Total Columns", str(shape.get('columns', 'N/A'))],
            ["Data Quality Score", f"{self.analysis.get('quality_report', {}).get('quality_score', 'N/A')}%"],
            ["Memory Usage", f"{overview.get('memory_usage_mb', 0):.2f} MB"],
        ]
        meta_table = Table(meta_data, colWidths=[4 * cm, 10 * cm])
        meta_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), self.CARD),
            ("TEXTCOLOR", (0, 0), (0, -1), self.ACCENT),
            ("TEXTCOLOR", (1, 0), (1, -1), self.LIGHT),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [self.CARD, self.DARK]),
            ("LINEBELOW", (0, 0), (-1, -1), 0.3, self.BORDER),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ]))
        story.append(meta_table)
        story.append(PageBreak())

        # ── SECTION 1: OVERVIEW ─────────────────────
        story.append(Paragraph("1. Dataset Overview", h1_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=self.BORDER))
        story.append(Spacer(1, 0.3 * cm))

        col_types = overview.get("column_types", {})
        stats_data = [
            ["Metric", "Value"],
            ["Rows", f"{shape.get('rows', 0):,}"],
            ["Columns", str(shape.get("columns", 0))],
            ["Numeric Columns", str(len(col_types.get("numeric", [])))],
            ["Categorical Columns", str(len(col_types.get("categorical", [])))],
            ["DateTime Columns", str(len(col_types.get("datetime", [])))],
            ["Missing Cells", f"{overview.get('missing', {}).get('total_missing_cells', 0):,} ({overview.get('missing', {}).get('missing_percentage', 0):.1f}%)"],
            ["Duplicate Rows", f"{overview.get('duplicates', {}).get('duplicate_rows', 0):,}"],
            ["Data Completeness", f"{overview.get('data_completeness_pct', 0):.1f}%"],
        ]
        self._add_table(story, stats_data)

        # Column types list
        if col_types.get("numeric"):
            story.append(Spacer(1, 0.3 * cm))
            story.append(Paragraph("Numeric Columns:", h2_style))
            story.append(Paragraph(", ".join(col_types["numeric"]), code_style))
        if col_types.get("categorical"):
            story.append(Paragraph("Categorical Columns:", h2_style))
            story.append(Paragraph(", ".join(col_types["categorical"]), code_style))

        # ── SECTION 2: NUMERIC STATS ─────────────────
        story.append(PageBreak())
        story.append(Paragraph("2. Numeric Column Statistics", h1_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=self.BORDER))
        story.append(Spacer(1, 0.3 * cm))

        num_stats = self.analysis.get("numeric_stats", {})
        for col, stat in num_stats.items():
            story.append(Paragraph(f"📊 {col}", h2_style))
            stat_rows = [
                ["Statistic", "Value", "Statistic", "Value"],
                ["Count", f"{stat.get('count', 0):,}", "Missing", f"{stat.get('missing', 0)} ({stat.get('missing_pct', 0):.1f}%)"],
                ["Mean", str(stat.get('mean', '')), "Std Dev", str(stat.get('std', ''))],
                ["Median", str(stat.get('median', '')), "Variance", str(stat.get('variance', ''))],
                ["Min", str(stat.get('min', '')), "Max", str(stat.get('max', ''))],
                ["Q1 (25%)", str(stat.get('q1', '')), "Q3 (75%)", str(stat.get('q3', ''))],
                ["IQR", str(stat.get('iqr', '')), "Range", str(stat.get('range', ''))],
                ["Skewness", str(stat.get('skewness', '')), "Kurtosis", str(stat.get('kurtosis', ''))],
                ["Outliers", f"{stat.get('outliers', {}).get('count', 0)} ({stat.get('outliers', {}).get('percentage', 0):.1f}%)",
                 "Is Normal?", "Yes ✓" if stat.get('normality', {}).get('is_normal') else "No ✗"],
            ]
            table = Table(stat_rows, colWidths=[4 * cm, 4 * cm, 4 * cm, 4 * cm])
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), self.CARD),
                ("TEXTCOLOR", (0, 0), (-1, 0), self.ACCENT),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
                ("TEXTCOLOR", (0, 1), (0, -1), self.MUTED),
                ("TEXTCOLOR", (2, 1), (2, -1), self.MUTED),
                ("TEXTCOLOR", (1, 1), (1, -1), self.LIGHT),
                ("TEXTCOLOR", (3, 1), (3, -1), self.LIGHT),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [self.DARK, self.CARD]),
                ("LINEBELOW", (0, 0), (-1, -1), 0.3, self.BORDER),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ]))
            story.append(table)
            story.append(Spacer(1, 0.4 * cm))

        # ── SECTION 3: CATEGORICAL STATS ─────────────
        cat_stats = self.analysis.get("categorical_stats", {})
        if cat_stats:
            story.append(PageBreak())
            story.append(Paragraph("3. Categorical Column Statistics", h1_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=self.BORDER))

            for col, stat in cat_stats.items():
                story.append(Paragraph(f"🏷 {col}", h2_style))
                top_vals = list(stat.get("value_counts", {}).items())[:8]
                rows = [["Value", "Count", "Percentage"]]
                for val, cnt in top_vals:
                    pct = stat.get("value_percentages", {}).get(val, 0)
                    rows.append([str(val), str(cnt), f"{pct:.1f}%"])

                t = Table(rows, colWidths=[8 * cm, 3 * cm, 3 * cm])
                t.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), self.CARD),
                    ("TEXTCOLOR", (0, 0), (-1, 0), self.ACCENT),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("TEXTCOLOR", (0, 1), (-1, -1), self.LIGHT),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [self.DARK, self.CARD]),
                    ("LINEBELOW", (0, 0), (-1, -1), 0.3, self.BORDER),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                ]))
                story.append(t)
                info_text = (f"Unique values: {stat.get('unique_values', 0)} | "
                             f"Missing: {stat.get('missing_pct', 0):.1f}% | "
                             f"Entropy: {stat.get('entropy', 0):.3f}")
                story.append(Paragraph(info_text, ParagraphStyle("info", fontName="Courier",
                                        fontSize=8, textColor=self.MUTED, spaceBefore=4)))
                story.append(Spacer(1, 0.3 * cm))

        # ── SECTION 4: CORRELATIONS ───────────────────
        corr = self.analysis.get("correlations", {})
        strong_pairs = corr.get("strong_pairs", [])
        if strong_pairs:
            story.append(PageBreak())
            story.append(Paragraph("4. Correlation Analysis", h1_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=self.BORDER))
            story.append(Spacer(1, 0.3 * cm))
            story.append(Paragraph("Strong Correlations (|r| ≥ 0.5):", h2_style))

            rows = [["Column 1", "Column 2", "Pearson r", "Strength", "Direction"]]
            for pair in strong_pairs:
                rows.append([
                    pair["col1"], pair["col2"],
                    str(pair["pearson_r"]), pair["strength"], pair["direction"]
                ])
            self._add_table(story, rows)

        # ── SECTION 5: QUALITY REPORT ─────────────────
        quality = self.analysis.get("quality_report", {})
        story.append(PageBreak())
        story.append(Paragraph("5. Data Quality Report", h1_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=self.BORDER))
        story.append(Spacer(1, 0.3 * cm))

        score = quality.get("quality_score", 0)
        score_color = self.GREEN if score >= 80 else self.ORANGE if score >= 60 else self.RED
        score_style = ParagraphStyle("Score", fontName="Helvetica-Bold", fontSize=32,
                                      textColor=score_color, alignment=TA_CENTER, spaceAfter=10)
        story.append(Paragraph(f"Quality Score: {score}/100", score_style))

        # Issues
        for issue in quality.get("issues", []):
            sev = issue["severity"]
            style = error_style if sev == "critical" else warn_style if sev == "warning" else body_style
            icon = "🔴" if sev == "critical" else "⚠️" if sev == "warning" else "ℹ️"
            story.append(Paragraph(f"{icon} {issue['message']}", style))

        # Recommendations
        recs = quality.get("recommendations", [])
        if recs:
            story.append(Spacer(1, 0.3 * cm))
            story.append(Paragraph("Recommendations:", h2_style))
            for rec in recs:
                story.append(Paragraph(f"→ {rec}", body_style))

        # ── SECTION 6: CHARTS ────────────────────────
        if self.charts:
            story.append(PageBreak())
            story.append(Paragraph("6. Visual Analysis", h1_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=self.BORDER))

            static_chart_keys = ["distribution_dashboard", "boxplot_dashboard",
                                  "correlation_heatmap", "scatter_matrix", "qq_plots",
                                  "violin_plots", "missing_values_chart"]

            for key in static_chart_keys:
                if key not in self.charts:
                    continue
                val = self.charts[key]
                if isinstance(val, str) and val.startswith("data:image/png;base64,"):
                    try:
                        img_data = base64.b64decode(val.split(",")[1])
                        img_buf = io.BytesIO(img_data)
                        img = Image(img_buf, width=17 * cm, height=10 * cm, kind="proportional")
                        title = key.replace("_", " ").title()
                        story.append(Paragraph(title, h2_style))
                        story.append(img)
                        story.append(Spacer(1, 0.5 * cm))
                    except Exception:
                        pass

            # Categorical charts
            for cat_chart in self.charts.get("categorical_charts", []):
                val = cat_chart.get("image", "")
                if val.startswith("data:image/png;base64,"):
                    try:
                        img_data = base64.b64decode(val.split(",")[1])
                        img_buf = io.BytesIO(img_data)
                        img = Image(img_buf, width=17 * cm, height=8 * cm, kind="proportional")
                        story.append(Paragraph(f"Category: {cat_chart['column']}", h2_style))
                        story.append(img)
                        story.append(Spacer(1, 0.5 * cm))
                    except Exception:
                        pass

        # ── FOOTER ────────────────────────────────────
        story.append(PageBreak())
        story.append(Spacer(1, 5 * cm))
        story.append(HRFlowable(width="100%", thickness=1, color=self.ACCENT))
        story.append(Spacer(1, 0.5 * cm))
        footer_style = ParagraphStyle("Footer", fontName="Helvetica", fontSize=9,
                                       textColor=self.MUTED, alignment=TA_CENTER)
        story.append(Paragraph("Generated by DataMind Pro — AI-Powered Data Analysis Platform", footer_style))
        story.append(Paragraph(f"Report Date: {self.generated_at}", footer_style))

        doc.build(story)
        return output_path

    def _add_table(self, story, data):
        t = Table(data, repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), self.CARD),
            ("TEXTCOLOR", (0, 0), (-1, 0), self.ACCENT),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("TEXTCOLOR", (0, 1), (-1, -1), self.LIGHT),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [self.DARK, self.CARD]),
            ("LINEBELOW", (0, 0), (-1, -1), 0.3, self.BORDER),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.3 * cm))

    def _generate_fallback_txt(self, output_path: str) -> str:
        """Text fallback if ReportLab not available"""
        txt_path = output_path.replace(".pdf", ".txt")
        with open(txt_path, "w") as f:
            f.write("DataMind Pro — Analysis Report\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {self.generated_at}\n\n")
            overview = self.analysis.get("overview", {})
            shape = overview.get("shape", {})
            f.write(f"Rows: {shape.get('rows')}\nCols: {shape.get('columns')}\n\n")
            f.write("Numeric Stats:\n")
            for col, stat in self.analysis.get("numeric_stats", {}).items():
                f.write(f"  {col}: mean={stat.get('mean')}, std={stat.get('std')}, min={stat.get('min')}, max={stat.get('max')}\n")
        return txt_path

