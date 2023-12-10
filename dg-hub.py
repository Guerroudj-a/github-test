import json
import requests
import argparse
from dockerhub import DockerHubReconnaissance
from request_handler import RequestHandler

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class GitHubReconnaissance:
    def __init__(self, username, token, output_file=None, socks5_proxy=None, socks5_auth=None, verbose=0, check_docker=None, page_limit=1):
        self.username = username
        self.token = token
        self.verbose = verbose
        self.output_file = output_file
        self.request_handler = RequestHandler(socks5_proxy, socks5_auth)
        self.checked_github_users = set()
        self.checked_dockerhub_users = set()
        self.checked_commit_usernames = set()
        self.common_email_addreses = []
        self.check_dockerhub = check_docker
        self.page_limit = page_limit

    def get_public_repositories(self):
        try:
            url = f'https://api.github.com/users/{self.username}/repos'
            headers = {'Authorization': f'token {self.token}'} if self.token else {}
            response = self.request_handler.make_request(url, headers=headers)
            return response.json() if response else []
        except Exception as e:
            if self.verbose > 1:
                print("Error fetching public repositories: {}{}{}".format(bcolors.WARNING, e, bcolors.ENDC))
            return []

    def get_commits(self, repository):
        try:
            url = f'https://api.github.com/repos/{self.username}/{repository}/commits'
            headers = {'Authorization': f'token {self.token}'} if self.token else {}
            response = self.request_handler.make_request(url, headers=headers)
            limit = self.page_limit
            count = 0

            if response and response.status_code == 200:
                commits = response.json()

                # Check for pagination
                while 'Link' in response.headers and 'rel="next"' in response.headers['Link'] and count < limit:
                    next_page_url = response.links['next']['url']
                    response = self.request_handler.make_request(next_page_url, headers=headers)
                    commits.extend(response.json())
                    count += 1

                if self.verbose > 0:
                    print("  Total Commits for {}: {}{}{}".format(repository, bcolors.OKGREEN, len(commits), bcolors.ENDC))

                return commits
            else:
                if self.verbose > 1:
                    print("Error fetching commits for repository {}: Status Code: {}{}{}".format(repository, bcolors.WARNING, response.status_code, bcolors.ENDC))
                return []
        except Exception as e:
            if self.verbose > 1:
                print("Error fetching commits for repository {}: {}{}{}".format(repository, bcolors.WARNING, e, bcolors.ENDC))
            return []

    def get_dockerhub_profile(self, username):
        # Placeholder for DockerHub reconnaissance
        pass

    def get_dockerhub_containers(self, username):
        # Placeholder for DockerHub reconnaissance
        pass

    def save_to_json(self, data):
        if self.output_file:
            with open(self.output_file, 'w') as json_file:
                json.dump(data, json_file, indent=2)
                print("GitHub Output saved to {}{}{}".format(bcolors.OKGREEN, self.output_file, bcolors.ENDC))

    def process_commit(self, commit):
        try:
            author_username = None
            if commit and 'author' in commit and commit['author']['type'] == "User":
                author_username = commit['author']['login'].strip()
            elif commit and 'commit' in commit and 'author' in commit['commit'] and commit['commit']['author']:
                author_email = commit['commit']['author']['email'].split('@')[0]
                if "+" in author_email:
                    author_username = author_email.split("+")[1].strip()

            if author_username:
                if author_username in self.checked_commit_usernames:
                    return
                self.checked_commit_usernames.add(author_username)

                print("\n  {} : {}{}{}.".format("Author", bcolors.OKGREEN, author_username, bcolors.ENDC))
                if self.verbose > 1:
                    print("    {} : {}{}{}.".format("Name", bcolors.OKGREEN, commit['commit']['author']['name'].strip(), bcolors.ENDC))
                    print("    {} : {}{}{}.".format("Email", bcolors.OKGREEN, commit['commit']['author']['email'].strip(), bcolors.ENDC))

                if self.check_dockerhub:
                    print("    - Checking DockerHub:")
                    dockerhub_recon = DockerHubReconnaissance(username=author_username, output_file=None,
                                                              socks5_proxy=None, socks5_auth=None)
                    dockerhub_recon.run_reconnaissance()
        except Exception as e:
            print("  Error processing commit: {}{}{}".format(bcolors.WARNING, e, bcolors.ENDC))

    def run_reconnaissance(self):
        repositories = self.get_public_repositories()
        output_data = {'repositories': []}

        for repo in repositories:
            repo_data = {'name': repo['name'], 'commits': []}

            if repo['fork']:
                print("Repository: {} - {}Forked{}".format(repo['name'], bcolors.WARNING, bcolors.ENDC))
            else:
                print("\nRepository: {}{}{}".format(bcolors.OKGREEN, repo['name'], bcolors.ENDC))
                commits = self.get_commits(repo['name'])
                for commit in commits:
                    self.process_commit(commit)

                output_data['repositories'].append(repo_data)
                print("\n")

        self.save_to_json(output_data)

def main():
    parser = argparse.ArgumentParser(description="GitHub Reconnaissance Script")
    parser.add_argument("-u", "--username", help="GitHub username or organization name")
    parser.add_argument("-t", "--token", help="GitHub access token")
    parser.add_argument("-o", "--output", help="Output file in JSON format")
    parser.add_argument("-s", "--socks5-proxy", help="SOCKS5 proxy URL (e.g., socks5://proxy_host:proxy_port)")
    parser.add_argument("-a", "--socks5-auth", help="SOCKS5 proxy authentication (format: username:password)")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="Increase output verbosity (e.g., -v or -vvvv)")
    parser.add_argument("-f", "--file", help="File containing a list of GitHub usernames or organization names")
    parser.add_argument("-l", "--single", action="store_true", help="Specify a single GitHub username or organization name")
    parser.add_argument("-d", "--dockerhub", action="store_true", help="Enumerate DockerHub Accounts")
    parser.add_argument("-p", "--page-limit", type=int, default=1, help="Limit the number of pages for commits")

    args = parser.parse_args()

    if args.single:
        reconnaissance = GitHubReconnaissance(username=args.username, token=args.token, output_file=args.output,
                                               socks5_proxy=args.socks5_proxy, socks5_auth=args.socks5_auth,
                                               verbose=args.verbose, check_docker=args.dockerhub, page_limit=args.page_limit)
        reconnaissance.run_reconnaissance()
    elif args.file:
        with open(args.file, 'r') as file:
            for line in file:
                username = line.strip()
                reconnaissance = GitHubReconnaissance(username=username, token=args.token, output_file=args.output,
                                                       socks5_proxy=args.socks5_proxy, socks5_auth=args.socks5_auth,
                                                       verbose=args.verbose, check_docker=args.dockerhub,
                                                       page_limit=args.page_limit)
                reconnaissance.run_reconnaissance()
    else:
        reconnaissance = GitHubReconnaissance(username=args.username, token=args.token, output_file=args.output,
                                               socks5_proxy=args.socks5_proxy, socks5_auth=args.socks5_auth,
                                               verbose=args.verbose, check_docker=args.dockerhub,
                                               page_limit=args.page_limit)
        reconnaissance.run_reconnaissance()

if __name__ == "__main__":
    main()

