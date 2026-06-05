import sys
import requests
import os 
import subprocess
import select
import threading

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
    print(" [!] Usage: python3 script.py <baseUrl> <wordlist> [-t<thread-count> --split (to open subprocess in same terminal when subscanning/probing)] ")
    print("Brackets are optional flags, not syntax")
    sys.exit(1)

baseUrl = sys.argv[1]
wordlist = sys.argv[2]
flag = sys.argv[3] if len(sys.argv) > 3 else ""
flag1 = sys.argv[4] if len(sys.argv) > 4 else ""
arguments = sys.argv[3:]
thread_flag = next((arg for arg in arguments if arg.startswith("-t")), "")
terminal_lock = threading.Lock()
prompt_lock = threading.Lock()
if thread_flag:
    try:
        thread_count = int(thread_flag[2:])
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
        url = f"{baseUrl}/{endpoint}"
        check_status(url, wordlist)
    check_wordlist(baseUrl, wordlist)

def check_wordlist(baseUrl, wordlist):
    if not os.path.exists(wordlist):
        print(f" [!] ERR: Wordlist not found at {wordlist}")
        sys.exit(1)
    endpoints = []
    try:
        with open(wordlist, 'r', encoding='UTF-8', errors='ignore') as f:
            for line in f:
                endpoint = line.strip()
                if endpoint and not endpoint.startswith('#'):
                    endpoints.append(endpoint)
    except Exception as e:
        print(f" [!] Failed to read wordlist! {e}")
    urls = [f"{baseUrl}/{endpoint}" for endpoint in endpoints]
    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        executor.map(lambda url: check_status(url, wordlist), urls)
def check_status(url, wordlist):
    try:
        response = requests.get(f"{url}")
        if response.status_code == 200:
            with terminal_lock:
                print(f"\n [+] Url found: {url}")
            with prompt_lock:
                ask_subscan(url, wordlist)
        elif response.status_code == 403: 
            with terminal_lock:
                print(f"\n [-] Url found but not permitted (403 ERR): {url}")
            with prompt_lock:
                ask_subscan(url, wordlist)
        elif response.status_code == 401: 
            with terminal_lock:
                print(f"\n [-] Url found but not permitted (401 ERR): {url}")
            with prompt_lock:
                ask_subscan(url, wordlist)
    except requests.exceptions.RequestException:
            pass

def ask_subscan(url, wordlist, timeout=5):
    sys.stdout.write("\r\033[K") 
    sys.stdout.write(f"    '-> Subscan {url}? (y/n) [Auto-skip in {timeout}s]: ")
    sys.stdout.flush()
    ready, _, _ = select.select([sys.stdin], [], [], timeout)
    if ready:
        choice = sys.stdin.readline().strip().lower()
        if choice in ['y', 'yes']:
            print(" [-] Beginning Subscan, please ensure script is named apispy.py")
            subScanCmd = f"python3 apispy.py {url} {wordlist}"
            
            if flag == "--split" or flag1 == "--split":
                subScanCmd = f"python3 apispy.py {url} {wordlist} --split"
                try:
                    subprocess.Popen(["tmux", "split-window", "-h", subScanCmd])
                    ask_probe(url)
                except Exception as e:
                    subScanCmd = f"python3 apispy.py {url} {wordlist}"
                    print(f"\n [!] An error occurred, opening new terminal despite flag: {e}")
                    os.system(f"gnome-terminal -- bash -c '{subScanCmd}; exec bash'")
                    ask_probe(url)
            else:
                os.system(f"gnome-terminal -- bash -c '{subScanCmd}; exec bash'")
                ask_probe(url)
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
            

            if flag == "--split" or flag1 == "--split" or "--split" in arguments:
                try:
                    subprocess.Popen(["tmux", "split-window", "-h", probeCmd])
                except Exception as e:
                    print(f"\n [!] An error occurred, opening new terminal despite flag: {e}")
                    os.system(f"gnome-terminal -- bash -c '{probeCmd}'")
            else:
                os.system(f"gnome-terminal -- bash -c '{probeCmd}'")
    else:

        with terminal_lock:
            sys.stdout.write("\r\033[K    [-] Timeout: Skipped probing for " + url + "\n")
            sys.stdout.flush()


check_common_apis(baseUrl, wordlist)
