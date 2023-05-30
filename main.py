import requests, random
from os import system, name
from colorama import Fore, Style
from concurrent.futures import ThreadPoolExecutor
from pystyle import Colors, Colorate, Center
from threading import Lock

logo = """
 ██████╗ ██╗   ██╗██╗██╗     ██████╗     ███████╗ ██████╗██████╗  █████╗ ██████╗ ███████╗██████╗ 
██╔════╝ ██║   ██║██║██║     ██╔══██╗    ██╔════╝██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗
██║  ███╗██║   ██║██║██║     ██║  ██║    ███████╗██║     ██████╔╝███████║██████╔╝█████╗  ██████╔╝
██║   ██║██║   ██║██║██║     ██║  ██║    ╚════██║██║     ██╔══██╗██╔══██║██╔═══╝ ██╔══╝  ██╔══██╗
╚██████╔╝╚██████╔╝██║███████╗██████╔╝    ███████║╚██████╗██║  ██║██║  ██║██║     ███████╗██║  ██║
 ╚═════╝  ╚═════╝ ╚═╝╚══════╝╚═════╝     ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝"""

class GuildScraper:
    def __init__(self):
        self.lock = Lock()
        self.tokens = []
        self.total_tokens = 0
        self.checked_tokens = 0
        self.total_guilds = 0
        self.threads = 0

    # Print the logo
    def print_logo(self):
        print(Center.XCenter(Colorate.Vertical(Colors.white_to_blue, logo, 1)))
        print(Center.XCenter(Colorate.Vertical(Colors.white_to_blue, "-----------------------------------------------------------\n\n", 1)))

    # Clear console function
    def clear_console(self):
        system("cls" if name in ("nt", "dos") else "clear")

    # Set a proxy each request
    def set_proxy(self):
        with open("proxies.txt", "r", encoding="utf8", errors="ignore") as proxies_file:
            proxy_list = proxies_file.read().splitlines()
        proxy = random.choice(proxy_list)
        return {'http': f"http://{proxy}", 'https': f'http://{proxy}'}

    # Read tokens from file
    def load_tokens(self):
        with open("tokens.txt", "r", encoding="utf8", errors="ignore") as tokens_file:
            self.tokens = tokens_file.read().splitlines()
            self.total_tokens = len(self.tokens)

    # Process token with ThreadPoolExecutor
    def process_token(self, token):
        session = requests.Session()
        session.proxies = self.set_proxy()

        headers = {
            "Authorization": token,
            "Content-Type": "application/json",
            "Connection": "keep-alive"
        }
        response = session.get("https://discord.com/api/v9/users/@me/guilds", headers=headers).json()

        with self.lock: 
            self.checked_tokens += 1

            if "message" in response:
                error = response["message"]
                if "401" in error:
                    print(f"{Fore.RED}>{Fore.RESET} Invalid Token! ({token})")
                    # Save invalid token
                    with open("invalid.txt", "a", encoding="utf8", errors="ignore") as invalid_file:
                        invalid_file.write(f"{token}\n")
                else:
                    print(f"{Fore.RED}>{Fore.RESET} Unknown Error {error} ({token})")
                    # Save unknown error token
                    with open("unknown.txt", "a", encoding="utf8", errors="ignore") as unknown_file:
                        unknown_file.write(f"{token}\n")
                return

            for guild in response:
                guild_id = guild["id"]
                with open("results.txt", "a", encoding="utf8", errors="ignore") as results_file:
                    results_file.write(f"{guild_id}\n")
                    self.total_guilds += 1
                    print(f"{Fore.GREEN}>{Fore.RESET} Saved guild: {Style.DIM}{Fore.MAGENTA}{guild_id}{Style.RESET_ALL}")

            system(f"title Guild ID Scraper - {self.total_guilds} scraped - {self.checked_tokens}/{self.total_tokens} checked")

    def start(self):
        # Prepare console
        self.clear_console()
        self.print_logo()

        # Load tokens
        self.load_tokens()

        # Ask for threads
        self.threads = int(input(f"{Fore.GREEN}>{Fore.RESET} Threads: "))

        # Start ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            executor.map(self.process_token, self.tokens)

if __name__ == "__main__":
    scraper = GuildScraper()
    scraper.start()
