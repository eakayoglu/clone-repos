# clone-repos

# Repository Synchronization Script

This script synchronizes repositories from GitLab to Bitbucket.
This script clones all repositories under the specified group ID in Gitlab and their branches. 
A new private repository is created in Bitbucket for each cloned repository.

## Prerequisites

Ensure you have the following installed:
- Python 3.x
- pip (Python package installer)

## Installation

1. Clone the repository:
    ```sh
    git clone <repository_url>
    cd <repository_directory>
    ```

2. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

3. Create a `.env` file in the root directory of the project and add the following environment variables:
    ```env
    GITLAB_GROUP_ID=<your_gitlab_group_id>
    GITLAB_TOKEN=<your_gitlab_token>
    BITBUCKET_USER=<your_bitbucket_username>
    BITBUCKET_PASS=<your_bitbucket_app_password>
    BITBUCKET_WORKSPACE=<your_bitbucket_workspace_id>
    BITBUCKET_PROJECT=<your_bitbucket_project_key>
    ```

## Usage

Run the script to synchronize repositories:
```sh
python main.py
```

## Functions

### log_error(error_message)
Logs error messages to a file named `error.txt` in the current working directory.

### sync_repos(github_repo_url, bitbucket_repo_name)
Synchronizes a GitHub/GitLab repository to a Bitbucket repository.

### fetch_and_save_gitlab_projects(group_id, token)
Fetches and returns the list of projects from a GitLab group.

## License

This project is licensed under the MIT License.