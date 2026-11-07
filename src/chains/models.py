"""
IBKR Options Intelligence - Option Domain Models & Data Schemas
"""

from datetime import date, datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class OptionRight(str, Enum):
    CALL = "C"
    PUT = "P"


class SpreadStrategyType(str, Enum):
    IRON_CONDOR = "IRON_CONDOR"
    VERTICAL_CREDIT_SPREAD = "VERTICAL_CREDIT"
    VERTICAL_DEBIT_SPREAD = "VERTICAL_DEBIT"
    CALENDAR_SPREAD = "CALENDAR"
    BUTTERFLY = "BUTTERFLY"


class OptionGreekQuote(BaseModel):
    symbol: str
    underlying_price: float
    strike: float
    right: OptionRight
    expiration: str
    dte: float
    bid: float
    ask: float
    last_price: float
    volume: int
    open_interest: int
    implied_volatility: float
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float


class GEXStrikeSummary(BaseModel):
    strike: float
    call_gex: float
    put_gex: float
    net_gex: float
    total_open_interest: int


class GEXProfile(BaseModel):
    symbol: str
    underlying_price: float
    net_gamma_exposure: float
    zero_gamma_level: float
    max_pain_strike: float
    market_maker_regime: str  # "LONG_GAMMA_STABILIZING" or "SHORT_GAMMA_VOLATILE"
    strikes: List[GEXStrikeSummary]


class UnusualActivityAlert(BaseModel):
    symbol: str
    strike: float
    right: OptionRight
    expiration: str
    volume: int
    open_interest: int
    vol_oi_ratio: float
    premium_paid_usd: float
    sentiment: str  # "BULLISH_SWEEP" or "BEARISH_BLOCK"


class MultiLegSpreadProposal(BaseModel):
    strategy: SpreadStrategyType
    underlying_symbol: str
    underlying_price: float
    expiration: str
    legs_description: List[str]
    net_credit_debit: float
    max_profit_usd: float
    max_loss_usd: float
    risk_reward_ratio: float
    probability_of_profit: float
