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
    url = f"https://api.github.com/users/{user}/repos"
    response = requests.get(url, headers=headers)
    return response.json()


# Function to get total stars
def aggregate_stars(repos):
    total_stars = 0
    for repo in repos:
        total_stars += repo['stargazers_count']
    return total_stars


# Function to get views for a specific repo
def get_repo_views(owner, repo_name):
    url = f"https://api.github.com/repos/{owner}/{repo_name}/traffic/views"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()['count']
    return 0


# Function to aggregate views across all repos
def aggregate_views(repos, owner):
    total_views = 0
    for repo in repos:
        total_views += get_repo_views(owner, repo['name'])
    return total_views


# Main function
def aggregate_github_stats(user):
    repos = get_repositories(user)
    total_stars = aggregate_stars(repos)
    total_views = aggregate_views(repos, user)

    # Create an output file to store the results
    with open('github_stats.md', 'w') as f:
        f.write(f"# GitHub Stats Report - {datetime.now().strftime('%Y-%m-%d')}\n")
        f.write(f"Total Stars: {total_stars}\n")
        f.write(f"Total Views: {total_views}\n")


# Run the script
if __name__ == "__main__":
    aggregate_github_stats(GITHUB_USER)
