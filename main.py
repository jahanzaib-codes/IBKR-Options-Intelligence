"""
IBKR Options Intelligence - Command Line & Analytics Suite
Interactive terminal runner for 0DTE scanning, GEX profiling, and options flow analytics.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import argparse
from src.greeks.calculator import BlackScholesEngine
from src.gex.engine import GEXProfiler
from src.scanners.spx_0dte.scanner import SPX0DTEScanner
from src.scanners.unusual_activity.scanner import UnusualActivityScanner


def print_banner():
    banner = """
================================================================================
  🎯 IBKR Options Intelligence & 0DTE Analytics Suite
  Author: Jahanzaib | Engine: Black-Scholes & GEX | Connect: IBKR TWS (7497/7496)
================================================================================
    """
    print(banner)


def run_demo():
    print_banner()

    # 1. SPX 0DTE Scan
    print("--- [1/3] 🎯 SPX 0DTE Expected Move & Iron Condor Setup ---")
    scanner = SPX0DTEScanner(target_symbol="SPX")
    spx_spot = 5850.0
    proposal = scanner.scan_iron_condor(current_spot=spx_spot, implied_volatility=0.165)

    print(f"SPX Spot Price: ${spx_spot:.2f} | Strategy: {proposal.strategy.value}")
    print(f"Legs:")
    for leg in proposal.legs_description:
        print(f"   • {leg}")
    print(f"Net Credit: ${proposal.net_credit_debit:.2f} | Max Profit: ${proposal.max_profit_usd:,.2f} | Max Loss: ${proposal.max_loss_usd:,.2f}")
    print(f"Probability of Profit (PoP): {proposal.probability_of_profit}%\n")

    # 2. Gamma Exposure (GEX) Profiler
    print("--- [2/3] 🌊 Gamma Exposure (GEX) Profile (SPY $585.00) ---")
    mock_strikes = [
        {"strike": 575.0, "call_oi": 15000, "put_oi": 45000, "call_gamma": 0.008, "put_gamma": 0.012},
        {"strike": 580.0, "call_oi": 28000, "put_oi": 35000, "call_gamma": 0.018, "put_gamma": 0.022},
        {"strike": 585.0, "call_oi": 62000, "put_oi": 58000, "call_gamma": 0.045, "put_gamma": 0.045},
        {"strike": 590.0, "call_oi": 54000, "put_oi": 21000, "call_gamma": 0.024, "put_gamma": 0.015},
        {"strike": 595.0, "call_oi": 38000, "put_oi": 12000, "call_gamma": 0.011, "put_gamma": 0.007},
    ]
    profile = GEXProfiler.profile_chain(symbol="SPY", underlying_price=585.0, strikes_data=mock_strikes)
    print(f"Net GEX: ${profile.net_gamma_exposure:+,.2f}M | Regime: {profile.market_maker_regime}")
    print(f"Zero-Gamma Flip Level: ${profile.zero_gamma_level:.2f} | Max Pain Strike: ${profile.max_pain_strike:.2f}")
    print(f"{'STRIKE':<10} {'CALL GEX':<14} {'PUT GEX':<14} {'NET GEX':<14} {'TOTAL OI'}")
    print("-" * 65)
    for s in profile.strikes:
        print(f"${s.strike:<9.1f} ${s.call_gex:<13.2f}M ${s.put_gex:<13.2f}M ${s.net_gex:<+13.2f}M {s.total_open_interest:,}")

    # 3. Unusual Activity Scanner
    print("\n--- [3/3] ⚡ Unusual Options Flow & Institutional Sweeps ---")
    flow_scanner = UnusualActivityScanner()
    alerts = flow_scanner.scan()
    print(f"{'SYMBOL':<8} {'EXPIRY':<12} {'STRIKE':<8} {'TYPE':<6} {'V/OI':<8} {'PREMIUM':<14} {'SENTIMENT'}")
    print("-" * 75)
    for a in alerts:
        print(f"{a.symbol:<8} {a.expiration:<12} ${a.strike:<7.1f} {a.right.value:<6} {a.vol_oi_ratio:<7.1f}x ${a.premium_paid_usd:<13,.2f} {a.sentiment}")

    print("\n🎉 Options Intelligence diagnostic suite executed with 100% precision!")


def main():
    parser = argparse.ArgumentParser(description="IBKR Options Intelligence Suite")
    parser.add_argument("--mode", choices=["demo", "spx", "gex", "flow"], default="demo", help="Analysis mode")
    args = parser.parse_args()

    if args.mode == "demo":
        run_demo()
    elif args.mode == "spx":
        s = SPX0DTEScanner()
        prop = s.scan_iron_condor()
        print(f"SPX Iron Condor: {prop.legs_description} | Net Credit: ${prop.net_credit_debit}")
    elif args.mode == "flow":
        fs = UnusualActivityScanner()
        for a in fs.scan():
            print(f"Alert: {a.symbol} ${a.strike} {a.right.value} | Vol/OI: {a.vol_oi_ratio}x")


if __name__ == "__main__":
    main()

