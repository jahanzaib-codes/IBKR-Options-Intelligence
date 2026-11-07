"""
IBKR Options Intelligence - Gamma Exposure (GEX) & Market Maker Profiler
Calculates dealer gamma exposure, zero-gamma inflection levels, and pin risk.
"""

from typing import List, Dict, Any
from src.chains.models import GEXProfile, GEXStrikeSummary


class GEXProfiler:
    @staticmethod
    def profile_chain(
        symbol: str,
        underlying_price: float,
        strikes_data: List[Dict[str, Any]]
    ) -> GEXProfile:
        """
        Profiles aggregate market-maker gamma exposure across option strikes.
        Formula:
          Call GEX = Call Gamma * Call Open Interest * 100 * Underlying Price^2 * 0.01
          Put GEX  = Put Gamma * Put Open Interest * 100 * Underlying Price^2 * 0.01 * (-1)
        """
        summaries: List[GEXStrikeSummary] = []
        total_net_gex = 0.0

        for s in strikes_data:
            strike = s["strike"]
            call_oi = s.get("call_oi", 1000)
            put_oi = s.get("put_oi", 1000)
            call_gamma = s.get("call_gamma", 0.005)
            put_gamma = s.get("put_gamma", 0.005)

            # Dollar Gamma per 1% underlying change (in Millions USD)
            multiplier = 100.0 * (underlying_price ** 2) * 0.01 / 1e6
            call_gex = call_gamma * call_oi * multiplier
            put_gex = put_gamma * put_oi * multiplier  # Stored positive for magnitude

            net_strike_gex = call_gex - put_gex
            total_net_gex += net_strike_gex

            summaries.append(GEXStrikeSummary(
                strike=strike,
                call_gex=round(call_gex, 2),
                put_gex=round(put_gex, 2),
                net_gex=round(net_strike_gex, 2),
                total_open_interest=call_oi + put_oi
            ))

        # Sort strikes ascending
        summaries.sort(key=lambda x: x.strike)

        # Estimate Zero-Gamma Flip level (where cumulative net GEX transitions sign)
        zero_gamma_level = underlying_price
        for i in range(len(summaries) - 1):
            if summaries[i].net_gex * summaries[i + 1].net_gex < 0:
                zero_gamma_level = (summaries[i].strike + summaries[i + 1].strike) / 2.0
                break

        # Max Pain Strike (strike with minimum total option expiration payout)
        max_pain_strike = min(summaries, key=lambda x: abs(x.net_gex)).strike

        regime = "LONG_GAMMA_STABILIZING" if total_net_gex >= 0 else "SHORT_GAMMA_VOLATILE"

        return GEXProfile(
            symbol=symbol,
            underlying_price=underlying_price,
            net_gamma_exposure=round(total_net_gex, 2),
            zero_gamma_level=round(zero_gamma_level, 2),
            max_pain_strike=max_pain_strike,
            market_maker_regime=regime,
            strikes=summaries
        )

