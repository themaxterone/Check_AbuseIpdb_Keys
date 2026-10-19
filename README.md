# AbuseIPDB API Keys Quota Checker (`check_abuseipdb_keys.py`)

A high-performance Python utility to monitor and inspect the real-time usage status, daily limits, and remaining query quotas of multiple **AbuseIPDB API keys** concurrently using thread pools.

---

## Table of Contents

1. [Features](#features)
2. [How It Works](#how-it-works)
3. [Prerequisites & Dependencies](#prerequisites--dependencies)
4. [Installation Guide](#installation-guide)
5. [Configuration](#configuration)
6. [Usage & Execution](#usage--execution)
7. [Output Fields Reference](#output-fields-reference)

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
```
conda install requests
```
   
### Option 2: Using Standard Python (CMD / PowerShell / macOS / Linux)

1. Open your terminal.
2. Install dependencies via pip:

```
pip install requests urllib3
```
---
### Configuration

1. Place check_abuseipdb_keys.py in your working directory.
2. Open the file in an editor (VS Code, Notepad, Vim, etc.).
3. Locate the API_KEYS list near the top of the script and populate it with your keys:

```
API_KEYS = [
    "YOUR_FIRST_API_KEY",
    "YOUR_SECOND_API_KEY",
    "YOUR_THIRD_API_KEY"
]
```
---
## Usage & Execution

Open your terminal or Anaconda Prompt, navigate to the script directory, and execute:

```
python check_abuseipdb_keys.py
```
---
## Terminal Output Example

```
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