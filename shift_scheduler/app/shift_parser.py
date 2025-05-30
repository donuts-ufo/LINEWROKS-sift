"""
"5/12 10:00-18:00" 等の行をパースして辞書を返す
"""
import datetime as dt
import re
from typing import Iterator

LINE_RE = re.compile(
    r"(?P<month>\d{1,2})[/-](?P<day>\d{1,2})\s+"
    r"(?P<start>\d{1,2}:\d{2})\s*-\s*(?P<end>\d{1,2}:\d{2})"
)

def parse_shift_lines(text: str, staff_name: str) -> Iterator[dict]:
    today = dt.date.today()
    default_year = today.year
    for line in text.splitlines():
        m = LINE_RE.search(line)
        if not m:
            continue
        month = int(m["month"])
        day = int(m["day"])
        start = dt.datetime.strptime(m["start"], "%H:%M").time()
        end = dt.datetime.strptime(m["end"], "%H:%M").time()
        # 年跨ぎ対応
        if month == 12 and today.month == 1:
            default_year -= 1
        work_date = dt.date(default_year, month, day)
        period = "前半" if 1 <= work_date.day <= 15 else "後半"
        yield {
            "staff_name": staff_name,
            "work_date": work_date,
            "start_time": start,
            "end_time": end,
            "period_tag": period,
        }
