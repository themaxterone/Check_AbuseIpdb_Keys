import concurrent.futures
from datetime import datetime, timezone
import requests
import urllib3

# Suppress SSL warnings in corporate proxy environments
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================================
# DEFINE YOUR LIST OF ABUSEIPDB API KEYS
# ==========================================
API_KEYS = [
    "YOUR_API_KEY_1",
    "YOUR_API_KEY_2",
    "YOUR_API_KEY_3"
]

def check_key_status(key_index, api_key):
    """Checks rate limits for a specific API key using a lightweight query."""
    url = "https://api.abuseipdb.com/api/v2/check"
    headers = {
        "Accept": "application/json",
        "Key": api_key.strip()
    }
    # Lightweight check against a public resolver
    params = {
        "ipAddress": "1.1.1.1",
        "maxAgeInDays": "1"
    }

    masked_key = f"{api_key[:6]}...{api_key[-4:]}" if len(api_key) > 10 else api_key

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10, verify=False)
        
        limit = response.headers.get("X-RateLimit-Limit")
        remaining = response.headers.get("X-RateLimit-Remaining")
        reset_ts = response.headers.get("X-RateLimit-Reset")

        reset_str = "N/A"
        if reset_ts and reset_ts.isdigit():
            reset_dt = datetime.fromtimestamp(int(reset_ts), tz=timezone.utc)
            reset_str = reset_dt.strftime("%Y-%m-%d %H:%M:%S UTC")

        if response.status_code == 200:
            limit_val = int(limit) if limit and limit.isdigit() else 1000
            rem_val = int(remaining) if remaining and remaining.isdigit() else 0
            used = limit_val - rem_val
            usage_pct = (used / limit_val) * 100 if limit_val > 0 else 0

            return {
                "index": key_index,
                "key": masked_key,
                "status": "Active",
                "limit": limit_val,
                "remaining": rem_val,
                "used_pct": f"{usage_pct:.1f}%",
                "reset": reset_str,
                "color": "\033[92m" if rem_val > 100 else "\033[93m"
            }

        elif response.status_code == 429:
            return {
                "index": key_index,
                "key": masked_key,
                "status": "Exhausted (429)",
                "limit": limit or "1000",
                "remaining": 0,
                "used_pct": "100.0%",
                "reset": reset_str,
                "color": "\033[91m"
            }

        elif response.status_code == 401:
            return {
                "index": key_index,
                "key": masked_key,
                "status": "Unauthorized (401)",
                "limit": "-",
                "remaining": "-",
                "used_pct": "-",
                "reset": "-",
                "color": "\033[91m"
            }

        else:
            return {
                "index": key_index,
                "key": masked_key,
                "status": f"HTTP {response.status_code}",
                "limit": "-",
                "remaining": "-",
                "used_pct": "-",
                "reset": "-",
                "color": "\033[91m"
            }

    except Exception as e:
        return {
            "index": key_index,
            "key": masked_key,
            "status": f"Error: {type(e).__name__}",
            "limit": "-",
            "remaining": "-",
            "used_pct": "-",
            "reset": "-",
            "color": "\033[91m"
        }

def main():
    print("\n[+] Checking API keys status concurrently against AbuseIPDB...\n")

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_key = {
            executor.submit(check_key_status, idx, key): idx 
            for idx, key in enumerate(API_KEYS, start=1)
        }
        for future in concurrent.futures.as_completed(future_to_key):
            results.append(future.result())

    # Sort results to maintain the original list order
    results.sort(key=lambda x: x["index"])

    # Output formatting for the terminal table
    reset_color = "\033[0m"
    header_fmt = "{:<4} | {:<16} | {:<18} | {:<8} | {:<10} | {:<8} | {:<23}"
    row_fmt    = "{:<4} | {:<16} | {}{:<18}{} | {:<8} | {:<10} | {:<8} | {:<23}"

    print("=" * 105)
    print(header_fmt.format("#", "Key (Masked)", "Status", "Limit", "Remaining", "Used %", "Reset Time (UTC)"))
    print("=" * 105)

    total_remaining = 0
    total_limit = 0

    for r in results:
        print(row_fmt.format(
            r["index"],
            r["key"],
            r["color"], r["status"], reset_color,
            str(r["limit"]),
            str(r["remaining"]),
            str(r["used_pct"]),
            str(r["reset"])
        ))
        if isinstance(r["remaining"], int) and isinstance(r["limit"], int):
            total_remaining += r["remaining"]
            total_limit += r["limit"]

    print("=" * 105)
    print(f" TOTAL AVAILABLE POOL: {total_remaining} / {total_limit} queries remaining across all keys.\n")

if __name__ == "__main__":
    main()