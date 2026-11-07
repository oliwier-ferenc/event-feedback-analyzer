import re
import pandas as pd

def format_google_sheet_url(url):
    """Converts a standard Google Sheet URL to a CSV export link."""
    if not url:
        return ""
    if "pub?output=csv" in url:
        return url
    if "/edit" in url:
        base = url.split("/edit")[0]
        gid = re.search(r"[#&]gid=(\d+)", url)
        tab = f"&gid={gid.group(1)}" if gid else ""
        return f"{base}/export?format=csv{tab}"
    return url

def sanitize_survey_data(df):
    """Drop columns whose names suggest they contain personal information"""
    pii_pattern = re.compile(
    r"\b(name|e-?mail|phone|mobile|address|ip|network[\s_-]*id|student[\s_-]*(id|number)|username|handle)\b",
    re.IGNORECASE,
    )
    columns_to_drop = [
        col for col in df.columns
        if pii_pattern.search(str(col))
    ]

    return df.drop(columns=columns_to_drop, errors="ignore")


def fetch_survey_data(source):
    """Load survey responses, then remove identifiable columns."""
    if hasattr(source, "read"):
        if source.name.lower().endswith(".xlsx"):
            df = pd.read_excel(source)
        else:
            df = pd.read_csv(source)
    elif isinstance(source, str):
        target_url = format_google_sheet_url(source)
        if not target_url:
            raise ValueError("Invalid Google Sheet URL provided.")
        df = pd.read_csv(target_url)
    else:
        raise ValueError("Unsupported data source. Please provide a file or Google Sheet URL.")

    # Pass through privacy scrubber
    return sanitize_survey_data(df)