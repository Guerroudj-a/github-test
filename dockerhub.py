import json
import argparse
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

class DockerHubReconnaissance:
    def __init__(self, username, output_file=None, socks5_proxy=None, socks5_auth=None):
        self.username = username
        self.output_file = output_file
        self.request_handler = RequestHandler(socks5_proxy, socks5_auth)

    def get_dockerhub_profile(self, username):
        try:
            url = f'https://hub.docker.com/v2/users/{username}'
            response = self.request_handler.make_request(url)
            if response:
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    return None
            return None
        except Exception as e:
            print(f"Error fetching DockerHub profile for {username}: {e}")
            return None

    def get_dockerhub_containers(self, username):
        try:
            profile_data = self.get_dockerhub_profile(username.strip())
            if profile_data:
                user_id = profile_data['username'].replace("_","").replace("-","").replace(".","")
                url = "https://hub.docker.com/v2/repositories/{}?page_size=50&ordering=last_updated".format(user_id)
                response = self.request_handler.make_request(url)
                if response:
                    if response.status_code == 404:
                        return None
                    return response.json()
            return None
        except Exception as e:
            print(f"Error fetching DockerHub containers for {username}: {e}")
            return None

    def save_to_json(self, data):
        if self.output_file:
            with open(self.output_file, 'w') as json_file:
                json.dump(data, json_file, indent=2)
                print(f"\nDockerHub Output saved to {self.output_file}")

    def run_reconnaissance(self):
        profile_data = self.get_dockerhub_profile(self.username)

        if profile_data:
            print(f"      [*] DockerHub Profile found: {profile_data.get('username', 'N/A')}")
            containers = self.get_dockerhub_containers(self.username)

            if containers:
                num_repositories = containers.get('count', 0)
                print(f"      [*] Number of DockerHub repositories: {num_repositories}")

                for container in containers.get('results', []):
                    if container !=[]:
                        print("          - Container: {}{}{}".format(bcolors.OKGREEN, container.get('name', 'N/A'), bcolors.ENDC))
            else:
                print("\tError fetching DockerHub containers.")
        else:
            print("        No DockerHub Profile found.")

def main():
    parser = argparse.ArgumentParser(description="DockerHub Reconnaissance Script")
    parser.add_argument("-u", "--username", help="DockerHub username or organization name")
    parser.add_argument("-o", "--output", help="Output file in JSON format")
    parser.add_argument("-s", "--socks5-proxy", help="SOCKS5 proxy URL (e.g., socks5://proxy_host:proxy_port)")
    parser.add_argument("-a", "--socks5-auth", help="SOCKS5 proxy authentication (format: username:password)")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-f", "--file", help="File containing a list of DockerHub usernames or organization names")
    group.add_argument("-l", "--single", action="store_true", help="Specify a single DockerHub username or organization name")

    args = parser.parse_args()

    if args.single:
        reconnaissance = DockerHubReconnaissance(username=args.username, output_file=args.output,
                                                socks5_proxy=args.socks5_proxy, socks5_auth=args.socks5_auth)
        reconnaissance.run_reconnaissance()
    elif args.file:
        with open(args.file, 'r') as file:
            for line in file:
                username = line.strip()
                reconnaissance = DockerHubReconnaissance(username=username, output_file=args.output,
                                                        socks5_proxy=args.socks5_proxy, socks5_auth=args.socks5_auth)
                reconnaissance.run_reconnaissance()

if __name__ == "__main__":
    main()

