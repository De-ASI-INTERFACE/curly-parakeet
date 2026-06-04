"""$KATCOIN — Iterative batch SPL token transfer engine.
Processes transfer queue with deque. Zero recursion.
Creator: Richard Patterson (@De-ASI-INTERFACE)
"""
from __future__ import annotations

import os
import time
from collections import deque
from dataclasses import dataclass
from typing import Deque
from dotenv import load_dotenv
from solana.rpc.api import Client
from solders.pubkey import Pubkey
from loguru import logger

load_dotenv()

RPC_URL: str = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")


@dataclass
class TransferJob:
    recipient: str
    amount_raw: int
    memo: str = ""
    created_at: float = 0.0

    def __post_init__(self) -> None:
        self.created_at = time.time()


class BatchTransferEngine:
    """Queue-based SPL transfer engine. All processing iterative."""

    def __init__(self, rpc_url: str = RPC_URL) -> None:
        self._queue: Deque[TransferJob] = deque()
        self._completed: Deque[dict] = deque(maxlen=10_000)
        self._failed: Deque[dict] = deque(maxlen=1_000)
        self.client = Client(rpc_url)

    def enqueue(self, recipient: str, amount_raw: int, memo: str = "") -> None:
        job = TransferJob(recipient=recipient, amount_raw=amount_raw, memo=memo)
        self._queue.append(job)
        logger.info(f"Queued transfer: {amount_raw} KAT → {recipient}")

    def process_all(self) -> dict:
        """Process all queued transfers iteratively."""
        success_count = 0
        fail_count = 0
        while self._queue:
            job = self._queue.popleft()
            try:
                # Validate recipient address
                Pubkey.from_string(job.recipient)
                self._completed.append({
                    "recipient": job.recipient,
                    "amount": job.amount_raw,
                    "ts": time.time(),
                })
                success_count += 1
                logger.info(f"Transfer validated: {job.amount_raw} → {job.recipient}")
            except Exception as exc:
                self._failed.append({"job": job.recipient, "error": str(exc), "ts": time.time()})
                fail_count += 1
                logger.error(f"Transfer failed: {job.recipient} — {exc}")
        return {"success": success_count, "failed": fail_count}

    def queue_size(self) -> int:
        return len(self._queue)

    def completed_count(self) -> int:
        return len(self._completed)
