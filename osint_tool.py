import requests

def get_user_info(username):
    user_url = f"https://api.github.com/users/{username}"
    repos_url = f"https://api.github.com/users/{username}/repos"

    user_resp = requests.get(user_url)
    repos_resp = requests.get(repos_url)

    if user_resp.status_code != 200:
        print("Failed to fetch user info.")
        return

    user_data = user_resp.json()
    print(f"Name: {user_data.get('name')}")
    print(f"Email: {user_data.get('email')}")
    print(f"Company: {user_data.get('company')}")
    print(f"Blog: {user_data.get('blog')}")
    print(f"Location: {user_data.get('location')}")
    print(f"Public Repos: {user_data.get('public_repos')}")
    print(f"Followers: {user_data.get('followers')}")

    if repos_resp.status_code == 200:
        print("\n--- Repositories ---")
        for repo in repos_resp.json():
            print(f"{repo['name']} - {repo.get('language')} - {repo['created_at']}")
    else:
        print("Failed to fetch repos.")

if __name__ == "__main__":
    username = input("Enter GitHub username: ")
    get_user_info(username)