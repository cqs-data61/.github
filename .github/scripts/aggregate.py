import requests
import os
from datetime import datetime

# GitHub username (can be set via environment variable in secrets)
GITHUB_USER = os.getenv('USER_NAME')
TOKEN = os.getenv('PAT_TOKEN')  # Get from GitHub secrets

# Headers for authentication
headers = {
    "Authorization": f"token {TOKEN}"
}


# Function to get all repositories for a user
def get_repositories(user):
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{user}/repos?page={page}&per_page=100"
        response = requests.get(url, headers=headers)
        data = response.json()
        if len(data) == 0:
            break
        repos.extend(data)
        page += 1
    return repos


def get_repo(repo):
    url = repo['url']
    response = requests.get(url, headers=headers)
    return response.json()


# Main function
def aggregate_github_stats(user):
    repos = []
    repo_list = get_repositories(user)

    for repo in repo_list[:5]:
        repos.append(get_repo(repo))

    stars = 0
    views = 0
    forks = 0
    for repo in repos:
        if 'parent' in repo:
            parent = repo['parent']
            stars += parent['stargazers_count'] + repo['stargazers_count']
            views += parent['watchers_count'] + repo['watchers_count']
            forks += parent['forks_count'] + repo['forks_count']
        else:
            stars += repo['stargazers_count']
            views += repo['watchers_count']
            forks += repo['forks_count']

    with open('profile/github_stats.md', 'w') as f:
        f.write(f"# GitHub Stats Report - {datetime.now().strftime('%Y-%m-%d')}\n")
        f.write(f"Total Stars: {stars}\n")
        f.write(f"Total Views: {views}\n")
        f.write(f"Total Views: {forks}\n")


# Run the script
if __name__ == "__main__":
    aggregate_github_stats(GITHUB_USER)
