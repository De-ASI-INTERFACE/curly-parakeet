"""$KATCOIN — On-chain activity monitor.
Polls Solana RPC for token account activity. Fully iterative.
Creator: Richard Patterson (@De-ASI-INTERFACE)
"""
from __future__ import annotations

import os
import time
from collections import deque
from typing import Deque
from dotenv import load_dotenv
from solana.rpc.api import Client
from solders.pubkey import Pubkey
from loguru import logger

load_dotenv()

RPC_URL: str = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
MINT_ADDRESS: str = os.getenv("KATCOIN_MINT_ADDRESS", "")
POLL_INTERVAL: float = 5.0


class ActivityMonitor:
    """Polls Solana for $KATCOIN token account changes."""

    def __init__(self) -> None:
        self.client = Client(RPC_URL)
        self._event_log: Deque[dict] = deque(maxlen=50_000)
        self._running = False

    def fetch_largest_accounts(self, mint: str, limit: int = 20) -> list[dict]:
        """Fetch top token holders — iterative result parsing."""
        accounts: list[dict] = []
        try:
            pubkey = Pubkey.from_string(mint)
            resp = self.client.get_token_largest_accounts(pubkey)
            for acct in resp.value:
                accounts.append({
                    "address": str(acct.address),
                    "amount": int(acct.amount),
                    "ui_amount": acct.ui_amount,
                })
                if len(accounts) >= limit:
                    break
        except Exception as exc:
            logger.error(f"Fetch largest accounts failed: {exc}")
        return accounts

    def run_once(self, mint: str) -> list[dict]:
        accounts = self.fetch_largest_accounts(mint)
        ts = time.time()
        for acct in accounts:
            self._event_log.append({**acct, "ts": ts})
        logger.info(f"Polled {len(accounts)} top holders at {ts:.0f}")
        return accounts

    def start_polling(self, mint: str, interval: float = POLL_INTERVAL) -> None:
        """Continuous iterative poll loop."""
        self._running = True
        logger.info(f"Starting $KATCOIN activity monitor (interval={interval}s)")
        while self._running:
            self.run_once(mint)
            time.sleep(interval)

    def stop(self) -> None:
        self._running = False


if __name__ == "__main__":
    if not MINT_ADDRESS:
        logger.error("KATCOIN_MINT_ADDRESS not set in .env")
    else:
        monitor = ActivityMonitor()
        monitor.start_polling(MINT_ADDRESS)
