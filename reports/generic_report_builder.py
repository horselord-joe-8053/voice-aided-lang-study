import os
import re
import uuid
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from core.rag.generic_data_processor import DataSchema

BASE_DIR = Path(__file__).parent.parent.resolve()
STORAGE_REPORTS_DIR = BASE_DIR / "storage" / "reports"

class ReportConfig:
    """Configuration for report generation."""
    
    def __init__(
        self,
        title: str = "Data Report",
        date_columns: List[str] = None,
        score_columns: List[str] = None,
        filter_columns: List[str] = None,
        display_columns: List[str] = None,
        max_rows: int = 500
    ):
        self.title = title
        self.date_columns = date_columns or []
        self.score_columns = score_columns or []
        self.filter_columns = filter_columns or []
        self.display_columns = display_columns or []
        self.max_rows = max_rows

def ensure_reports_dir() -> Path:
    """Ensure reports directory exists."""
    STORAGE_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    return STORAGE_REPORTS_DIR

def _parse_relative_date_range(text: str) -> Optional[Tuple[pd.Timestamp, pd.Timestamp]]:
    """Parse relative date ranges from text."""
    t = text.lower()
    now = pd.Timestamp.now().normalize()
    
    if re.search(r"last\s+week", t):
        return now - pd.Timedelta(days=7), now
    if re.search(r"last\s+month", t):
        return now - pd.Timedelta(days=30), now
    
    m = re.search(r"(last|past)\s+(\d+)\s+(day|days|week|weeks|month|months)", t)
    if m:
        num = int(m.group(2))
        unit = m.group(3)
        days = num * (7 if unit.startswith("week") else 30 if unit.startswith("month") else 1)
        return now - pd.Timedelta(days=days), now
    
    return None

def _filter_df_from_question(df: pd.DataFrame, question: str, config: ReportConfig) -> pd.DataFrame:
    """Filter DataFrame based on question and configuration."""
    out = df.copy()
    
    # Date filtering
    date_range = _parse_relative_date_range(question)
    if date_range and config.date_columns:
        start, end = date_range
        for date_col in config.date_columns:
            if date_col in out.columns:
                out[date_col] = pd.to_datetime(out[date_col], errors='coerce')
                out = out[(out[date_col] >= start) & (out[date_col] <= end)]
                break  # Use first available date column
    
    # Column-specific filtering
    for filter_col in config.filter_columns:
        if filter_col in out.columns:
            # Generic pattern matching for the column
            pattern = rf"{filter_col.lower()}[^0-9a-zA-Z]*([0-9A-Za-z\-_]+)"
            match = re.search(pattern, question, flags=re.I)
            if match:
                value = match.group(1).strip()
                if value:
                    out = out[out[filter_col].astype(str).str.contains(value, case=False, na=False)]
    
    return out.head(config.max_rows)

def _summary_blocks(df: pd.DataFrame, config: ReportConfig) -> Tuple[int, float, str, str]:
    """Generate summary statistics."""
    total = len(df)
    
    # Calculate average score if score columns exist
    avg = 0.0
    if config.score_columns:
        for score_col in config.score_columns:
            if score_col in df.columns:
                avg = float(df[score_col].mean()) if total > 0 else 0.0
                break
    
    # Get date range if date columns exist
    earliest = "-"
    latest = "-"
    if config.date_columns:
        for date_col in config.date_columns:
            if date_col in df.columns and total > 0:
                earliest = str(df[date_col].min())
                latest = str(df[date_col].max())
                break
    
    return total, avg, earliest, latest

def _table_data(df: pd.DataFrame, config: ReportConfig, max_cols: int = 8) -> List[List[str]]:
    """Generate table data for report."""
    # Use display columns if specified, otherwise use all columns
    if config.display_columns:
        cols = [col for col in config.display_columns if col in df.columns][:max_cols]
    else:
        cols = list(df.columns)[:max_cols]
    
    rows = [cols]
    for _, r in df.iterrows():
        rows.append([str(r.get(c, "")) for c in cols])
    
    return rows

def generate_report_from_df(
    df: pd.DataFrame, 
    config: ReportConfig, 
    question: str
) -> Tuple[str, Dict[str, Any]]:
    """Generate PDF report from DataFrame."""
    ensure_reports_dir()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"report_{stamp}_{uuid.uuid4().hex[:6]}.pdf"
    fpath = STORAGE_REPORTS_DIR / fname

    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph(config.title, styles['Title']))
    story.append(Spacer(1, 8))
    
    # Question and timestamp
    story.append(Paragraph(f"Question: {question}", styles['Normal']))
    story.append(Paragraph(f"Generated at: {datetime.now().isoformat(timespec='seconds')}", styles['Normal']))
    story.append(Spacer(1, 12))

    # Summary statistics
    total, avg, earliest, latest = _summary_blocks(df, config)
    
    # Create summary text based on available data
    summary_parts = [f"Rows: {total}"]
    
    if config.score_columns and avg > 0:
        score_col = config.score_columns[0] if config.score_columns else "SCORE"
        summary_parts.append(f"Avg {score_col}: {avg:.2f}")
    
    if config.date_columns and earliest != "-":
        date_col = config.date_columns[0] if config.date_columns else "DATE"
        summary_parts.append(f"Date range: {earliest} → {latest}")
    
    summary = " | ".join(summary_parts)
    story.append(Paragraph(summary, styles['Heading4']))
    story.append(Spacer(1, 8))

    # Data table
    table_rows = _table_data(df, config)
    if table_rows:
        table = Table(table_rows, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
            ("TEXTCOLOR", (0,0), (-1,0), colors.black),
            ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
            ("FONTSIZE", (0,0), (-1,-1), 8),
            ("ALIGN", (0,0), (-1,-1), "LEFT"),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
        ]))
        story.append(table)

    # Generate PDF
    doc = SimpleDocTemplate(
        str(fpath), 
        pagesize=A4, 
        leftMargin=36, 
        rightMargin=36, 
        topMargin=36, 
        bottomMargin=36
    )
    doc.build(story)

    # Metadata
    meta = {
        "filename": fname,
        "path": str(fpath),
        "rows": total,
        "avg_score": avg,
        "earliest": earliest,
        "latest": latest,
    }
    
    return str(fpath), meta

def generate_report_from_question(
    question: str, 
    csv_path: str, 
    data_schema: DataSchema,
    report_config: ReportConfig
) -> Tuple[str, Dict[str, Any]]:
    """Generate report from question and CSV file."""
    # Load data
    df = pd.read_csv(csv_path)
    
    # Clean numeric columns
    for score_col in report_config.score_columns:
        if score_col in df.columns:
            df[score_col] = pd.to_numeric(df[score_col], errors='coerce').fillna(0.0)
    
    # Clean date columns
    for date_col in report_config.date_columns:
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    
    # Filter data based on question
    filtered = _filter_df_from_question(df, question, report_config)
    
    # Generate report
    return generate_report_from_df(filtered, report_config, question)

# Legacy function for backward compatibility
def generate_report_from_question_legacy(question: str, csv_path: str) -> Tuple[str, Dict[str, Any]]:
    """Legacy function for backward compatibility with legacy data formats."""
    # Create default configuration for legacy data
    data_schema = DataSchema(
        required_columns=['RO_NO', 'DEALER_CODE', 'SCORE', 'CREATE_DATE'],
        date_columns=['CREATE_DATE'],
        score_columns=['SCORE'],
        filter_columns=['DEALER_CODE', 'REPAIR_TYPE_NAME']
    )
    
    report_config = ReportConfig(
        title="Legacy Data Report",
        date_columns=['CREATE_DATE'],
        score_columns=['SCORE'],
        filter_columns=['DEALER_CODE', 'REPAIR_TYPE_NAME']
    )
    
    return generate_report_from_question(question, csv_path, data_schema, report_config)
