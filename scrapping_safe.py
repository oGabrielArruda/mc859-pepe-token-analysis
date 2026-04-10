import requests
import pandas as pd
import time

# ── Config ────────────────────────────────────────────────────────────────────
DUNE_API_KEY = "cXhBuc5gwlTGQhCnx4RM3Snyv4eW8rYM" # API
TOKEN_MINT   = "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN"

HEADERS  = {"X-Dune-API-Key": DUNE_API_KEY}
BASE_URL = "https://api.dune.com/api/v1"

# ── Time windows ──────────────────────────────────────────────────────────────
WINDOWS = {
    "khamenei": ("2026-02-27 00:00:00", "2026-03-05 23:59:59"),
    "maduro":   ("2026-01-02 00:00:00", "2026-01-07 23:59:59"),
    "baseline": ("YYYY-MM-DD 00:00:00", "YYYY-MM-DD 23:59:59"),  # fill in
}

# ── Dune helpers ──────────────────────────────────────────────────────────────
def build_query(start: str, end: str) -> str:
    return f"""
    SELECT
        from_owner,
        to_owner,
        amount_display,
        amount_usd,
        block_time,
        tx_id,
        outer_executing_account,
        inner_instruction_index,
        action
    FROM tokens_solana.transfers
    WHERE token_mint_address = '{TOKEN_MINT}'
      AND block_time >= TIMESTAMP '{start}'
      AND block_time <= TIMESTAMP '{end}'
      AND from_owner IS NOT NULL
      AND to_owner   IS NOT NULL
      AND from_owner != to_owner
      AND amount_display > 0
      AND action = 'transfer'
    """

def execute_query(sql: str) -> str:
    # Step 1: create the query
    create_resp = requests.post(
        f"{BASE_URL}/query",
        headers=HEADERS,
        json={"query_sql": sql, "name": "trump-token-fetch", "is_private": True},
    )
    create_resp.raise_for_status()
    query_id = create_resp.json()["query_id"]
    print(f"  Query created → query_id: {query_id}")

    # Step 2: execute it
    exec_resp = requests.post(
        f"{BASE_URL}/query/{query_id}/execute",
        headers=HEADERS,
    )
    exec_resp.raise_for_status()
    execution_id = exec_resp.json()["execution_id"]
    print(f"  Execution started → execution_id: {execution_id}")
    return execution_id

def wait_for_result(execution_id: str, poll_interval: int = 5) -> pd.DataFrame:
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

# ── Safe interactive runner ───────────────────────────────────────────────────
def show_preview(df: pd.DataFrame):
    print("\n── Preview (first 5 rows) ───────────────────────────────────────")
    print(df.head().to_string(index=False))
    print("\n── Stats ────────────────────────────────────────────────────────")
    print(f"  Total rows      : {len(df):,}")
    print(f"  Unique sources  : {df['from_owner'].nunique():,}")
    print(f"  Unique dests    : {df['to_owner'].nunique():,}")
    print(f"  Amount range    : {df['amount_display'].min():.4f} → {df['amount_display'].max():.4f}")
    print(f"  Time range      : {df['block_time'].min()} → {df['block_time'].max()}")
    print("─────────────────────────────────────────────────────────────────\n")

def print_menu():
    print("\n" + "=" * 65)
    print("  TRUMP Token — Safe Interactive Fetcher")
    print("=" * 65)
    print("  Available windows:\n")
    for name, (start, end) in WINDOWS.items():
        status = "[DATES MISSING]" if "YYYY" in start else f"{start[:10]} → {end[:10]}"
        print(f"    {name:<12} {status}")
    print("\n  Commands: <window name> | quit")
    print("=" * 65)

if __name__ == "__main__":
    print_menu()

    while True:
        choice = input("\n  Which window to run? ").strip().lower()

        if choice == "quit":
            print("\nExiting. No more credits spent.")
            break

        if choice not in WINDOWS:
            print(f"  Unknown window '{choice}'. Choose from: {', '.join(WINDOWS)}")
            continue

        start, end = WINDOWS[choice]

        if "YYYY" in start:
            print(f"  [ERROR] Dates for '{choice}' are not filled in yet.")
            continue

        print(f"\n{'=' * 65}")
        print(f"  Window : {choice.upper()}")
        print(f"  From   : {start}")
        print(f"  To     : {end}")
        print(f"{'=' * 65}")

        confirm = input("\n  Confirm and spend credits? (yes / no): ").strip().lower()
        if confirm != "yes":
            print("  Cancelled.")
            continue

        try:
            execution_id = execute_query(build_query(start, end))
            df = wait_for_result(execution_id)
            show_preview(df)

            filename = f"data_{choice}.csv"
            df.to_csv(filename, index=False)
            print(f"  Saved to {filename}")

        except Exception as e:
            print(f"  ERROR: {e}")
