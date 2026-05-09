# -*- coding: utf-8 -*-
import os
import json
import datetime
import uuid
import glob
from jinja2 import Environment, FileSystemLoader

class ReportGenerator:
    def __init__(self,
                 output_dir="data/reports",
                 template_dir="src/reports/templates"):
        self.output_dir   = output_dir
        self.template_dir = template_dir
        os.makedirs(output_dir, exist_ok=True)
        self.env = Environment(loader=FileSystemLoader(self.template_dir))

    # ─────────────────────────────────────────
    # LOAD LATEST JSON FILE BY PREFIX
    # ─────────────────────────────────────────
    def _load_latest(self, prefix: str, folder: str = "data/processed") -> dict:
        pattern = os.path.join(folder, f"{prefix}*.json")
        files   = sorted(glob.glob(pattern), reverse=True)
        if not files:
            return {}
        with open(files[0], "r", encoding="utf-8") as f:
            print(f"[+] Loaded: {files[0]}")
            return json.load(f)

    def _load_graph(self, username: str) -> dict:
        pattern = os.path.join("data/graphs", f"graph_data_{username}*.json")
        files   = sorted(glob.glob(pattern), reverse=True)
        if not files:
            return {}
        with open(files[0], "r", encoding="utf-8") as f:
            return json.load(f)

    # ─────────────────────────────────────────
    # COLLECT ALL DATA
    # ─────────────────────────────────────────
    def collect_data(self, username: str) -> dict:
        print(f"\n[*] Collecting investigation data for: {username}")

        # 1. Run username search — source of truth for what exists
        from src.osint.username_search import search_username
        username_search = search_username(username)

        # 2. Extract profiles ONLY for found platforms
        from src.extractor.profile_extractor import ProfileExtractor
        extractor = ProfileExtractor()
        profiles  = extractor.extract_all(username, username_search=username_search)

        # 3. Graph + cache from saved files
        graph_data = self._load_graph(username)
        cache_data = self._load_latest(f"cache_recovery_{username}")

        return {
            "username":        username,
            "username_search": username_search,
            "profiles":        profiles,       # only platforms that were FOUND
            "graph_data":      graph_data,
            "cache_data":      cache_data,
            "generated_at":    datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "report_id":       str(uuid.uuid4())[:8].upper(),
        }

    # ─────────────────────────────────────────
    # GENERATE HTML REPORT
    # ─────────────────────────────────────────
    def generate_html(self, username: str) -> str:
        data     = self.collect_data(username)
        template = self.env.get_template("report_template.html")
        html     = template.render(**data)

        ts       = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.output_dir}/report_{username}_{ts}.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"\n[+] HTML report saved → {filename}")
        return filename

    # ─────────────────────────────────────────
    # GENERATE JSON REPORT
    # ─────────────────────────────────────────
    def generate_json(self, username: str) -> str:
        data     = self.collect_data(username)
        ts       = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.output_dir}/report_{username}_{ts}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        print(f"[+] JSON report saved → {filename}")
        return filename