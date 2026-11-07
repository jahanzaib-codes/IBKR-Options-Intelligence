"""
IBKR Options Intelligence - Black-Scholes Greeks & Expected Move Engine
Implements closed-form Black-Scholes-Merton formulas and analytical Greek sensitivities.
"""

import math
from typing import Dict, Any


def norm_cdf(x: float) -> float:
    """Standard Normal Cumulative Distribution Function."""
    return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0


def norm_pdf(x: float) -> float:
    """Standard Normal Probability Density Function."""
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


class BlackScholesEngine:
    @staticmethod
    def calculate_greeks(
        underlying_price: float,
        strike: float,
        time_to_expiry_years: float,
        risk_free_rate: float,
        volatility: float,
        is_call: bool
    ) -> Dict[str, float]:
        """
        Calculates theoretical price and full suite of first/second order Greeks.
        """
        S = max(0.01, underlying_price)
        K = max(0.01, strike)
        T = max(0.0001, time_to_expiry_years)
        r = risk_free_rate
        sigma = max(0.01, volatility)

        sqrt_T = math.sqrt(T)
        d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * sqrt_T)
        d2 = d1 - sigma * sqrt_T

        pdf_d1 = norm_pdf(d1)
        discount = math.exp(-r * T)

        # Theoretical Option Price
        if is_call:
            price = S * norm_cdf(d1) - K * discount * norm_cdf(d2)
            delta = norm_cdf(d1)
            rho = (K * T * discount * norm_cdf(d2)) / 100.0
            theta_annual = -(S * pdf_d1 * sigma) / (2.0 * sqrt_T) - r * K * discount * norm_cdf(d2)
        else:
            price = K * discount * norm_cdf(-d2) - S * norm_cdf(-d1)
            delta = norm_cdf(d1) - 1.0
            rho = -(K * T * discount * norm_cdf(-d2)) / 100.0
            theta_annual = -(S * pdf_d1 * sigma) / (2.0 * sqrt_T) + r * K * discount * norm_cdf(-d2)

        gamma = pdf_d1 / (S * sigma * sqrt_T)
        vega = (S * sqrt_T * pdf_d1) / 100.0  # Per 1% vol change
        theta_daily = theta_annual / 365.0    # Per calendar day decay

        return {
            "theoretical_price": round(price, 2),
            "delta": round(delta, 4),
            "gamma": round(gamma, 6),
            "theta": round(theta_daily, 4),
            "vega": round(vega, 4),
            "rho": round(rho, 4)
        }

    @staticmethod
    def estimate_expected_move(
        underlying_price: float,
        implied_volatility: float,
        dte_calendar_days: float
    ) -> Dict[str, float]:
        """
        Estimates expected range bounds: S * IV * sqrt(DTE / 365)
        """
        dte_years = max(0.0001, dte_calendar_days / 365.0)
        expected_range_dollar = underlying_price * implied_volatility * math.sqrt(dte_years)
        expected_range_pct = (expected_range_dollar / underlying_price) * 100.0

        return {
            "expected_move_dollar": round(expected_range_dollar, 2),
            "expected_move_pct": round(expected_range_pct, 2),
            "upper_bound": round(underlying_price + expected_range_dollar, 2),
            "lower_bound": round(underlying_price - expected_range_dollar, 2)
        }

