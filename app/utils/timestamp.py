from datetime import datetime
from zoneinfo import ZoneInfo

def format_timestamp(tz_str: str = "UTC", dt: datetime = None) -> str:
    try:
        tz = ZoneInfo(tz_str)
    except Exception:
        tz = ZoneInfo("UTC")

    dt = dt or datetime.now(tz)
    dt = dt.astimezone(tz)

    offset = dt.strftime('%z')  # e.g., +0530
    offset_str = f"UTC{offset[:3]}:{offset[3:]}"  # UTC+05:30
    formatted = dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-4]  # e.g., 2025-05-15 21:27:05.30
    return f"{formatted} {offset_str}"
