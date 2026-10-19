# AbuseIPDB API Keys Quota Checker (`check_abuseipdb_keys.py`)

A high-performance Python utility to monitor and inspect the real-time usage status, daily limits, and remaining query quotas of multiple **AbuseIPDB API keys** concurrently using thread pools.

---

## Table of Contents

1. [Features](#features)
2. [How It Works](#how-it-works)
3. [Prerequisites & Dependencies](#prerequisites--dependencies)
4. [Installation Guide](#installation-guide)
   - [Option 1: Using Anaconda (Recommended)](#option-1-using-anaconda-recommended)
   - [Option 2: Using Standard Python (CMD / PowerShell / macOS / Linux)](#option-2-using-standard-python-cmd--powershell--macos--linux)
5. [Configuration](#configuration)
6. [Workflow](#workflow)
7. [Usage & Execution](#usage--execution)
8. [Output Fields Reference](#output-fields-reference)
9. [Corporate Proxy & SSL Troubleshooting](#corporate-proxy--ssl-troubleshooting)

---

## Features

- **Concurrent Multi-Key Checks**: Uses Python's `concurrent.futures.ThreadPoolExecutor` to query the status of multiple API keys in parallel, returning results in seconds.
- **Quota & Rate Limit Metrics**: Inspects HTTP response headers to extract daily limits (`X-RateLimit-Limit`), remaining requests (`X-RateLimit-Remaining`), and the exact reset time (`X-RateLimit-Reset`).
- **Aggregated Capacity Pool**: Calculates the total remaining queries across all functional keys.
- **Key Masking**: Automatically masks key strings in terminal output (e.g., `4c9a12...98f1`) to protect credentials from unintended disclosure.
- **Proxy and Corporate Network Resilient**: Preconfigured to handle corporate SSL decryption environments without raising certificate verification errors.

---

## How It Works

1. **Lightweight Probe**: Sends a minimal check request against AbuseIPDB's `/check` endpoint targeting a public resolver (`1.1.1.1`).
2. **HTTP Header Inspection**: Parses standard rate-limiting headers returned by AbuseIPDB:
   - `X-RateLimit-Limit`: Daily request allowance (e.g., 1000 requests/day on standard free tier).
   - `X-RateLimit-Remaining`: Number of requests left for the current 24-hour cycle.
   - `X-RateLimit-Reset`: UNIX timestamp representing when the quota resets.
3. **Status Assessment**:
   - **Active (Green/Yellow)**: Valid key with available requests.
   - **Exhausted (Red, HTTP 429)**: Quota exhausted for the current cycle.
   - **Unauthorized (Red, HTTP 401)**: Invalid, revoked, or mistyped API key.
4. **Console Dashboard**: Renders a formatted table sorting keys by their original index and shows the total available query pool at the bottom.

---

## Prerequisites & Dependencies

- Python 3.8+ (Standard Python or Anaconda/Miniconda)
- Active API keys from [AbuseIPDB](https://www.abuseipdb.com/)
- Required Python libraries:
  - `requests`
  - `urllib3`

---

## Installation Guide

### Option 1: Using Anaconda (Recommended)

1. Open **Anaconda Prompt**.
2. Install the required network libraries:
   ```bash
   conda install requests
   ```
   *(Confirm with `y` if prompted)*.

### Option 2: Using Standard Python (CMD / PowerShell / macOS / Linux)

1. Open your terminal.
2. Install dependencies via `pip`:
   ```bash
   pip install requests urllib3
   ```

---

## Configuration

1. Place `check_abuseipdb_keys.py` in your working directory.
2. Open the file in an editor (VS Code, Notepad, Vim, etc.).
3. Locate the `API_KEYS` list near the top of the script and populate it with your keys:
   ```python
   API_KEYS = [
       "YOUR_FIRST_API_KEY",
       "YOUR_SECOND_API_KEY",
       "YOUR_THIRD_API_KEY"
   ]
   ```
4. Save the file.

---

## Workflow

```text
[Start Execution]
       │
       ▼
[Load API_KEYS list]
       │
       ▼
[ThreadPoolExecutor launches worker threads]
       │
       ├─► Worker 1: Query AbuseIPDB /check (1.1.1.1) with Key #1
       ├─► Worker 2: Query AbuseIPDB /check (1.1.1.1) with Key #2
       └─► Worker N: Query AbuseIPDB /check (1.1.1.1) with Key #N
       │
       ▼
[Parse HTTP Response Headers]
  ├── X-RateLimit-Limit
  ├── X-RateLimit-Remaining
  └── X-RateLimit-Reset
       │
       ▼
[Determine Key State: Active | Exhausted (429) | Unauthorized (401)]
       │
       ▼
[Sort & Render Color-Coded Summary Table in Terminal]
       │
       ▼
[Compute & Display Total Remaining Query Pool]
```

---

## Usage & Execution

Open your terminal or Anaconda Prompt, navigate to the script directory, and execute:

```bash
python check_abuseipdb_keys.py
```

### Terminal Output Example

```plaintext
[+] Checking API keys status concurrently against AbuseIPDB...

=========================================================================================================
#    | Key (Masked)     | Status             | Limit    | Remaining  | Used %   | Reset Time (UTC)       
=========================================================================================================
1    | 4c9a12...98f1    | Active             | 1000     | 842        | 15.8%    | 2026-10-20 00:00:00 UTC
2    | e10bf4...a12c    | Active             | 1000     | 990        | 1.0%     | 2026-10-20 00:00:00 UTC
3    | f038de...51ab    | Exhausted (429)    | 1000     | 0          | 100.0%   | 2026-10-20 00:00:00 UTC
=========================================================================================================
 TOTAL AVAILABLE POOL: 1832 / 3000 queries remaining across all keys.
```

---

## Output Fields Reference

| Column Header | Description |
| :--- | :--- |
| **`#`** | Sequential order of the key matching the `API_KEYS` list index. |
| **`Key (Masked)`** | Partial key preview (first 6 and last 4 characters) to prevent secret exposure. |
| **`Status`** | Operational status: `Active`, `Exhausted (429)`, or `Unauthorized (401)`. |
| **`Limit`** | Maximum daily queries allowed under the key's account tier. |
| **`Remaining`** | Unused requests available before reaching the rate limit. |
| **`Used %`** | Percentage of the daily quota already consumed. |
| **`Reset Time (UTC)`** | Exact UTC timestamp when AbuseIPDB resets the daily quota counter. |
| **`TOTAL AVAILABLE POOL`** | Aggregate sum of all remaining queries across functional keys. |

---

## Corporate Proxy & SSL Troubleshooting

When executing this script in corporate environments with SSL/TLS inspection, standard Python HTTPS calls can trigger certificate verification failures:

```text
SSLError(SSLCertVerificationError: certificate verify failed: self-signed certificate in certificate chain)
```

The script natively handles this behavior by:
1. Disabling insecure request warnings:
   ```python
   import urllib3
   urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
   ```
2. Setting `verify=False` within outbound API requests:
   ```python
   requests.get(url, headers=headers, params=params, timeout=10, verify=False)
   ```