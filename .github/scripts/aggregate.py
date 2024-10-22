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

    for repo in repo_list:
        repos.append(get_repo(repo))

    for repo in repos:
        if 'parent' in repo:
            parent = repo['parent']
            print(parent['stargazers_count'], parent['watchers_count'], parent['forks'], parent['forks'])
        else:
            print(repo['stargazers_count'], repo['watchers_count'], repo['forks'], repo['forks'])


# Run the script
if __name__ == "__main__":
    aggregate_github_stats(GITHUB_USER)
