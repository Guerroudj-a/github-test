# dg-hub-recon
# Cyber Reconnaissance Tool

Explore GitHub and DockerHub connections with our Cyber Reconnaissance Tool. This Python script delves into GitHub repositories, extracts commit information, and seamlessly links with DockerHub accounts. Elevate your cybersecurity analysis by exploring GitHub commits and enumerating DockerHub containers associated with users.

## Key Features

- **GitHub Reconnaissance**: Retrieve commit details from public repositories.
- **DockerHub Integration**: Automatically identify DockerHub accounts linked to GitHub commit authors.
- **Container Enumeration**: Explore DockerHub containers associated with users for a comprehensive profile.
- **SOCKS5 Proxy Support**: Enhance privacy during reconnaissance.
- **Customizable Verbosity**: Tailor output levels for your specific needs.
- **JSON Output**: Streamline integration with other security tools.

## Usage

1. **Specify GitHub User or Organization**: Provide the GitHub username or organization name for reconnaissance.
2. **GitHub Access Token (Optional)**: Enhance API access by providing a GitHub access token.
3. **GitHub Reconnaissance**: Retrieve commit details from GitHub repositories.
4. **DockerHub Integration**: Seamlessly link GitHub commits to DockerHub accounts.
5. **Container Enumeration**: Enumerate DockerHub containers to unveil potential security insights.

## Getting Started

```bash
# Single User or Organization
python dg-hub.py -u <GitHubUsername> -t <GitHubAccessToken> -d

# From a File (list of usernames or organizations)
python dg-hub.py -f <UserListFile> -t <GitHubAccessToken> -d
