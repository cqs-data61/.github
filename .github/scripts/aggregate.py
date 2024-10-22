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
    '''
    while True:
        url = f"https://api.github.com/users/{user}/repos?page={page}&per_page=100"
        print(url)
        response = requests.get(url, headers=headers)
        data = response.json()
        print(data)
        if len(data) == 0:
            break
        repos.extend(data)
        page += 1
    '''

    url = f"https://api.github.com/users/{user}/repos?page={page}&per_page=100"
    print(url)
    response = requests.get(url, headers=headers)
    data = response.json()
    print(data)

    return data


def get_repo(repo):
    url = repo['url']
    response = requests.get(url, headers=headers)
    return response.json()


def update_readme(forks, stars):
    readme_filename = "profile/README.md"

    # Prepare the stats output
    stats_section = (
        f"<!-- STATS-START -->\n"
        f"![Forks](https://img.shields.io/badge/Forks-{forks}-orange) ![Stars](https://img.shields.io/badge/Stars-{stars}-yellow)\n"
        f"<!-- STATS-END -->\n"
    )

    # Read the current README.md content
    with open(readme_filename, "r") as file:
        content = file.read()

    # Replace the old stats section between <!-- STATS-START --> and <!-- STATS-END -->
    if "<!-- STATS-START -->" in content and "<!-- STATS-END -->" in content:
        # Find and replace the stats section
        updated_content = content.split("<!-- STATS-START -->")[0] + stats_section + content.split("<!-- STATS-END -->")[1]
    else:
        # If no stats section exists, append it at the end
        updated_content = content + "\n" + stats_section

    # Write the updated content back to README.md
    with open(readme_filename, "w") as file:
        file.write(updated_content)


# Main function
def aggregate_github_stats(user):
    repos = []
    print('getting list...')
    repo_list = get_repositories(user)
    print(f'received {len(repo_list)} repos')

    for repo in repo_list:
        _repo = get_repo(repo)
        repos.append(_repo)

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

    #update_readme(forks, stars)
    print(f'Forks: {forks}')
    print(f'Stars: {stars}')


# Run the script
if __name__ == "__main__":
    aggregate_github_stats(GITHUB_USER)
