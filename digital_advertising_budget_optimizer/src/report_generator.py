"""
Report Generation Module.
Generates comprehensive executive summaries, platform breakdowns,
benchmark audits, and budget recommendation reports.
Supports CSV, Markdown, and formatted PDF/HTML exports.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import pandas as pd
import config


class ReportGenerator:
    """
    Creates university and executive-grade analytical reports.
    """

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or config.REPORTS_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_executive_summary_text(
        self,
        overall_metrics: Dict[str, Any],
        platform_df: pd.DataFrame,
        recommendation: Dict[str, Any],
    ) -> str:
        """
        Creates a structured academic and executive markdown report.
        """
        timestamp = datetime.now().strftime("%B %d, %Y - %H:%M:%S")

        report = f"""# EXECUTIVE REPORT — DIGITAL ADVERTISING BUDGET OPTIMIZATION
**Big Data Analytics Decision Support System**
**Date Generated:** {timestamp}
**Target Budget:** Rs. {recommendation.get('total_budget', 1_000_000):,.2f} PKR
**Strategy:** {recommendation.get('strategy', 'Balanced Optimization')}

---

## 1. Executive Summary & Problem Context
Management faces the strategic question: **"Where should we spend the next Rs. 1,000,000 across Facebook, Instagram, Google, TikTok, and YouTube to maximize marketing ROI?"**

Historical campaign data demonstrates that capital allocation must balance immediate revenue yield (ROAS), cost per acquisition (CPA), conversion volume, and channel volatility rather than defaulting to arbitrary fixed splits.

---

## 2. Overall Portfolio Performance Scorecard
- **Total Historical Ad Spend:** Rs. {overall_metrics.get('total_spend', 0):,.2f}
- **Total Gross Revenue Generated:** Rs. {overall_metrics.get('total_revenue', 0):,.2f}
- **Net Marketing Contribution (Profit):** Rs. {overall_metrics.get('net_profit', 0):,.2f}
- **Portfolio-wide ROAS:** {overall_metrics.get('roas', 0):.2f}x
- **Total Impressions Delivered:** {overall_metrics.get('total_impressions', 0):,}
- **Total Clicks Captured:** {overall_metrics.get('total_clicks', 0):,} (CTR: {overall_metrics.get('ctr', 0):.2f}%)
- **Total Conversions / Orders:** {overall_metrics.get('total_conversions', 0):,} (CVR: {overall_metrics.get('cvr', 0):.2f}%)
- **Blended Cost Per Click (CPC):** Rs. {overall_metrics.get('cpc', 0):.2f}
- **Blended Cost Per Acquisition (CPA):** Rs. {overall_metrics.get('cpa', 0):.2f}

---

## 3. Platform Performance Comparison Table
| Platform | Total Spend (PKR) | Revenue (PKR) | ROAS | CTR (%) | CPC (PKR) | CPA (PKR) | CVR (%) |
|---|---|---|---|---|---|---|---|
"""
        for _, r in platform_df.iterrows():
            report += f"| {r['platform']} | Rs. {r['spend']:,.2f} | Rs. {r['revenue']:,.2f} | {r['roas']:.2f}x | {r['ctr']:.2f}% | Rs. {r['cpc']:.2f} | Rs. {r['cpa']:.2f} | {r['conversion_rate']:.2f}% |\n"

        report += f"""
---

## 4. Recommended Allocation for Next Rs. 1,000,000
| Platform | Allocation (%) | Recommended Amount (PKR) | Direction | Rationale |
|---|---|---|---|---|
"""
        for a in recommendation.get("allocations", []):
            report += f"| {a['platform']} | {a['allocated_percentage']:.1f}% | Rs. {a['allocated_amount']:,.2f} | {a['action']} | {a['rationale']} |\n"

        proj = recommendation.get("projections", {})
        report += f"""
---

## 5. Projected Marketing Outcomes (Mathematical Estimates)
- **Projected Impressions:** {proj.get('expected_impressions', 0):,}
- **Projected Clicks:** {proj.get('expected_clicks', 0):,}
- **Projected Conversions:** {proj.get('expected_conversions', 0):,}
- **Projected Gross Revenue:** Rs. {proj.get('expected_revenue', 0):,.2f}
- **Projected Net Contribution:** Rs. {proj.get('expected_net_profit', 0):,.2f}
- **Projected Blended ROAS:** {proj.get('expected_roas', 0):.2f}x

*> Note: {proj.get('disclaimer', '')}*

---
*Report automatically compiled by Digital Advertising Budget Optimizer System.*
"""
        return report

    def export_csv(self, df: pd.DataFrame, filename: str) -> Path:
        """Exports a DataFrame to the reports directory as a CSV."""
        path = self.output_dir / filename
        df.to_csv(path, index=False)
        return path

    def export_pdf(self, markdown_text: str, filename: str = "Executive_Report.pdf") -> Optional[Path]:
        """
        Attempts to generate a PDF report using ReportLab if installed.
        Falls back to saving markdown if ReportLab is unavailable.
        """
        path = self.output_dir / filename
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

            doc = SimpleDocTemplate(str(path), pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
            styles = getSampleStyleSheet()
            story = []

            for line in markdown_text.split("\n"):
                line_str = line.strip()
                if not line_str:
                    story.append(Spacer(1, 8))
                elif line_str.startswith("# "):
                    story.append(Paragraph(line_str[2:], styles["Heading1"]))
                elif line_str.startswith("## "):
                    story.append(Paragraph(line_str[3:], styles["Heading2"]))
                elif line_str.startswith("- "):
                    story.append(Paragraph(f"• {line_str[2:]}", styles["Normal"]))
                elif not line_str.startswith("|") and not line_str.startswith("---"):
                    story.append(Paragraph(line_str, styles["Normal"]))

            doc.build(story)
            return path
        except Exception:
            # Fallback: save as markdown file
            md_path = path.with_suffix(".md")
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(markdown_text)
            return md_path

