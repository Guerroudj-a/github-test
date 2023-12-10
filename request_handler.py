import requests
from requests.auth import HTTPProxyAuth

class RequestHandler:
    def __init__(self, socks5_proxy=None, socks5_auth=None):
        self.session = requests.Session()
        self.socks5_proxy = socks5_proxy
        self.socks5_auth = socks5_auth

        if self.socks5_proxy:
            self.session.proxies = {
                "http": self.socks5_proxy,
                "https": self.socks5_proxy
            }

            if self.socks5_auth:
                username, password = self.socks5_auth.split(":")
                self.session.proxies["http"] = f"{username}:{password}@{self.socks5_proxy}"
                self.session.proxies["https"] = f"{username}:{password}@{self.socks5_proxy}"

    def make_request(self, url, headers=None):
        try:
            response = self.session.get(url, headers=headers)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {url}: {e}")
            return None

if __name__ == "__main__":
    # Example usage
    handler = RequestHandler()
    response = handler.make_request("https://www.example.com", headers={"User-Agent": "Mozilla/5.0"})
    if response:
        print(response.text)

