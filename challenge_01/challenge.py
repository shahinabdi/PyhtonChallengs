from pathlib import Path

def build_report_path(base_dir, user, year):
    filename = f"report_{user}_{year}.txt"
    full = Path(base_dir) / "reports" / filename
    full.parent.mkdir(parents=True, exist_ok=True)
    return full