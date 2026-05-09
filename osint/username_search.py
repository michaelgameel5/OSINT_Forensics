import requests

# ──────────────────────────────────────────────────────────────
# Platform checkers
# Each function returns (found: bool, reason: str, url: str)
# ──────────────────────────────────────────────────────────────

def _check_github(username: str):
    """Use the public GitHub API — returns 404 cleanly for missing users."""
    api_url     = f"https://api.github.com/users/{username}"
    profile_url = f"https://github.com/{username}"
    try:
        r = requests.get(
            api_url,
            timeout=10,
            headers={
                "User-Agent": "osint-tool",
                "Accept": "application/vnd.github+json",
            },
        )
        if r.status_code == 200:
            return True,  "GitHub API: user exists",        profile_url
        elif r.status_code == 404:
            return False, "GitHub API: 404 not found",      profile_url
        elif r.status_code == 403:
            return False, "GitHub API: rate limited (403)", profile_url
        else:
            return False, f"GitHub API: HTTP {r.status_code}", profile_url
    except requests.exceptions.Timeout:
        return False, "timeout", profile_url
    except Exception as e:
        return False, str(e), profile_url


def _check_twitter(username: str):
    """
    Twitter/X always returns 200 — must inspect the response body.
    Uses plain requests (no session/self needed).
    """
    url = f"https://twitter.com/{username}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    try:
        r = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
    except requests.exceptions.Timeout:
        return False, "timeout", url
    except Exception as e:
        return False, str(e), url

    body = r.text.lower()

    not_found_signals = [
        "this account doesn't exist",
        "account suspended",
        "caution: this account is temporarily restricted",
        "try searching for another",
        "user not found",
        "sorry, that page doesn't exist",
    ]
    for signal in not_found_signals:
        if signal in body:
            return False, f"page contains: '{signal}'", url

    # Twitter is JS-heavy — a tiny body means the profile didn't render
    if len(body) < 500:
        return False, "response too small to confirm (JS-rendered, likely missing)", url

    return True, "no not-found signals detected", url
def _check_reddit(username: str):
    """Reddit's API returns clean 404 for missing users."""
    api_url     = f"https://www.reddit.com/user/{username}/about.json"
    profile_url = f"https://reddit.com/user/{username}"
    try:
        r = requests.get(
            api_url,
            timeout=10,
            headers={"User-Agent": "osint-tool/1.0"},
        )
        if r.status_code == 200:
            data = r.json()
            # Suspended accounts still return 200 but with an error field
            if data.get("error") or data.get("data", {}).get("is_suspended"):
                return False, "account suspended or deleted", profile_url
            return True, "Reddit API: user exists", profile_url
        elif r.status_code == 404:
            return False, "Reddit API: 404 not found", profile_url
        elif r.status_code == 429:
            return False, "Reddit API: rate limited (429)", profile_url
        else:
            return False, f"Reddit API: HTTP {r.status_code}", profile_url
    except requests.exceptions.Timeout:
        return False, "timeout", profile_url
    except Exception as e:
        return False, str(e), profile_url


def _check_instagram(username: str):
    """
    Instagram heavily blocks scrapers. Use the same redirect trick as Twitter:
    missing profiles redirect to /accounts/login/.
    """
    profile_url = f"https://www.instagram.com/{username}/"
    try:
        r = requests.get(
            profile_url,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"},
            allow_redirects=True,
        )
        final_url = r.url.rstrip("/").lower()

        redirect_sinks = [
            "https://www.instagram.com/accounts/login",
            "https://instagram.com/accounts/login",
        ]
        for sink in redirect_sinks:
            if final_url.startswith(sink.lower()):
                return False, "redirected to login page", profile_url

        if r.status_code == 404:
            return False, "HTTP 404", profile_url

        if username.lower() in final_url:
            return True, "stayed on profile URL", profile_url

        return False, f"unexpected redirect to {r.url}", profile_url

    except requests.exceptions.Timeout:
        return False, "timeout", profile_url
    except Exception as e:
        return False, str(e), profile_url


# ──────────────────────────────────────────────────────────────
# Dispatcher
# ──────────────────────────────────────────────────────────────

CHECKERS = {
    "GitHub":    _check_github,
    "Twitter":   _check_twitter,
    "Reddit":    _check_reddit,
    "Instagram": _check_instagram,
}


def search_username(username: str) -> dict:
    results = {}
    for platform, checker in CHECKERS.items():
        found, reason, url = checker(username)
        results[platform] = {"url": url, "found": found, "reason": reason}
        icon = "✓" if found else "✗"
        print(f"[{icon}] {platform}: {url}  ({reason})")
    return results