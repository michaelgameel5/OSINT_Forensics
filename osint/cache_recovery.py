# -*- coding: utf-8 -*-
import requests
import json
import os
import datetime
import uuid
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class CacheRecovery:
    def __init__(self, output_dir="data/processed"):
        self.output_dir  = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.headers     = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        self.wayback_api = "https://archive.org/wayback/available"
        self.cdx_api     = "https://web.archive.org/cdx/search/cdx"

        # Session with automatic retries
        self.session = requests.Session()
        retry = Retry(
            total=2,
            backoff_factor=3,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://",  adapter)
        self.session.mount("https://", adapter)

    # ─────────────────────────────────────────
    # CHECK AVAILABILITY
    # ─────────────────────────────────────────
    def check_availability(self, url: str) -> dict:
        print(f"[*] Checking availability for: {url}")
        try:
            res = self.session.get(
                self.wayback_api,
                params={"url": url},
                headers=self.headers,
                timeout=60
            )
        except requests.exceptions.Timeout:
            print("[X] Timed out checking availability")
            return {}
        except requests.exceptions.ConnectionError:
            print("[X] Connection error")
            return {}

        if res.status_code != 200 or not res.text.strip():
            print("[X] Empty response")
            return {}

        try:
            data = res.json()
        except Exception:
            print("[X] Invalid JSON response")
            return {}

        snapshot = data.get("archived_snapshots", {}).get("closest", {})
        if not snapshot:
            print(f"[X] No snapshots found for: {url}")
            return {}

        print(f"[+] Snapshot found: {snapshot.get('timestamp')}")
        return snapshot

    # ─────────────────────────────────────────
    # GET SNAPSHOT HISTORY
    # ─────────────────────────────────────────
    def get_snapshot_history(self, url: str, limit: int = 10) -> list:
        print(f"[*] Fetching snapshot history for: {url}")
        params = {
            "url":      url,
            "output":   "json",
            "limit":    limit,
            "fl":       "timestamp,statuscode,mimetype,length",
            "collapse": "timestamp:8"
        }
        try:
            res = self.session.get(
                self.cdx_api,
                params=params,
                headers=self.headers,
                timeout=60
            )
        except requests.exceptions.Timeout:
            print("[X] Timed out fetching snapshot history")
            return []
        except requests.exceptions.ConnectionError:
            print("[X] Connection error")
            return []

        if res.status_code != 200 or not res.text.strip():
            print("[X] No snapshot history found")
            return []

        try:
            rows = res.json()
        except Exception:
            print("[X] Invalid JSON response")
            return []

        if len(rows) <= 1:
            print("[X] No records returned")
            return []

        headers   = rows[0]
        snapshots = []
        for row in rows[1:]:
            entry = dict(zip(headers, row))
            entry["wayback_url"] = (
                f"https://web.archive.org/web/{entry['timestamp']}/{url}"
            )
            snapshots.append(entry)

        print(f"[+] Found {len(snapshots)} snapshots")
        for s in snapshots:
            print(f"    [{s['timestamp']}] {s['statuscode']} -> {s['wayback_url']}")
        return snapshots

    # ─────────────────────────────────────────
    # DETECT DELETED CONTENT
    # ─────────────────────────────────────────
    def detect_deleted_content(self, url: str) -> list:
        print(f"[*] Scanning for deleted content: {url}")
        params = {
            "url":    url,
            "output": "json",
            "limit":  50,
            "fl":     "timestamp,statuscode",
        }
        try:
            res = self.session.get(
                self.cdx_api,
                params=params,
                headers=self.headers,
                timeout=60
            )
        except requests.exceptions.Timeout:
            print("[X] Timed out scanning deleted content")
            return []
        except requests.exceptions.ConnectionError:
            print("[X] Connection error")
            return []

        if res.status_code != 200 or not res.text.strip():
            print("[X] No history found")
            return []

        try:
            rows = res.json()
        except Exception:
            print("[X] Invalid JSON response")
            return []

        if len(rows) <= 1:
            print("[X] No records returned")
            return []

        headers  = rows[0]
        deleted  = []
        was_live = False

        for row in rows[1:]:
            entry  = dict(zip(headers, row))
            status = entry.get("statuscode", "")
            if status == "200":
                was_live = True
            if was_live and status in ("404", "301", "302", "gone"):
                deleted.append({
                    "timestamp":   entry["timestamp"],
                    "status":      status,
                    "wayback_url": f"https://web.archive.org/web/{entry['timestamp']}/{url}"
                })

        if deleted:
            print(f"[!] Found {len(deleted)} deleted/modified snapshots")
            for d in deleted:
                print(f"    [{d['timestamp']}] HTTP {d['status']} -> {d['wayback_url']}")
        else:
            print("[+] No deleted content detected")

        return deleted

    # ─────────────────────────────────────────
    # RECOVER ALL PLATFORMS
    # ─────────────────────────────────────────
    def recover_all(self, username: str, platforms: dict = None) -> dict:
        if platforms is None:
            platforms = {
                "github":    f"https://github.com/{username}",
                "reddit":    f"https://reddit.com/user/{username}",
                "twitter":   f"https://twitter.com/{username}",
                "instagram": f"https://instagram.com/{username}",
            }

        slow_platforms = ["twitter", "instagram"]

        print(f"\n{'='*50}")
        print(f"  Cache Recovery Report for: {username}")
        print(f"{'='*50}")

        results = {}
        for platform, url in platforms.items():
            print(f"\n--- {platform.upper()} ---")
            if platform in slow_platforms:
                print(f"[*] {platform} may be slow, please wait...")
            try:
                results[platform] = {
                    "url":              url,
                    "availability":     self.check_availability(url),
                    "snapshot_history": self.get_snapshot_history(
                                            url,
                                            limit=5 if platform in slow_platforms else 10
                                        ),
                    "deleted_content":  self.detect_deleted_content(url),
                }
            except Exception as e:
                print(f"[X] {platform} failed: {str(e)[:80]}")
                results[platform] = {"url": url, "status": "failed"}
                continue

        self.save_results(results, username)
        return results

    # ─────────────────────────────────────────
    # SAVE RESULTS
    # ─────────────────────────────────────────
    def save_results(self, results: dict, username: str):
        filename = (
            f"{self.output_dir}/cache_recovery_{username}_"
            f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4)
        print(f"\n[+] Cache recovery report saved -> {filename}")