# API-SPY 🕵️👻

A powerful directory brute-force tool designed for API reconnaissance and penetration testing. Automatically discovers hidden API endpoints, performs recursive subscanning, and probes HTTP methods for deeper API enumeration.

<img width="1920" height="1047" alt="screenie" src="https://github.com/user-attachments/assets/3ecfba10-8dae-4174-b3db-3d8be198eedd" alt="Debugging on HTB machine WingData" />
<img width="1920" height="1047" alt="work" src="https://github.com/user-attachments/assets/fc370c85-34a5-4df6-a681-78e649be133a" alt="Debugging on HTB machine WingData" />


## Features

✨ **Core Capabilities:**
- 🎯 Fast endpoint discovery using wordlist-based brute-forcing
- 🔄 Automatic recursive subscanning of discovered endpoints
- 🔍 HTTP method probing (GET, POST, PUT, DELETE, PATCH, OPTIONS)
- ⚡ Multi-threaded scanning for improved performance
- 📊 Smart status code handling (200, 401, 403)
- 🔗 Interactive prompts for selective subscanning and probing
- 🕷️ JavaScript scraping for common /api/ endpoints
- 🪟 Terminal multiplexing support (tmux) for parallel operations
- ⏱️ Auto-skip prompts with configurable timeout

## Installation

### Prerequisites
- Python 3.6+
- `requests` library
- `tmux` (optional, for `--split` flag)
- `xfce-terminal` (for Linux desktop environments)

### Setup

```bash
# Clone the repository
git clone https://github.com/austinjump-sec/API-SPY.git
cd API-SPY

# Install dependencies
pip install requests

# Make scripts executable (optional)
chmod +x apispy.py apiprobe.py
```

## Usage

### Basic Syntax

```bash
python3 apispy.py <baseUrl> <wordlist> [OPTIONS]
```

### Required Arguments

| Argument | Description |
|----------|-------------|
| `<baseUrl>` | Target URL (e.g., `http://example.com` or `http://api.example.com`) |
| `<wordlist>` | Path to wordlist file containing endpoints (one per line) |

### Optional Arguments

| Argument | Description |
|----------|-------------|
| `--t<number>` | Thread count (max 150, default: 1) |
| `--split` | Use tmux split-window instead of new terminal windows |
| `--debug` | Shows otherwise hidden error messages |
| ` --loud `  |  Shows all messages, positive and errors, highlighting any that dont return 404|
|` --js`  | Scans for JavaScript files and scrapes any found ones for common hardcoded API endpoints|
### Examples

#### Basic scan with default settings (single-threaded)
```bash
python3 apispy.py http://api.example.com wordlist.txt
```

#### Multi-threaded scan with 10 threads
```bash
python3 apispy.py http://api.example.com wordlist.txt -t10
```

#### Use tmux for parallel operations
```bash
python3 apispy.py http://api.example.com wordlist.txt -t5 --split
```

#### Subscan specific URL with higher thread count
```bash
python3 apispy.py http://api.example.com/v1 wordlist.txt -t20
```

## How It Works

### Phase 1: Common API Endpoint Testing
The tool starts by testing a predefined set of common API paths:
- `api`, `v1`, `v2`, `api/v1`, `api/v2`, `graphql`, `rest`

### Phase 2: Wordlist Brute-Force
- Loads endpoints from your wordlist (ignores comments starting with `#`)
- Tests each endpoint with HTTP GET requests
- Multi-threaded execution for faster scanning
- Identifies responsive endpoints with status codes: `200`, `401`, `403`

### Phase 3: Interactive Subscanning (Optional)
When an endpoint is found, you're prompted:
```
'-> Subscan <url>? (y/n) [Auto-skip in 5s]:
```
- Choose `y/yes` to recursively scan that endpoint with the same wordlist
- Automatically launches in a new terminal or tmux split-window
- Auto-skips after 5 seconds if no input provided

### Phase 4: HTTP Method Probing (Optional)
After subscanning, you're prompted:
```
'-> Probe methods on <url>? (y/n) [Auto-skip in 5s]:
```
- Launches `apiprobe.py` which tests HTTP methods on the discovered endpoint
- Tests: GET, POST, PUT, DELETE, PATCH, OPTIONS
- Color-coded output (green for 200, yellow for auth-related errors)
- Shows response sizes and `Allow` header hints

## Output Interpretation

### API-SPY Main Script
```
[+] Url found: http://api.example.com/v1            ← 200 OK (accessible)
    '-> Subscan http://api.example.com/v1? (y/n) [Auto-skip in 0s]: 
[-] Timeout: Skipped prompt for http://api.example.com/v1?
    '-> Probe methods on http://api.example.com/v1? (y/n) [Auto-skip in 4s]: 
[-] Url found but not permitted (403 ERR): ...      ← Forbidden but exists
[-] Url found but not permitted (401 ERR): ...      ← Requires authentication
```

### API-Probe Script
```
[+] GET     -> STATUS: 200 OK (Size: 1024)
[-] POST    -> STATUS: 405 (Size: 0)
[Header Hint] Allow: GET, HEAD, OPTIONS
```

## Wordlist Format

Create a simple text file with endpoints (one per line):

```
admin
users
api/users
v1/products
v2/customers
/api/v1/auth
/graphql
search
data
config
```

**Note:** Lines starting with `#` are treated as comments and ignored.

## Recommended Wordlists

Popular API wordlists to use with API-SPY:
- [SecLists - API endpoints](https://github.com/danielmiessler/SecLists/tree/master/Discovery/Web-Content/api)
- [Assetnote API wordlist](https://wordlists.assetnote.io/)
- [FuzzDB API routes](https://github.com/fuzzdb-project/fuzzdb/tree/master/discovery/api)

## Performance Tips

### Thread Count Guidelines
- **1-5 threads**: Conservative, less detection risk, slower
- **5-20 threads**: Balanced performance and stealth
- **20-50 threads**: Aggressive scanning, faster results
- **50-150 threads**: Maximum speed (may trigger WAF/IDS)

```bash
# Stealth mode (low threads)
python3 apispy.py http://target.com wordlist.txt -t3

# Balanced mode
python3 apispy.py http://target.com wordlist.txt -t15

# Aggressive mode
python3 apispy.py http://target.com wordlist.txt -t50
```

### Timeout Behavior
- Interactive prompts automatically skip after **5 seconds**
- Useful for unattended scanning of large target lists
- Modify `timeout=5` in source code to customize

## Troubleshooting

### "Wordlist not found"
Ensure the wordlist path is correct and the file exists:
```bash
ls -la /path/to/wordlist.txt
```

### Script named incorrectly error
When subscanning, ensure:
- Main script is named: `apispy.py`
- Probe script is named: `apiprobe.py`
- Both are in the same directory

### tmux split-window not working
If `--split` fails:
- Install tmux: `sudo apt install tmux`
- Ensure you're running in a tmux session: `tmux new-session -s scan`
- Falls back to xfce-terminal automatically

### "Connection Failed" for all endpoints
- Verify the base URL is correct and accessible
- Check firewall/proxy settings
- Ensure the target service is running
- Test manually: `curl http://your-url/`

### No results found
- Verify the wordlist contains relevant endpoints
- Check if the target returns status codes other than 200/401/403
- Try with fewer threads to avoid timeouts
- Increase request timeout in `check_status()` function

## Security Considerations

⚠️ **Legal & Ethical:**
- **Only test systems you own or have explicit written permission to test**
- Unauthorized access to computer systems is illegal in most jurisdictions
- Use API-SPY responsibly for authorized penetration testing and security research
- Respect rate limits and don't perform DoS attacks

### Best Practices

1. **Obtain Authorization**: Get written permission before testing
2. **Use Appropriate Wordlists**: Choose relevant endpoints for your target
3. **Monitor Detection**: Watch for WAF/IDS blocks or account lockouts
4. **Respect Rate Limits**: Use lower thread counts for production systems
5. **Document Findings**: Log all discovered endpoints for reporting

## Advanced Usage

### Custom Timeout Values
Edit the source code to adjust timeout values:
```python
def ask_subscan(url, wordlist, timeout=10):  # Change from 5 to 10 seconds
```

### Filtering Results
Create wordlists targeting specific API paths:
```bash
# Admin endpoints only
grep -i "admin" full-wordlist.txt > admin-wordlist.txt

# v1 API only
grep "v1" full-wordlist.txt > v1-wordlist.txt
```

### Batch Scanning
Scan multiple targets with a loop:
```bash
for target in http://target1.com http://target2.com http://target3.com; do
    python3 apispy.py "$target" wordlist.txt -t10
done
```

## Architecture

### apispy.py (Main Scanner)
- Orchestrates the scanning workflow
- Manages threading and concurrent requests
- Handles interactive prompts and terminal spawning
- Coordinates subscan and probe operations

### apiprobe.py (Method Prober)
- Tests HTTP methods on discovered endpoints
- Reports method availability and status codes
- Extracts hints from HTTP headers
- Provides endpoint capability assessment





## Contributing

Contributions are welcome! Feel free to:
- Report bugs and issues
- Suggest new features
- Improve documentation
- Optimize performance

## Disclaimer

This tool is provided for educational and authorized security testing purposes only. Users are responsible for ensuring they have proper authorization before scanning any systems. Unauthorized access to computer systems is illegal.

## License

This project is provided as-is for security research and authorized testing purposes.

---

**Created by:** austinjump-sec  
**Repository:** [austinjump-sec/API-SPY](https://github.com/austinjump-sec/API-SPY)
