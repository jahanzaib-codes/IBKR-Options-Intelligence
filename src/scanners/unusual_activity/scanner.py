"""
IBKR Options Intelligence - Unusual Options Activity & Flow Scanner
Detects smart money block sweeps, volume-to-open-interest spikes, and institutional positioning.
"""

from typing import List, Dict, Any
from src.chains.models import UnusualActivityAlert, OptionRight


class UnusualActivityScanner:
    def __init__(self):
        # Simulated live options flow feed
        self.raw_flow = [
            {"symbol": "NVDA", "strike": 145.0, "right": OptionRight.CALL, "exp": "Next Week", "vol": 38400, "oi": 8200, "price": 4.10, "sentiment": "BULLISH_SWEEP"},
            {"symbol": "AAPL", "strike": 220.0, "right": OptionRight.PUT, "exp": "Monthly", "vol": 24500, "oi": 6100, "price": 3.40, "sentiment": "BEARISH_BLOCK"},
            {"symbol": "TSLA", "strike": 265.0, "right": OptionRight.CALL, "exp": "0DTE", "vol": 52000, "oi": 11500, "price": 2.85, "sentiment": "BULLISH_SWEEP"},
            {"symbol": "SPY", "strike": 570.0, "right": OptionRight.PUT, "exp": "0DTE", "vol": 78000, "oi": 22000, "price": 1.95, "sentiment": "BEARISH_BLOCK"},
            {"symbol": "MSFT", "strike": 435.0, "right": OptionRight.CALL, "exp": "Bi-Weekly", "vol": 18200, "oi": 4300, "price": 5.20, "sentiment": "BULLISH_SWEEP"},
        ]

    def scan(self, min_vol_oi_ratio: float = 2.0, min_premium_usd: float = 50000.0) -> List[UnusualActivityAlert]:
        """
        Filters flow for high-conviction institutional footprints.
        """
        alerts = []
        for flow in self.raw_flow:
            ratio = flow["vol"] / max(1, flow["oi"])
            premium = flow["vol"] * flow["price"] * 100.0

            if ratio >= min_vol_oi_ratio and premium >= min_premium_usd:
                alerts.append(UnusualActivityAlert(
                    symbol=flow["symbol"],
                    strike=flow["strike"],
                    right=flow["right"],
                    expiration=flow["exp"],
                    volume=flow["vol"],
                    open_interest=flow["oi"],
                    vol_oi_ratio=round(ratio, 2),
                    premium_paid_usd=round(premium, 2),
                    sentiment=flow["sentiment"]
                ))
        return alerts

