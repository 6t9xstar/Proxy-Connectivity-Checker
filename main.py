import requests
import threading
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, Style, init

init(autoreset=True)

# ================== CONFIG ==================
TEST_URL = "https://httpbin.org/ip"
TIMEOUT = 12
MAX_THREADS = 40
# ============================================

lock = threading.Lock()
results = {
    "LIVE": 0,
    "DEAD": 0
}

BANNER = f"""
{Fore.RED}▄█▀▀▀▄  ▄█▀▀▀▄  ▄█▀▀▀▄
{Fore.RED}█▀   ▀  █▀   ▀  █▀   ▀
{Fore.RED}█        █        █
{Fore.RED}█▄   ▄▀  █▄   ▄▀  █▄   ▄▀
{Fore.RED}▀█▄▄▄█▀  ▀█▄▄▄█▀  ▀█▄▄▄█▀
{Style.DIM}All Proxy Connectivity Tester
"""

print(BANNER)


def load_proxies(file="proxies.txt"):
    with open(file, "r", encoding="utf-8") as f:
        proxies = [line.strip() for line in f if line.strip()]
    if not proxies:
        raise ValueError("Proxy list is empty")
    return proxies


def build_proxy_dict(proxy_url):
    return {
        "http": proxy_url,
        "https": proxy_url
    }


def test_proxy(proxy):
    try:
        parsed = urlparse(proxy)
        if not parsed.scheme:
            raise ValueError("Missing proxy scheme")

        proxy_dict = build_proxy_dict(proxy)

        r = requests.get(
            TEST_URL,
            proxies=proxy_dict,
            timeout=TIMEOUT
        )

        if r.status_code == 200:
            with lock:
                results["LIVE"] += 1
            print(Fore.GREEN + f"[LIVE] {proxy}")
        else:
            raise Exception("Bad response")

    except Exception:
        with lock:
            results["DEAD"] += 1
        print(Fore.RED + f"[DEAD] {proxy}")


def main():
    try:
        proxies = load_proxies()
    except Exception as e:
        print(Fore.RED + f"[ERROR] {e}")
        return

    print(Fore.CYAN + f"[INFO] Loaded {len(proxies)} proxies")
    print(Fore.CYAN + f"[INFO] Threads: {MAX_THREADS}\n")

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.map(test_proxy, proxies)

    print("\n" + Fore.YELLOW + "===== SUMMARY =====")
    print(Fore.GREEN + f"LIVE : {results['LIVE']}")
    print(Fore.RED + f"DEAD : {results['DEAD']}")


if __name__ == "__main__":
    main()
