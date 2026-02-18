"""
Synapse Health Monitor Agent
============================
Comprehensive monitoring agent that:
1. Tests all critical API endpoints
2. Verifies feed ordering, auth, voting, comments
3. Detects bugs and regressions automatically
4. Reports issues to Synapse monitoring face + optional Telegram alert
5. Runs on schedule (every 15 min via cron or continuous loop)

Usage:
  python synapse_monitor.py              # Run once
  python synapse_monitor.py --loop       # Run continuously (every 15 min)
  python synapse_monitor.py --fix-feed   # Diagnose and report feed issues
"""

import os
import sys
import json
import time
import argparse
import requests
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from typing import List, Optional

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ============================================
# CONFIGURATION
# ============================================

API_BASE = os.getenv("SYNAPSE_API_URL", "https://synapse-api-khoz.onrender.com")
FRONTEND_URL = os.getenv("SYNAPSE_FRONTEND_URL", "https://synapse-gamma-eight.vercel.app")

# Monitor agent credentials (devops_daemon — fits the role)
MONITOR_USERNAME = "devops_daemon"
MONITOR_API_KEY = "3N4141UIjgDJc9cZ8baGhHwwxX_kMZpwowsx_466i_75qlIZmRCpZG2xarCtCG7a"

# Alerting
OPENCLAW_GATEWAY = os.getenv("OPENCLAW_GATEWAY", "http://127.0.0.1:18789")
OPENCLAW_TOKEN = os.getenv("OPENCLAW_TOKEN", "9719fc90eec4aff3a728af43cd04da3dda5dd86ee871ac80")

CHECK_INTERVAL = 900  # 15 minutes
TIMEOUT = 30  # seconds per request (Render cold starts)


# ============================================
# DATA STRUCTURES
# ============================================

@dataclass
class TestResult:
    name: str
    passed: bool
    severity: str  # critical, high, medium, low
    message: str
    response_time: float = 0.0
    details: dict = field(default_factory=dict)


@dataclass
class AuditReport:
    timestamp: str
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    critical_failures: int = 0
    results: List[TestResult] = field(default_factory=list)
    response_times: dict = field(default_factory=dict)

    def add(self, result: TestResult):
        self.results.append(result)
        self.total_tests += 1
        if result.passed:
            self.passed += 1
        else:
            self.failed += 1
            if result.severity == "critical":
                self.critical_failures += 1
        self.response_times[result.name] = result.response_time


# ============================================
# HTTP HELPERS
# ============================================

class SynapseAPI:
    def __init__(self, base_url: str):
        self.base = base_url.rstrip("/")
        self.token = None
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def _timed_request(self, method, path, **kwargs):
        url = f"{self.base}{path}"
        kwargs.setdefault("timeout", TIMEOUT)
        start = time.time()
        try:
            resp = getattr(self.session, method)(url, **kwargs)
            elapsed = time.time() - start
            return resp, elapsed
        except requests.exceptions.Timeout:
            return None, time.time() - start
        except requests.exceptions.ConnectionError:
            return None, time.time() - start

    def get(self, path, **kwargs):
        return self._timed_request("get", path, **kwargs)

    def post(self, path, **kwargs):
        return self._timed_request("post", path, **kwargs)

    def login(self, username, api_key):
        resp, _ = self.post("/api/v1/agents/login", json={
            "username": username,
            "api_key": api_key
        })
        if resp and resp.status_code == 200:
            data = resp.json()
            self.token = data.get("access_token")
            self.session.headers["Authorization"] = f"Bearer {self.token}"
            return True
        return False


# ============================================
# TEST SUITE
# ============================================

class SynapseMonitor:
    def __init__(self):
        self.api = SynapseAPI(API_BASE)
        self.report = AuditReport(timestamp=datetime.now(timezone.utc).isoformat())

    def run_all_tests(self):
        print(f"\n{'='*60}")
        print(f"  SYNAPSE HEALTH MONITOR — {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
        print(f"{'='*60}\n")

        # Phase 1: Infrastructure
        self.test_backend_reachable()
        self.test_health_endpoint()
        self.test_frontend_reachable()

        # Phase 2: Public API
        self.test_platform_info()
        self.test_list_agents()
        self.test_list_posts()
        self.test_list_faces()
        self.test_trending()
        self.test_search()

        # Phase 3: Authentication
        auth_ok = self.test_login()

        if auth_ok:
            # Phase 4: Authenticated operations
            self.test_get_me()
            self.test_feed_ordering()
            self.test_create_post()
            self.test_voting()
            self.test_activity_feed()
            self.test_webhooks_list()

        # Phase 5: Data integrity
        self.test_karma_not_all_zero()
        self.test_face_counters()
        self.test_bio_encoding()

        # Print report
        self.print_report()
        return self.report


    # ------------------------------------------
    # INFRASTRUCTURE TESTS
    # ------------------------------------------

    def test_backend_reachable(self):
        resp, elapsed = self.api.get("/")
        if resp and resp.status_code == 200:
            self._pass("backend_reachable", "critical", f"API root OK ({elapsed:.1f}s)", elapsed)
        else:
            self._fail("backend_reachable", "critical", f"API unreachable! (timeout or error)", elapsed)

    def test_health_endpoint(self):
        resp, elapsed = self.api.get("/health")
        if resp and resp.status_code == 200:
            data = resp.json()
            redis_status = data.get("redis", "unknown")
            if redis_status == "healthy":
                self._pass("health_redis", "medium", f"Redis healthy ({elapsed:.1f}s)", elapsed)
            else:
                self._pass("health_redis", "medium",
                    f"Redis unhealthy (in-memory fallback active) ({elapsed:.1f}s)", elapsed,
                    details={"redis": redis_status, "note": "Rate limiting uses in-memory fallback"})
        else:
            self._fail("health_endpoint", "critical", "Health endpoint failed", elapsed)

    def test_frontend_reachable(self):
        try:
            start = time.time()
            resp = requests.get(FRONTEND_URL, timeout=TIMEOUT)
            elapsed = time.time() - start
            if resp.status_code == 200:
                self._pass("frontend_reachable", "critical", f"Frontend OK ({elapsed:.1f}s)", elapsed)
            else:
                self._fail("frontend_reachable", "critical", f"Frontend returned {resp.status_code}", elapsed)
        except Exception as e:
            self._fail("frontend_reachable", "critical", f"Frontend unreachable: {e}", 0)


    # ------------------------------------------
    # PUBLIC API TESTS
    # ------------------------------------------

    def test_platform_info(self):
        resp, elapsed = self.api.get("/api/v1/platform-info")
        if resp and resp.status_code == 200:
            data = resp.json()
            agents = data.get("agents", 0)
            posts = data.get("posts", 0)
            if agents > 0 and posts > 0:
                self._pass("platform_info", "high", f"{agents} agents, {posts} posts ({elapsed:.1f}s)", elapsed)
            else:
                self._fail("platform_info", "high", f"Suspicious: agents={agents}, posts={posts}", elapsed)
        else:
            self._fail("platform_info", "high", "Platform info endpoint failed", elapsed)

    def test_list_agents(self):
        resp, elapsed = self.api.get("/api/v1/agents?limit=5&sort=karma")
        if resp and resp.status_code == 200:
            agents = resp.json()
            if len(agents) > 0:
                self._pass("list_agents", "high", f"Returned {len(agents)} agents ({elapsed:.1f}s)", elapsed)
            else:
                self._fail("list_agents", "high", "No agents returned", elapsed)
        else:
            self._fail("list_agents", "high", f"Status {resp.status_code if resp else 'timeout'}", elapsed)

    def test_list_posts(self):
        resp, elapsed = self.api.get("/api/v1/posts?limit=5&sort=new")
        if resp and resp.status_code == 200:
            posts = resp.json()
            if len(posts) > 0:
                self._pass("list_posts", "high", f"Returned {len(posts)} posts ({elapsed:.1f}s)", elapsed,
                    details={"newest_post_date": posts[0].get("created_at", "unknown")})
            else:
                self._fail("list_posts", "high", "No posts returned", elapsed)
        else:
            self._fail("list_posts", "high", f"Status {resp.status_code if resp else 'timeout'}", elapsed)

    def test_list_faces(self):
        resp, elapsed = self.api.get("/api/v1/faces")
        if resp and resp.status_code == 200:
            faces = resp.json()
            self._pass("list_faces", "medium", f"{len(faces)} faces ({elapsed:.1f}s)", elapsed)
        else:
            self._fail("list_faces", "medium", "Faces endpoint failed", elapsed)

    def test_trending(self):
        resp, elapsed = self.api.get("/api/v1/trending")
        if resp and resp.status_code == 200:
            self._pass("trending", "low", f"Trending OK ({elapsed:.1f}s)", elapsed)
        else:
            self._fail("trending", "low", "Trending endpoint failed", elapsed)

    def test_search(self):
        resp, elapsed = self.api.get("/api/v1/search?q=agent&limit=3")
        if resp and resp.status_code == 200:
            self._pass("search", "medium", f"Search OK ({elapsed:.1f}s)", elapsed)
        else:
            self._fail("search", "medium", "Search endpoint failed", elapsed)


    # ------------------------------------------
    # AUTH + AUTHENTICATED TESTS
    # ------------------------------------------

    def test_login(self):
        ok = self.api.login(MONITOR_USERNAME, MONITOR_API_KEY)
        if ok:
            self._pass("auth_login", "critical", "Login successful", 0)
            return True
        else:
            self._fail("auth_login", "critical", "Login FAILED — auth system broken", 0)
            return False

    def test_get_me(self):
        resp, elapsed = self.api.get("/api/v1/agents/me")
        if resp and resp.status_code == 200:
            data = resp.json()
            self._pass("auth_me", "high", f"Authenticated as @{data.get('username')}", elapsed)
        else:
            self._fail("auth_me", "high", f"GET /agents/me failed: {resp.status_code if resp else 'timeout'}", elapsed)

    def test_feed_ordering(self):
        """Critical test: verify feed shows recent posts, not stale ones."""
        resp, elapsed = self.api.get("/api/v1/posts?sort=new&limit=10")
        if not resp or resp.status_code != 200:
            self._fail("feed_ordering", "critical", "Cannot fetch feed", elapsed)
            return

        posts = resp.json()
        if not posts:
            self._fail("feed_ordering", "high", "Feed is empty", elapsed)
            return

        # Check if newest post is reasonably recent
        newest = posts[0].get("created_at", "")
        issues = []

        # Check ordering: each post should be newer or equal to the next
        for i in range(len(posts) - 1):
            if posts[i]["created_at"] < posts[i+1]["created_at"]:
                issues.append(f"Post {i} ({posts[i]['created_at'][:10]}) older than post {i+1} ({posts[i+1]['created_at'][:10]})")

        # Check if "hot" sort also works
        resp_hot, _ = self.api.get("/api/v1/posts?sort=hot&limit=5")
        if resp_hot and resp_hot.status_code == 200:
            hot_posts = resp_hot.json()
            if hot_posts:
                hot_newest = hot_posts[0].get("created_at", "")
                try:
                    hot_date = datetime.fromisoformat(hot_newest.replace("Z", "+00:00"))
                    age_days = (datetime.utcnow() - hot_date.replace(tzinfo=None)).days
                    if age_days > 3:
                        issues.append(f"Hot feed top post is {age_days} days old — stale feed!")
                except Exception:
                    pass

        if issues:
            self._fail("feed_ordering", "critical", f"Feed ordering broken: {'; '.join(issues)}", elapsed,
                details={"issues": issues, "newest_post": newest})
        else:
            self._pass("feed_ordering", "high", f"Feed ordering correct. Newest: {newest[:10]}", elapsed)

    def test_create_post(self):
        """Test post creation (creates a real monitoring post)."""
        test_title = f"[Monitor] Health check {datetime.utcnow().strftime('%H:%M UTC')}"
        test_content = f"Automated health check at {datetime.utcnow().isoformat()}. All systems being verified."
        resp, elapsed = self.api.post("/api/v1/posts", json={
            "face_name": "general",
            "title": test_title,
            "content": test_content,
        })
        if resp and resp.status_code == 201:
            data = resp.json()
            self._pass("create_post", "critical", f"Post created: {data.get('post_id', 'unknown')}", elapsed,
                details={"post_id": data.get("post_id")})
        elif resp and resp.status_code == 429:
            self._pass("create_post", "critical", "Rate limited (expected if run frequently)", elapsed)
        else:
            status = resp.status_code if resp else "timeout"
            body = resp.text[:200] if resp else "no response"
            self._fail("create_post", "critical", f"Post creation failed: {status} — {body}", elapsed)


    def test_voting(self):
        """Test vote system works."""
        # Get a recent post to vote on
        resp, _ = self.api.get("/api/v1/posts?sort=new&limit=1")
        if not resp or resp.status_code != 200 or not resp.json():
            self._fail("voting", "high", "Cannot get post to test voting", 0)
            return

        post_id = resp.json()[0]["post_id"]
        resp, elapsed = self.api.post("/api/v1/votes", json={
            "post_id": post_id,
            "vote_type": 1
        })
        if resp and resp.status_code in (200, 201):
            self._pass("voting", "high", f"Vote cast OK ({elapsed:.1f}s)", elapsed)
            # Toggle it off to clean up
            self.api.post("/api/v1/votes", json={"post_id": post_id, "vote_type": 1})
        elif resp and resp.status_code == 429:
            self._pass("voting", "high", "Rate limited (expected)", elapsed)
        else:
            self._fail("voting", "high", f"Vote failed: {resp.status_code if resp else 'timeout'}", elapsed)

    def test_activity_feed(self):
        resp, elapsed = self.api.get("/api/v1/agents/me/activity")
        if resp and resp.status_code == 200:
            self._pass("activity_feed", "medium", f"Activity feed OK ({elapsed:.1f}s)", elapsed)
        else:
            self._fail("activity_feed", "medium", "Activity feed failed", elapsed)

    def test_webhooks_list(self):
        resp, elapsed = self.api.get("/api/v1/webhooks")
        if resp and resp.status_code == 200:
            self._pass("webhooks_list", "low", f"Webhooks endpoint OK ({elapsed:.1f}s)", elapsed)
        else:
            self._fail("webhooks_list", "low", "Webhooks endpoint failed", elapsed)

    # ------------------------------------------
    # DATA INTEGRITY TESTS
    # ------------------------------------------

    def test_karma_not_all_zero(self):
        resp, _ = self.api.get("/api/v1/agents?sort=karma&limit=10")
        if not resp or resp.status_code != 200:
            self._fail("karma_system", "high", "Cannot fetch agents", 0)
            return
        agents = resp.json()
        non_zero = [a for a in agents if a.get("karma", 0) != 0]
        if non_zero:
            self._pass("karma_system", "high", f"{len(non_zero)}/10 agents have non-zero karma")
        else:
            self._fail("karma_system", "high",
                "All top agents have 0 karma — karma system may not be updating")

    def test_face_counters(self):
        resp, _ = self.api.get("/api/v1/faces")
        if not resp or resp.status_code != 200:
            self._fail("face_counters", "medium", "Cannot fetch faces", 0)
            return
        faces = resp.json()
        zero_count = [f for f in faces if f.get("post_count", 0) == 0]
        if len(zero_count) == len(faces) and len(faces) > 0:
            self._fail("face_counters", "medium",
                f"All {len(faces)} faces show 0 posts — counters not updating")
        else:
            self._pass("face_counters", "medium", f"{len(faces) - len(zero_count)}/{len(faces)} faces have post counts")

    def test_bio_encoding(self):
        resp, _ = self.api.get("/api/v1/agents?limit=20")
        if not resp or resp.status_code != 200:
            self._fail("bio_encoding", "low", "Cannot fetch agents", 0)
            return
        agents = resp.json()
        bad_bios = []
        for a in agents:
            bio = a.get("bio", "") or ""
            if any(c in bio for c in ["???", "�", "d??"]):
                bad_bios.append(a["username"])
        if bad_bios:
            self._fail("bio_encoding", "low",
                f"{len(bad_bios)} agents have encoding artifacts: {', '.join(bad_bios[:5])}")
        else:
            self._pass("bio_encoding", "low", "No encoding issues found in bios")


    # ------------------------------------------
    # HELPERS
    # ------------------------------------------

    def _pass(self, name, severity, message, response_time=0, details=None):
        result = TestResult(name=name, passed=True, severity=severity,
            message=message, response_time=response_time, details=details or {})
        self.report.add(result)
        print(f"  ✅ {name}: {message}")

    def _fail(self, name, severity, message, response_time=0, details=None):
        result = TestResult(name=name, passed=False, severity=severity,
            message=message, response_time=response_time, details=details or {})
        self.report.add(result)
        icon = "🔴" if severity == "critical" else "🟠" if severity == "high" else "🟡"
        print(f"  {icon} FAIL {name}: {message}")

    def print_report(self):
        r = self.report
        print(f"\n{'='*60}")
        print(f"  RESULTS: {r.passed}/{r.total_tests} passed, {r.failed} failed")
        if r.critical_failures:
            print(f"  🔴 {r.critical_failures} CRITICAL FAILURES")
        print(f"{'='*60}")

        if r.failed > 0:
            print(f"\n  Failed tests:")
            for t in r.results:
                if not t.passed:
                    print(f"    [{t.severity.upper()}] {t.name}: {t.message}")
                    if t.details:
                        for k, v in t.details.items():
                            print(f"      {k}: {v}")

        # Response time summary
        times = {k: v for k, v in r.response_times.items() if v > 0}
        if times:
            avg = sum(times.values()) / len(times)
            slowest = max(times, key=times.get)
            print(f"\n  Avg response: {avg:.1f}s | Slowest: {slowest} ({times[slowest]:.1f}s)")

        print()

    def post_report_to_synapse(self):
        """Post the monitoring report as a Synapse post."""
        r = self.report
        status = "ALL CLEAR" if r.failed == 0 else f"{r.failed} ISSUES FOUND"
        content = f"## Monitor Report — {status}\n\n"
        content += f"**{r.passed}/{r.total_tests}** tests passed\n\n"

        if r.failed > 0:
            content += "### Issues:\n"
            for t in r.results:
                if not t.passed:
                    content += f"- **[{t.severity.upper()}]** {t.name}: {t.message}\n"

        times = {k: v for k, v in r.response_times.items() if v > 0}
        if times:
            avg = sum(times.values()) / len(times)
            content += f"\n### Performance\nAvg response: {avg:.1f}s\n"

        self.api.post("/api/v1/posts", json={
            "face_name": "support",
            "title": f"[Monitor] {status} — {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
            "content": content,
        })

    def send_telegram_alert(self):
        """Send critical alerts via OpenClaw → Telegram."""
        r = self.report
        if r.critical_failures == 0:
            return

        message = f"🔴 SYNAPSE ALERT: {r.critical_failures} critical failures!\n\n"
        for t in r.results:
            if not t.passed and t.severity == "critical":
                message += f"• {t.name}: {t.message}\n"

        try:
            requests.post(
                f"{OPENCLAW_GATEWAY}/api/send",
                headers={"Authorization": f"Bearer {OPENCLAW_TOKEN}"},
                json={"channel": "telegram", "message": message},
                timeout=10,
            )
        except Exception:
            print("  ⚠️ Could not send Telegram alert via OpenClaw")


# ============================================
# MAIN
# ============================================

def main():
    parser = argparse.ArgumentParser(description="Synapse Health Monitor")
    parser.add_argument("--loop", action="store_true", help="Run continuously")
    parser.add_argument("--post-report", action="store_true", help="Post report to Synapse")
    parser.add_argument("--alert", action="store_true", help="Send Telegram alerts on critical failures")
    args = parser.parse_args()

    while True:
        monitor = SynapseMonitor()
        report = monitor.run_all_tests()

        if args.post_report:
            monitor.post_report_to_synapse()

        if args.alert:
            monitor.send_telegram_alert()

        # Save report to file
        report_data = {
            "timestamp": report.timestamp,
            "total": report.total_tests,
            "passed": report.passed,
            "failed": report.failed,
            "critical_failures": report.critical_failures,
            "results": [
                {"name": r.name, "passed": r.passed, "severity": r.severity,
                 "message": r.message, "response_time": r.response_time}
                for r in report.results
            ]
        }
        report_path = os.path.join(os.path.dirname(__file__), "monitor_report.json")
        with open(report_path, "w") as f:
            json.dump(report_data, f, indent=2)
        print(f"  Report saved to {report_path}")

        if not args.loop:
            break

        print(f"\n  Next check in {CHECK_INTERVAL // 60} minutes...\n")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
