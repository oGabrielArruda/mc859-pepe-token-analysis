import requests
import pandas as pd
import time

# ── Config ────────────────────────────────────────────────────────────────────
DUNE_API_KEY  = "your_free_api_key_here"   # get at dune.com → settings → API
TOKEN_MINT    = "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN"

HEADERS = {"X-Dune-API-Key": DUNE_API_KEY}
BASE_URL = "https://api.dune.com/api/v1"

# ── Time windows ──────────────────────────────────────────────────────────────
WINDOWS = {
    "khamenei": ("2026-02-27 00:00:00", "2026-03-05 23:59:59"),
    "maduro":   ("2026-01-02 00:00:00", "2026-01-07 23:59:59"),  # fill in
    "baseline": ("YYYY-MM-DD 00:00:00", "YYYY-MM-DD 23:59:59"),  # fill in
}

# ── Dune helpers ──────────────────────────────────────────────────────────────
def build_query(start: str, end: str) -> str:
    return f"""
    SELECT
        from_owner   AS source,
        to_owner     AS destination,
        amount,
        block_time   AS block_timestamp,
        tx_id        AS tx_signature
    FROM tokens_solana.transfers
    WHERE token_mint_address = '{TOKEN_MINT}'
      AND block_time >= TIMESTAMP '{start}'
      AND block_time <= TIMESTAMP '{end}'
      AND from_owner IS NOT NULL
      AND to_owner   IS NOT NULL
      AND from_owner != to_owner
      AND amount > 0
    """

def execute_query(sql: str) -> str:
    """Submit query and return execution_id."""
    resp = requests.post(
        f"{BASE_URL}/query/execute",
        headers=HEADERS,
        json={"query_sql": sql},
    )
    resp.raise_for_status()
    execution_id = resp.json()["execution_id"]
    print(f"  Query submitted → execution_id: {execution_id}")
    return execution_id

def wait_for_result(execution_id: str, poll_interval: int = 5) -> pd.DataFrame:
    """Poll until done, then return results as DataFrame."""
    while True:
        resp = requests.get(
            f"{BASE_URL}/execution/{execution_id}/status",
            headers=HEADERS,
        )
        resp.raise_for_status()
        state = resp.json()["state"]
        print(f"  Status: {state}")

        if state == "QUERY_STATE_COMPLETED":
            break
        elif state in ("QUERY_STATE_FAILED", "QUERY_STATE_CANCELLED"):
            raise RuntimeError(f"Query failed with state: {state}")

        time.sleep(poll_interval)

    resp = requests.get(
        f"{BASE_URL}/execution/{execution_id}/results",
        headers=HEADERS,
    )
    resp.raise_for_status()
    rows = resp.json()["result"]["rows"]
    return pd.DataFrame(rows)

# ── Main ──────────────────────────────────────────────────────────────────────
def fetch_window(name: str, start: str, end: str) -> pd.DataFrame:
    print(f"\n[{name}] Fetching {start} → {end}")
    sql = build_query(start, end)
    execution_id = execute_query(sql)
    df = wait_for_result(execution_id)
    print(f"  Rows collected: {len(df):,}")
    df.to_csv(f"data_{name}.csv", index=False)
    print(f"  Saved to data_{name}.csv")
    return df

if __name__ == "__main__":
    for name, (start, end) in WINDOWS.items():
        if "YYYY" in start:
            print(f"\n[{name}] Skipping — fill in the dates first")
            continue
        fetch_window(name, start, end)
