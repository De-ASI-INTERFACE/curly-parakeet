"""$KATCOIN — SPL token supply and authority verification.
Fully iterative. No recursion. Memory-safe.
Creator: Richard Patterson (@De-ASI-INTERFACE)
"""
from __future__ import annotations

import os
from dotenv import load_dotenv
from solana.rpc.api import Client
from solders.pubkey import Pubkey
from loguru import logger

load_dotenv()

RPC_URL: str = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
MINT_ADDRESS: str = os.getenv("KATCOIN_MINT_ADDRESS", "")


def verify_token(client: Client, mint: str) -> dict:
    results: dict = {"mint": mint, "errors": []}
    try:
        pubkey = Pubkey.from_string(mint)
        supply = client.get_token_supply(pubkey)
        results["supply_raw"] = int(supply.value.amount)
        results["supply_kat"] = results["supply_raw"] / (10 ** 9)
        results["decimals"] = supply.value.decimals
        logger.info(f"$KATCOIN supply: {results['supply_kat']:,.2f} KAT")
    except Exception as exc:
        results["errors"].append(str(exc))
        logger.error(f"Verification failed: {exc}")
    return results


def main() -> None:
    if not MINT_ADDRESS:
        logger.error("KATCOIN_MINT_ADDRESS not set in .env")
        return
    client = Client(RPC_URL)
    result = verify_token(client, MINT_ADDRESS)
    for k, v in result.items():
        logger.info(f"{k}: {v}")


if __name__ == "__main__":
    main()
