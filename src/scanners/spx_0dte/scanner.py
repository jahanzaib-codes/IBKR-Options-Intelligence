"""
IBKR Options Intelligence - SPX 0DTE Scanner & Spread Constructor
Scans zero-day-to-expiration option chains and constructs high-probability non-directional Iron Condors.
"""

from typing import Dict, Any, List
from src.greeks.calculator import BlackScholesEngine
from src.chains.models import (
    MultiLegSpreadProposal,
    SpreadStrategyType
)


class SPX0DTEScanner:
    def __init__(self, target_symbol: str = "SPX"):
        self.target_symbol = target_symbol

    def scan_iron_condor(
        self,
        current_spot: float = 5850.0,
        implied_volatility: float = 0.165,
        target_delta: float = 0.12,
        wing_width: float = 25.0
    ) -> MultiLegSpreadProposal:
        """
        Synthesizes an optimal 0DTE Iron Condor around the current SPX spot price.
        Selects short call and short put near target delta (e.g. 12-15 delta),
        with defined protective long wings.
        """
        # 1. Estimate 0DTE Expected Move (1 day)
        move_stats = BlackScholesEngine.estimate_expected_move(
            underlying_price=current_spot,
            implied_volatility=implied_volatility,
            dte_calendar_days=1.0
        )
        exp_move = move_stats["expected_move_dollar"]

        # 2. Select Strikes
        # Short Put placed at Spot - 1.2 * Expected Move (approx ~12-14 Delta)
        short_put_strike = round((current_spot - (1.15 * exp_move)) / 5.0) * 5.0
        long_put_strike = short_put_strike - wing_width

        # Short Call placed at Spot + 1.2 * Expected Move
        short_call_strike = round((current_spot + (1.15 * exp_move)) / 5.0) * 5.0
        long_call_strike = short_call_strike + wing_width

        # 3. Compute Theoretical Credits (approximated for 12-15 delta wings)
        call_spread_credit = round(wing_width * 0.12, 2)  # ~12% of wing width
        put_spread_credit = round(wing_width * 0.14, 2)   # ~14% of wing width
        total_credit = round(call_spread_credit + put_spread_credit, 2)

        max_profit = total_credit * 100.0
        max_loss = (wing_width - total_credit) * 100.0
        risk_reward = round(max_profit / max_loss, 2)
        pop = round((1.0 - (2.0 * target_delta)) * 100.0, 1)  # ~76% Probability of Profit

        legs = [
            f"BUY Long Put @ ${long_put_strike:.0f}",
            f"SELL Short Put @ ${short_put_strike:.0f} (~{target_delta*100:.0f} Delta)",
            f"SELL Short Call @ ${short_call_strike:.0f} (~{target_delta*100:.0f} Delta)",
            f"BUY Long Call @ ${long_call_strike:.0f}"
        ]

        return MultiLegSpreadProposal(
            strategy=SpreadStrategyType.IRON_CONDOR,
            underlying_symbol=self.target_symbol,
            underlying_price=current_spot,
            expiration="0DTE (Today)",
            legs_description=legs,
            net_credit_debit=total_credit,
            max_profit_usd=max_profit,
            max_loss_usd=max_loss,
            risk_reward_ratio=risk_reward,
            probability_of_profit=pop
        )
