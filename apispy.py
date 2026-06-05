import sys
import requests
import os 
import subprocess
import select
import threading
from urllib.parse import urlparse, urlunparse
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from concurrent.futures import ThreadPoolExecutor
print(r"""
=====================================================================
=====================================================================
   ('-.      _ (`-.                    .-')     _ (`-.              
  ( OO ).-. ( (OO  )                  ( OO ).  ( (OO  )             
  / . --. /_.`     \ ,-.-')          (_)---\_)_.`     \  ,--.   ,--.
  | \-.  \(__...--'' |  |OO)   .-')  /    _ |(__...--''   \  `.'  / 
.-'-'  |  ||  /  | | |  |  \ _(  OO) \  :` `. |  /  | | .-')     /  
 \| |_.'  ||  |_.' | |  |(_/(,------. '..`''.)|  |_.' |(OO  \   /   
  |  .-.  ||  .___.',|  |_.' '------'.-._)   \|  .___.' |   /  /\_  
  |  | |  ||  |    (_|  |            \       /|  |      `-./  /.__) 
  `--' `--'`--'      `--'             `-----' `--'        `--'      
=====================================================================
=====================================================================
""");
if len(sys.argv) < 3:
    print(" [!] Usage: python3 script.py <baseUrl> <wordlist> [flags] ")
    print("Flags: --debug: Gives error messages that are hidden by default to keep prompting and scanning output from interrupting eachother.")
    print("--loud: Gives response of every directory and highlighting any results not 404.")
    print("--t<1-150>: Specifies thread count. Note: I added a pretty high thread count, if subscanning and probing are important please use a low thread count.")
    print("--split: Opens subscans in a multiplex terminal (tmux) split-pane.")
    sys.exit(1)

baseUrl = sys.argv[1]
wordlist = sys.argv[2]
flag = sys.argv[3] if len(sys.argv) > 3 else ""
flag1 = sys.argv[4] if len(sys.argv) > 4 else ""
flag2 = sys.argv[5] if len(sys.argv) > 5 else ""
flag3 = sys.argv[6] if len(sys.argv) > 6 else ""
arguments = sys.argv[3:]
thread_flag = next((arg for arg in arguments if arg.startswith("--t")), "")
terminal_lock = threading.Lock()
prompt_lock = threading.Lock()
if thread_flag:
    try:
        thread_count = int(thread_flag[3:])
        if thread_count > 150:
            thread_count = 1
    except ValueError:
        print(f" [!] Invalid thread count in {thread_flag}. Defaulting to 1.")
        thread_count = 1
else:
    thread_count = 1
def check_common_apis(baseUrl, wordlist):
    tempWordlist = ["api", "v1", "v2", "api/v2", "api/v1", "graphql", "rest"]
    print(" [-] Testing Common API endpoints first")
    for endpoint in tempWordlist:
        url = f"{baseUrl.rstrip('/')}/{endpoint.lstrip('/')}"
        check_status(url, wordlist)
    check_wordlist(baseUrl, wordlist)


def check_wordlist(baseUrl, wordlist):
    if not os.path.exists(wordlist):
        print(f" [!] ERR: Wordlist not found at {wordlist}")
        sys.exit(1)
    endpoints = []
    try:
        print(" [+] Starting User Wordlist")
        with open(wordlist, 'r', encoding='UTF-8', errors='ignore') as f:
            for line in f:
                endpoint = line.strip()
                if endpoint:
                    endpoints.append(endpoint.lstrip('/'))
    except Exception as e:
        print(f" [!] Failed to read wordlist! {e}")
    
    clean_base = baseUrl if baseUrl.endswith('/') else baseUrl + '/'
    urls = [f"{clean_base}{endpoint}" for endpoint in endpoints]
    
    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        executor.map(lambda url: check_status(url, wordlist), urls)
def check_status(url, wordlist):
    encode_hash = url
    parsed = urlparse(encode_hash)
    clean_path = parsed.path.replace('//', '/')
    
    url = urlunparse((parsed.scheme, parsed.netloc, clean_path, parsed.params, parsed.query, parsed.fragment))

    try:
        headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0"}
        response = requests.get(url, headers=headers, timeout=5, allow_redirects=False)
    except requests.exceptions.SSLError:
        response = requests.get(url, headers=headers, timeout=5, allow_redirects=False, verify=False)
    except requests.exceptions.RequestException as e:
        if "--debug" in arguments:
            with terminal_lock:
                print(f"[!] {e.__class__.__name__} on {url}: {e}")
        return
    if response.status_code == 200:
        with terminal_lock:
            print(f"\n [+] Url found: {url}")
        with prompt_lock:
            ask_subscan(url, wordlist)
    if response.status_code in [301, 302, 307, 308]:
        with terminal_lock:
            print(
        f"[>] Redirect ({response.status_code}) "
        f"{url} -> {response.headers.get('Location')}"
        )
    elif response.status_code in [401, 403]: 
        with terminal_lock:
            print(f"\n [-] Url found but restricted ({response.status_code}): {url}")
        with prompt_lock:
            ask_subscan(url, wordlist)
    elif "--loud" in arguments:
        with terminal_lock:
            if response.status_code == 404:
                print(f"{url} attempted. HTTP Code: {response.status_code}")
            else:
                print(f"\033[31m {url} attemped. HTTP Code: {response.status_code} \033[0m")
def ask_subscan(url, wordlist, timeout=5):
    sys.stdout.write("\r\033[K") 
    sys.stdout.write(f"    '-> Subscan {url}? (y/n) [Auto-skip in {timeout}s]: ")
    sys.stdout.flush()
    ready, _, _ = select.select([sys.stdin], [], [], timeout)
    if ready:
        choice = sys.stdin.readline().strip().lower()
        if choice in ['y', 'yes']:
            print(" [-] Beginning Subscan, please ensure script is named apispy.py")
            subScanCmd = f"python3 apispy.py {url} {wordlist} {flag} {flag1} {flag2} {flag3}".strip()
            
            if "--split" in arguments:
                try:
                    subprocess.Popen(["tmux", "split-window", "-h", subScanCmd])
                except Exception as e:
                    subScanCmd = f"python3 apispy.py {url} {wordlist}"
                    print(f"\n [!] An error occurred, opening new terminal despite flag: {e}")
                    os.system(f"x-terminal-emulator -e bash -c '{subScanCmd}; exec bash'")

            else:
                os.system(f"x-terminal-emulator -e bash -c '{subScanCmd}; exec bash'")

    else:
        sys.stdout.write("\r\033[K    [-] Timeout: Skipped prompt for " + url + "\n")
        sys.stdout.flush()

    ask_probe(url)

def ask_probe(url, timeout=5):
    sys.stdout.write("\r\033[K") 
    sys.stdout.write(f"    '-> Probe methods on {url}? (y/n) [Auto-skip in {timeout}s]: ")
    sys.stdout.flush()
    
    ready, _, _ = select.select([sys.stdin], [], [], timeout)
    if ready:
        choice = sys.stdin.readline().strip().lower()
        if choice in ['y', 'yes']:
            print(" [-] Beginning probe script, make sure it is saved in same directory with name apiprobe.py")
            probeCmd = f"python3 apiprobe.py {url}"
            

            if "--split" in arguments:
                try:
                    subprocess.Popen(["tmux", "split-window", "-h", probeCmd])
                except Exception as e:
                    print(f"\n [!] An error occurred, opening new terminal despite flag: {e}")
                    os.system(f"x-terminal-emulator -e bash -c '{probeCmd}; exec bash'")

            else:
                os.system(f"x-terminal-emulator -e bash -c '{probeCmd}; exec bash'")

    else:

        with terminal_lock:
            sys.stdout.write("\r\033[K    [-] Timeout: Skipped probing for " + url + "\n")
            sys.stdout.flush()


check_common_apis(baseUrl, wordlist)
