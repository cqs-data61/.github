import requests
import os
import json
from datetime import datetime
import pytz

# GitHub username (can be set via environment variable in secrets)
USER_NAME = os.getenv('USER_NAME')
TOKEN = os.getenv('PAT_TOKEN')  # Get from GitHub secrets
COUNT_FILENAME = '.github/counts.json'

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


def update_readme(count, uniques, clones, forks, stars, watches):
    readme_filename = "profile/README.md"
    timezone = pytz.timezone('UTC')

    # Prepare the stats output
    '''
    stats_section = (
        f"<!-- STATS-START -->\n"
        f"*GitHub Stats (Updated: {datetime.now(timezone).strftime('%d-%m-%Y %H:%M %Z%z')})*  \n"
        f"![View](https://img.shields.io/badge/View-{count}-lightgreen) ![Unique Visitor](https://img.shields.io/badge/Unique_Visitor-{uniques}-green) ![Clone](https://img.shields.io/badge/Clone-{clones}-royalblue) ![Watch](https://img.shields.io/badge/Watch-{watches}-blue) ![Fork](https://img.shields.io/badge/Fork-{forks}-orange) ![Star](https://img.shields.io/badge/Star-{stars}-yellow)  \n"
        f""
        f"<!-- STATS-END -->"
    )
    '''
    stats_section = (
        f"<!-- STATS-START -->\n"
        f"*GitHub Stats (Updated: {datetime.now(timezone).strftime('%d-%m-%Y %H:%M %Z%z')})*  \n"
        f"![View](https://img.shields.io/badge/View-{count}-lightgreen) ![Clone](https://img.shields.io/badge/Clone-{clones}-royalblue) ![Watch](https://img.shields.io/badge/Watch-{watches}-blue) ![Fork](https://img.shields.io/badge/Fork-{forks}-orange) ![Star](https://img.shields.io/badge/Star-{stars}-yellow)  \n"
        f""
        f"<!-- STATS-END -->"
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


def get_view_counts(user, repo, counts):
    url = f"https://api.github.com/repos/{user}/{repo['name']}/traffic/views"
    response = requests.get(url, headers=headers)
    json_obj = response.json()
    if 'views' in json_obj:
        for view in json_obj['views']:
            timestamp = view['timestamp']
            if timestamp in counts:
                counts[timestamp]['count'] = counts[timestamp]['count'] + view['count']
                counts[timestamp]['uniques'] = counts[timestamp]['uniques'] + view['uniques']
            else:
                counts[timestamp] = {
                    'count': view['count'],
                    'uniques': view['uniques'],
                    'clone_count': 0,
                    'unique_clones': 0
                }


def get_clone_counts(user, repo, counts):
    url = f"https://api.github.com/repos/{user}/{repo['name']}/traffic/clones"
    response = requests.get(url, headers=headers)
    json_obj = response.json()
    if 'clones' in json_obj:
        for view in json_obj['clones']:
            timestamp = view['timestamp']
            if timestamp in counts:
                counts[timestamp]['clone_count'] = counts[timestamp]['clone_count'] + view['count']
                counts[timestamp]['unique_clones'] = counts[timestamp]['unique_clones'] + view['uniques']
            else:
                counts[timestamp] = {
                    'count': 0,
                    'uniques': 0,
                    'clone_count': view['count'],
                    'unique_clones': view['uniques']
                }


# Main function
def aggregate_github_stats(user):
    repos = []
    counts = {}

    print('getting list...')
    repo_list = get_repositories(user)
    print(f'received {len(repo_list)} repos')

    for repo in repo_list:
        # get repo details
        _repo = get_repo(repo)
        repos.append(_repo)

        # get view stats
        get_view_counts(user, repo, counts)

        # get clone stats
        get_clone_counts(user, repo, counts)

    # load previous counts
    total_counts = {}
    try:
        with open(COUNT_FILENAME, 'r') as json_file:
            total_counts = json.load(json_file)
    except:
        pass

    # replace with new counts
    for key, count in counts.items():
        total_counts[key] = count

    stars = 0
    watches = 0
    forks = 0
    for repo in repos:
        if 'parent' in repo:
            parent = repo['parent']
            stars += parent['stargazers_count'] + repo['stargazers_count']
            watches += parent['watchers_count'] + repo['watchers_count']
            forks += parent['forks_count'] + repo['forks_count']
        else:
            stars += repo['stargazers_count']
            watches += repo['watchers_count']
            forks += repo['forks_count']

    total_visits = 0
    total_uniques = 0
    clones = 0
    unique_clones = 0
    for timestamp, count in total_counts.items():
        total_visits += count['count']
        total_uniques += count['uniques']
        clones += count['clone_count']
        unique_clones += count['unique_clones']

    update_readme(total_visits, total_uniques, clones, forks, stars, watches)
    print(f'Forks: {forks}')
    print(f'Stars: {stars}')
    print(f'Watches: {watches}')
    print(f"Clones: {clones}")
    print(f"Unique Clones: {unique_clones}")
    print(f"Visits: {total_visits}")
    print(f"Uniques: {total_uniques}")

    with open(COUNT_FILENAME, 'w') as f:
        f.write(json.dumps(total_counts))


# Run the script
if __name__ == "__main__":
    aggregate_github_stats(USER_NAME)
