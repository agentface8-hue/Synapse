"""
Synapse Email Monitor
=====================
Reads agentface8@gmail.com and takes actions based on email content.
- Monitors for API alerts, Render deployment notifications, user signups
- Can forward important alerts to Telegram via OpenClaw
- Runs on a schedule or one-shot

Requires: Gmail App Password (not regular password)
Setup: 
  1. Go to https://myaccount.google.com/apppasswords
  2. Create an app password for "Mail" 
  3. Set as environment variable: GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
"""

import imaplib
import email
from email.header import decode_header
import os
import sys
import json
import time
import requests
from datetime import datetime, timezone

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Config
GMAIL_USER = os.environ.get("GMAIL_USER", "agentface8@gmail.com")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
SYNAPSE_API = "https://synapse-api-khoz.onrender.com"
CHECK_INTERVAL = 300  # 5 minutes


# Keywords that trigger actions
ALERT_KEYWORDS = {
    "render": ["deploy failed", "build failed", "service down", "suspended"],
    "anthropic": ["billing", "rate limit", "api key", "payment"],
    "github": ["security alert", "dependabot", "vulnerability"],
    "google": ["billing", "quota exceeded", "api disabled"],
    "synapse": ["error", "crash", "down"],
}

class EmailMonitor:
    def __init__(self):
        self.mail = None
        self.last_seen_uid = 0

    def connect(self):
        """Connect to Gmail via IMAP."""
        if not GMAIL_APP_PASSWORD:
            print("ERROR: Set GMAIL_APP_PASSWORD environment variable")
            print("Get one at: https://myaccount.google.com/apppasswords")
            return False
        try:
            self.mail = imaplib.IMAP4_SSL("imap.gmail.com")
            self.mail.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            print(f"Connected to {GMAIL_USER}")
            return True
        except Exception as e:
            print(f"Login failed: {e}")
            return False

    def fetch_unread(self, limit=10):
        """Fetch unread emails from inbox."""
        self.mail.select("INBOX")
        status, messages = self.mail.search(None, "UNSEEN")
        if status != "OK":
            return []

        email_ids = messages[0].split()
        if not email_ids:
            return []

        # Get most recent N
        email_ids = email_ids[-limit:]
        results = []

        for eid in email_ids:
            status, msg_data = self.mail.fetch(eid, "(RFC822)")
            if status != "OK":
                continue
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject = ""
                    raw_subject = msg["Subject"]
                    if raw_subject:
                        decoded = decode_header(raw_subject)
                        subject = decoded[0][0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(decoded[0][1] or "utf-8", errors="replace")

                    sender = msg.get("From", "")
                    date = msg.get("Date", "")

                    # Get body
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode("utf-8", errors="replace")
                                break
                    else:
                        body = msg.get_payload(decode=True).decode("utf-8", errors="replace")

                    results.append({
                        "id": eid.decode(),
                        "from": sender,
                        "subject": subject,
                        "date": date,
                        "body": body[:500],  # First 500 chars
                    })
        return results

    def classify_email(self, email_data):
        """Classify email by urgency and type."""
        subject_lower = (email_data.get("subject", "") or "").lower()
        body_lower = (email_data.get("body", "") or "").lower()
        sender = (email_data.get("from", "") or "").lower()
        combined = f"{subject_lower} {body_lower}"

        for source, keywords in ALERT_KEYWORDS.items():
            if source in sender or source in subject_lower:
                for kw in keywords:
                    if kw in combined:
                        return {"type": "alert", "source": source, "keyword": kw, "priority": "high"}

        # General classification
        if any(w in combined for w in ["urgent", "critical", "emergency", "action required"]):
            return {"type": "urgent", "priority": "high"}
        if any(w in combined for w in ["invoice", "payment", "receipt", "billing"]):
            return {"type": "billing", "priority": "medium"}
        if any(w in combined for w in ["newsletter", "unsubscribe", "promotional"]):
            return {"type": "newsletter", "priority": "low"}

        return {"type": "general", "priority": "low"}

    def check_and_report(self):
        """Check inbox and report findings."""
        emails = self.fetch_unread(limit=20)
        if not emails:
            print(f"  [{datetime.now(timezone.utc).strftime('%H:%M')}] No new emails")
            return []

        print(f"\n  [{datetime.now(timezone.utc).strftime('%H:%M')}] {len(emails)} new email(s):")
        alerts = []

        for em in emails:
            classification = self.classify_email(em)
            priority = classification["priority"]
            icon = {"high": "!!", "medium": "!", "low": " "}[priority]
            print(f"    [{icon}] {em['subject'][:60]}")
            print(f"        From: {em['from'][:50]} | Type: {classification['type']}")

            if priority == "high":
                alerts.append({**em, "classification": classification})

        return alerts

    def run_once(self):
        """Run a single check."""
        if not self.connect():
            return
        print(f"\nEmail Monitor - {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
        alerts = self.check_and_report()
        if alerts:
            print(f"\n  ** {len(alerts)} HIGH PRIORITY alert(s) found! **")
            for a in alerts:
                print(f"  >> {a['subject']}")
        self.mail.logout()

    def run_loop(self):
        """Run continuously."""
        print(f"Email Monitor starting - checking every {CHECK_INTERVAL//60} min")
        while True:
            try:
                if self.connect():
                    alerts = self.check_and_report()
                    self.mail.logout()
            except Exception as e:
                print(f"  Error: {e}")
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Synapse Email Monitor")
    parser.add_argument("--loop", action="store_true", help="Run continuously")
    args = parser.parse_args()

    monitor = EmailMonitor()
    if args.loop:
        monitor.run_loop()
    else:
        monitor.run_once()
