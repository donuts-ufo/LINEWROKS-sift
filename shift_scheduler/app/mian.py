import os, datetime as dt, asyncio
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .models import init_db, SessionLocal
from .shift_parser import parse_shift_lines
from .lineworks import verify_signature, get_user_profile
from .excel_writer import build_excel
from .pdf_exporter import excel_to_pdf

load_dotenv()
app = FastAPI()
init_db()

PDF_DIR = Path(__file__).resolve().parent.parent / "generated"
PDF_DIR.mkdir(exist_ok=True)

# -- Webhook -----------------------------------------------------------
@app.post("/callback")
async def callback(req: Request):
    body = await req.body()
    if not verify_signature(body, req.headers.get("X-LINEWORKS-Signature")):
        raise HTTPException(400, "Signature mismatch")

    events = (await req.json()).get("events", [])
    db = SessionLocal()

    for ev in events:
        if ev.get("type") != "message" or ev["message"]["type"] != "text":
            continue
        uid = ev["source"]["userId"]
        profile = await get_user_profile(uid)
        name = profile["displayName"]
        for rec in parse_shift_lines(ev["message"]["text"], name):
            db.merge(rec)  # SQLAlchemy の dict merge (2.0 以降)
    db.commit()
    return {"ok": True}

# -- Scheduler ---------------------------------------------------------
sched = AsyncIOScheduler(timezone="Asia/Tokyo")

def last_day(year: int, month: int) -> int:
    return (dt.date(year + int(month == 12), month % 12 + 1, 1) -
            dt.timedelta(days=1)).day

def build_and_save(year: int, month: int, start: int, end: int):
    first = dt.date(year, month, start)
    last = dt.date(year, month, end)
    xlsx = PDF_DIR / f"shift_{year}{month:02d}_{start:02d}-{end:02d}.xlsx"
    pdf_path = excel_to_pdf(build_excel(first, last, xlsx))
    # ここで LINE WORKS Bot からファイル送信しても良い
    print("PDF exported:", pdf_path)

@sched.scheduled_job("cron", day="20", hour="0")
def first_half_job():
    nxt = dt.date.today() + dt.timedelta(days=11)  # 翌月
    build_and_save(nxt.year, nxt.month, 1, 15)

@sched.scheduled_job("cron", day="5", hour="0")
def second_half_job():
    today = dt.date.today()
    build_and_save(today.year, today.month, 16, last_day(today.year, today.month))

@app.on_event("startup")
async def startup_event():
    sched.start()
    print("Scheduler started")

