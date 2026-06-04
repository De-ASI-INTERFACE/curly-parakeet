"""$KATCOIN — Holder snapshot tool.
Exports top holders to CSV. Fully iterative.
Creator: Richard Patterson (@De-ASI-INTERFACE)
"""
from __future__ import annotations

import csv
import os
import time
from dotenv import load_dotenv
from solana.rpc.api import Client
from solders.pubkey import Pubkey
from loguru import logger

load_dotenv()

RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
MINT_ADDRESS = os.getenv("KATCOIN_MINT_ADDRESS", "")


def snapshot(mint: str, output_path: str = "snapshot.csv") -> None:
    client = Client(RPC_URL)
    rows: list[dict] = []
    try:
        pubkey = Pubkey.from_string(mint)
        resp = client.get_token_largest_accounts(pubkey)
        for acct in resp.value:
            rows.append({
                "address": str(acct.address),
                "amount_raw": int(acct.amount),
                "amount_kat": acct.ui_amount,
            })
    except Exception as exc:
        logger.error(f"Snapshot failed: {exc}")
        return

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["address", "amount_raw", "amount_kat"])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    logger.info(f"Snapshot saved: {output_path} ({len(rows)} holders)")


if __name__ == "__main__":
    if not MINT_ADDRESS:
        logger.error("KATCOIN_MINT_ADDRESS not set in .env")
    else:
        snapshot(MINT_ADDRESS)
