import os
import shutil
import requests
import git
import time
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
GITLAB_GROUP_ID = os.getenv("GITLAB_GROUP_ID")
GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")
BITBUCKET_USER = os.getenv("BITBUCKET_USER")
BITBUCKET_PASS = os.getenv("BITBUCKET_PASS")
BITBUCKET_WORKSPACE = os.getenv("BITBUCKET_WORKSPACE")
BITBUCKET_PROJECT = os.getenv("BITBUCKET_PROJECT")

# Check if any of the environment variables are not set
if not all([GITLAB_GROUP_ID, GITLAB_TOKEN, BITBUCKET_USER, BITBUCKET_PASS, BITBUCKET_WORKSPACE, BITBUCKET_PROJECT]):
    raise EnvironmentError("One or more environment variables are not set. Please check your .env file.")

def log_error(error_message):
    """
    Logs an error message to a file named 'error2.txt' in the current working directory.

    Args:
        error_message (str): The error message to be logged.

    The function appends the error message to the file, creating the file if it does not exist.
    """
    error_file_path = os.path.join(os.getcwd(), "error.txt")
    with open(error_file_path, 'a') as error_file:
        error_file.write(error_message + '\n')

def sync_repos(github_repo_url, bitbucket_repo_name):
    """
    Synchronizes a GitHub/GitLab repository to a Bitbucket repository.

    This function clones a GitHub/GitLab repository, creates a corresponding repository on Bitbucket,
    and pushes all branches and tags from the GitHub/GitLab repository to the newly created Bitbucket repository.
    Finally, it deletes the local clone of the repository.

    Args:
        github_repo_url (str): The URL of the GitHub/GitLab repository to be cloned.
        bitbucket_repo_name (str): The name of the Bitbucket repository to be created.

    Raises:
        Exception: If there is an error during the cloning, repository creation, or pushing process,
                   an exception is raised with the appropriate error message.
    """
    try:
        bitbucket_repo_name = ''.join(c for c in bitbucket_repo_name.lower() if c.isalnum() or c in ['_', '-', '.'])
        repo_dir = os.path.basename(github_repo_url).replace(".git", "") + ".git"
        print(f"Cloning: {github_repo_url}")
        git.Repo.clone_from(github_repo_url, repo_dir, mirror=True)

        print(f"Creating a repo on Bitbucket: {bitbucket_repo_name}")
        bitbucket_api_url = f"https://api.bitbucket.org/2.0/repositories/{BITBUCKET_WORKSPACE}/{bitbucket_repo_name}"
        response = requests.post(
            bitbucket_api_url,
            auth=(BITBUCKET_USER, BITBUCKET_PASS),
            json={"scm": "git", "is_private": True, "project": {"key": BITBUCKET_PROJECT}}
        )

        if response.status_code == 200 or response.status_code == 201:
            print("Repo successfully created on Bitbucket.")
        else:
            raise Exception(f"An error occurred while creating the repo on Bitbucket: {response.text}")

        repo = git.Repo(repo_dir)
        origin = repo.remotes.origin
        new_remote_url = f"https://{BITBUCKET_USER}:{BITBUCKET_PASS}@bitbucket.org/{BITBUCKET_WORKSPACE}/{bitbucket_repo_name}.git"
        origin.set_url(new_remote_url)

        print("All branches and tags are pushed to Bitbucket...")
        repo.git.push('--mirror')

        print(f"Deleting local repo files: {repo_dir}")
        shutil.rmtree(repo_dir)
        print("Local repo files have been deleted successfully.\n")

        time.sleep(5)

    except Exception as e:
        error_message = f"Repo: {github_repo_url}, Error: {str(e)}"
        log_error(error_message)
        print(f"Error occurred: {error_message}")

def fetch_and_save_gitlab_projects(group_id, token):
    """
    Fetches and saves GitLab projects for a given group.
    This function retrieves all projects within a specified GitLab group using the GitLab API.
    It handles pagination to ensure all projects are fetched and returns a list of tuples
    containing the repository path and HTTP URL for each project.
    Args:
        group_id (str): The ID of the GitLab group to fetch projects from.
        token (str): The private token for authenticating with the GitLab API.
    Returns:
        list of tuple: A list of tuples where each tuple contains:
            - repo_path (str): The path of the repository.
            - repo_http_url (str): The HTTP URL of the repository.
    Raises:
        requests.exceptions.RequestException: If there is an issue with the network request.
    """
    GITLAB_API_URL = f"https://gitlab.com/api/v4/groups/{group_id}/projects"
    headers = {'PRIVATE-TOKEN': token}

    per_page = 100 # Maximum number of projects per page
    page = 1 # Initial page number

    projects = [] # List to store project data
    repos_infos = [] # List to store repository path and HTTP URL

    while True:
        response = requests.get(GITLAB_API_URL, headers=headers, params={'per_page': per_page, 'page': page})
        
        if response.status_code == 200:
            data = response.json()
            if not data:
                break 
            projects.extend(data) 
            page += 1
        else:
            print(f"An error occurred while importing projects: {response.status_code}")
            break

    if not projects:
        print(f"No project found in the group {group_id}")

    for project in projects:
        repo_path = project.get('path')
        repo_http_url = project.get('http_url_to_repo')
        repos_infos.append((repo_path, repo_http_url))
    
    return repos_infos

if __name__ == "__main__":
    repoz = fetch_and_save_gitlab_projects(GITLAB_GROUP_ID, GITLAB_TOKEN)
    
    for path, url in repoz:
        sync_repos(url, path)

    print("All repos are synchronized.")