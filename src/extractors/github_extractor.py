import requests

def extract(url):
    if not url:
        return None
    username = url.rstrip("/").split("/")[-1]
    try:
        user_resp = requests.get(f"https://api.github.com/users/{username}", timeout=5)
        if user_resp.status_code != 200:
            return None
        user = user_resp.json()

        repo_resp = requests.get(f"https://api.github.com/users/{username}/repos", timeout=5)
        repos = repo_resp.json() if repo_resp.status_code == 200 else []

        langs = {}
        for r in repos:
            lang = r.get("language")
            if lang:
                langs[lang] = langs.get(lang, 0) + 1

        return {
            "source": "github",
            "fields": {
                "full_name": user.get("name"),
                "headline": user.get("bio"),
                "skills_raw": list(langs.keys()),
                "github_url": user.get("html_url"),
                "email": user.get("email"),
            }
        }
    except requests.RequestException:
        return None