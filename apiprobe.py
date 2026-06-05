import sys
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print(r"""
=====================================================================================
=====================================================================================
   ('-.      _ (`-.                    _ (`-.  _  .-')              .-. .-')    ('-.   
  ( OO ).-. ( (OO  )                  ( (OO  )( \( -O )             \  ( OO ) _(  OO)  
  / . --. /_.`     \ ,-.-')          _.`     \ ,------.  .-'),-----. ;-----.\(,------. 
  | \-.  \(__...--'' |  |OO)   .-') (__...--'' |   /`. '( OO'  .-.  '| .-.  | |  .---' 
.-'-'  |  ||  /  | | |  |  \ _(  OO) |  /  | | |  /  | |/   |  | |  || '-' /_)|  |     
 \| |_.'  ||  |_.' | |  |(_/(,------.|  |_.' | |  |_.' |\_) |  |\|  || .-. `.(|  '--.  
  |  .-.  ||  .___.',|  |_.' '------'|  .___.' |  .  '.'  \ |  | |  || |  \  ||  .--'  
  |  | |  ||  |    (_|  |            |  |      |  |\  \    `'  '-'  '| '--'  /|  `---. 
  `--' `--'`--'      `--'            `--'      `--' '--'     `-----' `------' `------' 
=====================================================================================
=====================================================================================
""")
if len(sys.argv) < 2:
    print(" [!] Error: No URL provided.")
    sys.exit(1)

url = sys.argv[1]
methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]

print(f"\n [!] Probing HTTP Methods for {url}:")
print(" =====================================================")

for method in methods:
    try:
        response = requests.request(method, url, timeout=4, allow_redirects=False)
    except requests.exceptions.SSLError:
        response = requests.request(method, url, timeout=4, allow_redirects=False, verify=False)
        
        if response.status_code == 200:
            status_text = f"\033[92m200 OK\033[0m"
        elif response.status_code in [401, 403]:
            status_text = f"\033[93m{response.status_code}\033[0m"
        else:
            status_text = str(response.status_code)
            
        print(f"     [+] {method:<7} -> STATUS: {status_text} (Size: {len(response.content)})")
        
        
        if response.headers.get('Allow'):
            print(f"         [Header Hint] Allow: {response.headers.get('Allow')}")
            
    except requests.exceptions.RequestException:
        print(f"     [x] {method:<7} -> Connection Failed")

print(" =====================================================")

input("\n [-] Probe finished. Press Enter to close window...")
