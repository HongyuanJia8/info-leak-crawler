import requests
import json
import time

# --- Helper function to make authenticated requests with optional rate limit handling ---
def github_request(url, token=None, params=None):
    headers = {"Authorization": f"token {token}"} if token else {}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 403 and "X-RateLimit-Remaining" in response.headers:
        reset_time = int(response.headers.get("X-RateLimit-Reset", time.time() + 60))
        wait_seconds = reset_time - time.time()
        print(f"Rate limit exceeded. Waiting {wait_seconds:.0f} seconds...")
        time.sleep(wait_seconds)
        response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def get_user_info(username, token=None):
    url = f"https://api.github.com/users/{username}"
    data = github_request(url, token)
    return {
        "login": data.get("login"),
        "name": data.get("name"),
        "company": data.get("company"),
        "location": data.get("location"),
        "email": data.get("email"),
        "bio": data.get("bio"),
        "public_repos": data.get("public_repos"),
        "followers": data.get("followers"),
        "following": data.get("following")
    }

def get_user_network(username, token=None):
    followers = github_request(f"https://api.github.com/users/{username}/followers", token)
    following = github_request(f"https://api.github.com/users/{username}/following", token)
    return {
        "followers": [user["login"] for user in followers],
        "following": [user["login"] for user in following]
    }

def get_repo_details(username, token=None):
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{username}/repos"
        params = {"per_page": 100, "page": page}
        page_data = github_request(url, token, params)
        if not page_data:
            break
        for repo in page_data:
            repos.append({
                "name": repo["name"],
                "description": repo["description"],
                "language": repo["language"],
                "created_at": repo["created_at"],
                "updated_at": repo["updated_at"],
                "stars": repo["stargazers_count"],
                "forks": repo["forks_count"],
                "html_url": repo.get("html_url"),
                "archived": repo.get("archived"),
                "default_branch": repo.get("default_branch")
            })
        page += 1
    return repos

def get_commit_activity(username, repo, token=None):
    url = f"https://api.github.com/repos/{username}/{repo}/stats/commit_activity"
    try:
        data = github_request(url, token)
        total_commits = sum(week["total"] for week in data)
        return total_commits
    except Exception:
        return None

def collect_github_profile(username, token=None):
    profile = get_user_info(username, token)
    network = get_user_network(username, token)
    repos = get_repo_details(username, token)

    for repo in repos:
        commit_count = get_commit_activity(username, repo["name"], token)
        repo["recent_commits"] = commit_count

    result = {
        "profile": profile,
        "network": network,
        "repositories": repos
    }
    return result

def main():
    username = input("Enter GitHub username: ")
    token = input("Enter GitHub token (or leave blank): ").strip() or None

    print("\nCollecting data...")
    data = collect_github_profile(username, token)

    output_filename = f"{username}_github_profile.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"\nData saved to '{output_filename}'")

if __name__ == "__main__":
    main()
