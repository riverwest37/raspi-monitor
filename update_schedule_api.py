#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pathlib import Path
from datetime import datetime, timedelta, UTC
import html

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

BASE_DIR = Path("/home/pi/monitoring")
CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"
OUT_HTML = BASE_DIR / "schedule.html"

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
MAX_EVENTS = 10
WEEKDAY_JP = ["月", "火", "水", "木", "金", "土", "日"]


def get_credentials():
    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_FILE, "w", encoding="utf-8") as token:
            token.write(creds.to_json())
        return creds

    print("=== Google 認証を開始します ===")
    os.environ["DISPLAY"] = ":0"
    os.environ["XAUTHORITY"] = "/home/pi/.Xauthority"

    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
    creds = flow.run_local_server(
        host="localhost",
        port=0,
        open_browser=True,
    )

    with open(TOKEN_FILE, "w", encoding="utf-8") as token:
        token.write(creds.to_json())

    print("認証完了")
    return creds


def get_events(service):
    now = datetime.now(UTC).isoformat()

    events_result = service.events().list(
        calendarId="primary",
        timeMin=now,
        maxResults=MAX_EVENTS,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    return events_result.get("items", [])


def parse_event_datetime(event):
    start = event["start"].get("dateTime")
    if start:
        return datetime.fromisoformat(start.replace("Z", "+00:00"))

    start_date = event["start"].get("date")
    if start_date:
        return datetime.fromisoformat(start_date)

    return None


def is_all_day(event):
    return "date" in event.get("start", {})


def format_event_line(event, today, tomorrow):
    summary = event.get("summary", "(無題)")
    dt = parse_event_datetime(event)
    all_day = is_all_day(event)

    if dt is None:
        return "#ffffff", f"----  {summary}"

    ev_date = dt.date()

    if ev_date == today:
        color = "#ffff66"
    elif ev_date == tomorrow:
        color = "#66ccff"
    else:
        color = "#ffffff"

    day_str = f"{ev_date:%m/%d}"
    weekday_str = WEEKDAY_JP[ev_date.weekday()]

    if all_day:
        time_str = "終日"
    else:
        time_str = dt.astimezone().strftime("%H:%M")

    line = f"{day_str}({weekday_str})  {time_str:<5}  {summary}"
    return color, line


def write_html(events):
    now_local = datetime.now()
    today = now_local.date()
    tomorrow = today + timedelta(days=1)

    header = now_local.strftime(f"%m/%d({WEEKDAY_JP[now_local.weekday()]}) %H:%M")
    lines_html = [f'    <div class="header">{html.escape(header)}</div>']

    if not events:
        lines_html.append('    <div class="line">予定なし</div>')
    else:
        for event in events:
            color, line = format_event_line(event, today, tomorrow)
            lines_html.append(
                f'    <div class="line" style="color:{color}">{html.escape(line)}</div>'
            )

    page = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="60">
<style>
html, body {{
  margin: 0;
  width: 100%;
  height: 100%;
  background: black;
  color: white;
  font-family: Arial, "Hiragino Sans", "Yu Gothic", sans-serif;
}}
.wrap {{
  width: 100%;
  height: 100%;
  box-sizing: border-box;
  padding: 12px 18px;
  display: flex;
  flex-direction: column;
}}
.header {{
  font-size: 32px;
  margin-bottom: 10px;
  color: #00ffcc;
  font-weight: bold;
}}
.line {{
  font-size: 23px;
  line-height: 1.35;
  font-weight: bold;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin: 3px 0;
}}
</style>
</head>
<body>
  <div class="wrap">
{chr(10).join(lines_html)}
  </div>
</body>
</html>
"""
    OUT_HTML.write_text(page, encoding="utf-8")


def main():
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)
    events = get_events(service)

    print("=== 今後の予定 ===")
    if not events:
        print("予定はありません")
    else:
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            summary = event.get("summary", "(無題)")
            print(f"{start}  {summary}")

    write_html(events)
    print(f"updated: {OUT_HTML}")


if __name__ == "__main__":
    main()
