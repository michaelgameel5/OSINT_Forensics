from bs4 import BeautifulSoup
import requests
import json
import os
import datetime

class ProfileExtractor:
    def __init__(self, output_dir="data/processed"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36"
        }

    # ─────────────────────────────────────────
    # GITHUB — public REST API, no auth needed
    # ─────────────────────────────────────────
    def extract_github(self, username: str) -> dict:
        url = f"https://api.github.com/users/{username}"
        try:
            r = requests.get(url, headers=self.headers, timeout=10)
        except Exception as e:
            print(f"[✗] GitHub request failed: {e}")
            return {}

        if r.status_code == 404:
            print(f"[✗] GitHub: user '{username}' not found")
            return {}
        if r.status_code != 200:
            print(f"[✗] GitHub: HTTP {r.status_code}")
            return {}

        d = r.json()
        profile = {
            "platform":     "GitHub",
            "username":     d.get("login"),
            "display_name": d.get("name"),
            "bio":          d.get("bio"),
            "location":     d.get("location"),
            "email":        d.get("email"),
            "company":      d.get("company"),
            "website":      d.get("blog"),
            "followers":    d.get("followers"),
            "following":    d.get("following"),
            "public_repos": d.get("public_repos"),
            "created_at":   d.get("created_at"),
            "updated_at":   d.get("updated_at"),
            "profile_url":  d.get("html_url"),
            "avatar_url":   d.get("avatar_url"),
            "extracted_at": datetime.datetime.utcnow().isoformat(),
        }
        print(f"[✓] GitHub profile extracted for: {username}")
        return profile

    # ─────────────────────────────────────────
    # REDDIT — public JSON API, no auth needed
    # ─────────────────────────────────────────
    def extract_reddit(self, username: str) -> dict:
        url = f"https://www.reddit.com/user/{username}/about.json"
        try:
            r = requests.get(url, headers=self.headers, timeout=10)
        except Exception as e:
            print(f"[✗] Reddit request failed: {e}")
            return {}

        if r.status_code == 404:
            print(f"[✗] Reddit: user '{username}' not found")
            return {}
        if r.status_code != 200:
            print(f"[✗] Reddit: HTTP {r.status_code}")
            return {}

        data = r.json()
        # Suspended/deleted accounts return 200 with an error field
        if data.get("error") or not data.get("data"):
            print(f"[✗] Reddit: account suspended or deleted for '{username}'")
            return {}

        d = data["data"]
        profile = {
            "platform":      "Reddit",
            "username":      d.get("name"),
            "bio":           d.get("subreddit", {}).get("public_description"),
            "post_karma":    d.get("link_karma"),
            "comment_karma": d.get("comment_karma"),
            "total_karma":   d.get("total_karma"),
            "is_verified":   d.get("verified"),
            "is_mod":        d.get("is_mod"),
            "account_age":   datetime.datetime.utcfromtimestamp(
                                 d.get("created_utc", 0)
                             ).isoformat(),
            "profile_url":   f"https://reddit.com/user/{username}",
            "icon_url":      d.get("icon_img"),
            "extracted_at":  datetime.datetime.utcnow().isoformat(),
        }
        print(f"[✓] Reddit profile extracted for: {username}")
        return profile

    # ─────────────────────────────────────────
    # TWITTER — scrape public profile page
    # Only bio/name/handle available without API
    # ─────────────────────────────────────────
    def extract_twitter(self, username: str) -> dict:
        url = f"https://twitter.com/{username}"
        try:
            r = requests.get(url, headers=self.headers, timeout=10, allow_redirects=True)
        except Exception as e:
            print(f"[✗] Twitter request failed: {e}")
            return {}

        # Redirected to /home or /login = account doesn't exist
        final = r.url.rstrip("/").lower()
        for sink in ["twitter.com/home", "x.com/home", "twitter.com/login", "x.com/login"]:
            if sink in final:
                print(f"[✗] Twitter: user '{username}' not found (redirected)")
                return {}

        if r.status_code != 200:
            print(f"[✗] Twitter: HTTP {r.status_code}")
            return {}

        # Twitter is heavily JS-rendered; extract what's available in raw HTML
        soup = BeautifulSoup(r.text, "html.parser")

        # og: meta tags are the most reliable source before JS loads
        def og(prop):
            tag = soup.find("meta", property=f"og:{prop}") or \
                  soup.find("meta", attrs={"name": f"og:{prop}"})
            return tag["content"].strip() if tag and tag.get("content") else None

        title       = og("title") or ""
        description = og("description") or ""

        # og:title is usually "Display Name (@handle)"
        display_name = title.split("(")[0].strip() if "(" in title else title

        profile = {
            "platform":     "Twitter",
            "username":     username,
            "display_name": display_name or None,
            "bio":          description or None,
            "profile_url":  f"https://twitter.com/{username}",
            "note":         "Limited data — Twitter requires API access for full profile",
            "extracted_at": datetime.datetime.utcnow().isoformat(),
        }
        print(f"[✓] Twitter profile extracted for: {username}")
        return profile

    # ─────────────────────────────────────────
    # INSTAGRAM — scrape public profile page
    # Only basic meta available without API
    # ─────────────────────────────────────────
    def extract_instagram(self, username: str) -> dict:
        url = f"https://www.instagram.com/{username}/"
        try:
            r = requests.get(url, headers=self.headers, timeout=10, allow_redirects=True)
        except Exception as e:
            print(f"[✗] Instagram request failed: {e}")
            return {}

        # Redirected to login = account doesn't exist or blocked
        final = r.url.rstrip("/").lower()
        if "accounts/login" in final:
            print(f"[✗] Instagram: user '{username}' not found or login required")
            return {}

        if r.status_code == 404:
            print(f"[✗] Instagram: user '{username}' not found")
            return {}

        soup = BeautifulSoup(r.text, "html.parser")

        def meta(prop=None, name=None):
            if prop:
                tag = soup.find("meta", property=prop)
            else:
                tag = soup.find("meta", attrs={"name": name})
            return tag["content"].strip() if tag and tag.get("content") else None

        title       = meta(prop="og:title") or ""
        description = meta(prop="og:description") or ""
        image       = meta(prop="og:image")

        # og:title is usually "username • Instagram photos and videos" or
        # "Display Name (@username) • Instagram photos and videos"
        display_name = title.split("•")[0].strip() if "•" in title else title

        profile = {
            "platform":     "Instagram",
            "username":     username,
            "display_name": display_name or None,
            "bio":          description or None,
            "avatar_url":   image,
            "profile_url":  f"https://www.instagram.com/{username}/",
            "note":         "Limited data — Instagram requires API access for full profile",
            "extracted_at": datetime.datetime.utcnow().isoformat(),
        }
        print(f"[✓] Instagram profile extracted for: {username}")
        return profile

    # ─────────────────────────────────────────
    # SAVE TO JSON
    # ─────────────────────────────────────────
    def save_profile(self, profile: dict, platform: str, username: str):
        if not profile:
            return
        ts       = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.output_dir}/{platform}_{username}_{ts}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=4)
        print(f"[+] Profile saved → {filename}")

    # ─────────────────────────────────────────
    # EXTRACT ALL — only platforms where found=True
    # Pass username_search results to skip missing accounts
    # ─────────────────────────────────────────
    def extract_all(self, username: str, username_search: dict = None) -> dict:
        """
        username_search: dict returned by search_username(), e.g.
            {"GitHub": {"found": True, ...}, "Reddit": {"found": False, ...}}
        If provided, only extract profiles for platforms where found=True.
        If not provided, attempt all platforms anyway.
        """
        print(f"\n[*] Extracting profiles for: {username}\n")

        def is_found(platform_key):
            if username_search is None:
                return True  # no filter — try everything
            entry = username_search.get(platform_key, {})
            return entry.get("found", False)

        extractors = {
            "github":    (self.extract_github,    "GitHub"),
            "reddit":    (self.extract_reddit,    "Reddit"),
            "twitter":   (self.extract_twitter,   "Twitter"),
            "instagram": (self.extract_instagram, "Instagram"),
        }

        results = {}
        for key, (fn, search_key) in extractors.items():
            if not is_found(search_key):
                print(f"[–] Skipping {search_key}: not found in username search")
                continue
            data = fn(username)
            if data:
                results[key] = data
                self.save_profile(data, key, username)

        return results