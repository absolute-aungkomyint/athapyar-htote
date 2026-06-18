"""
Domain models for AthaPyar Htote — personal budget management.

Dataclass-based representations of each database entity, used for
type-safe data passing between the database layer and the terminal UI.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


# ---------------------------------------------------------------------------
# Reference / lookup models
# ---------------------------------------------------------------------------


@dataclass
class Currency:
    """A supported currency (MMK, USD, SGD, THB)."""

    id: int
    code: str          # ISO code, e.g. "MMK"
    name: str          # Human-readable, e.g. "Myanmar Kyat"
    symbol: str        # e.g. "Ks", "$", "S$", "฿"
    is_default: bool = False

    def __str__(self) -> str:
        return f"{self.code} ({self.symbol})"


@dataclass
class ExchangeRate:
    """Conversion rate between two currencies."""

    id: int
    from_currency_id: int
    to_currency_id: int
    rate: float
    updated_at: Optional[datetime] = None


@dataclass
class Category:
    """An income or expense category with an emoji icon."""

    id: int
    name: str          # e.g. "Food & Drinks", "Salary"
    icon: str          # emoji, e.g. "🍜", "💼"
    type: str          # "income" or "expense"

    def __str__(self) -> str:
        return f"{self.icon} {self.name}"


# ---------------------------------------------------------------------------
# Core transaction model
# ---------------------------------------------------------------------------


@dataclass
class Transaction:
    """A single financial transaction — income or expense."""

    id: int
    type: str          # "income" or "expense"
    amount: float
    currency_id: int
    category_id: Optional[int] = None
    note: Optional[str] = None
    created_at: Optional[str] = None

    # Joined fields (populated when fetched with joins)
    category_name: Optional[str] = None
    category_icon: Optional[str] = None
    currency_symbol: Optional[str] = None
    currency_code: Optional[str] = None

    @property
    def is_income(self) -> bool:
        return self.type == "income"

    @property
    def is_expense(self) -> bool:
        return self.type == "expense"

    @property
    def signed_amount(self) -> float:
        """Return positive for income, negative for expense."""
        return self.amount if self.is_income else -self.amount


# ---------------------------------------------------------------------------
# Budget model
# ---------------------------------------------------------------------------


@dataclass
class Budget:
    """A spending (or saving) cap for a given category and time period."""

    id: int
    category_id: int
    amount: float
    currency_id: int
    period: str = "monthly"     # "monthly", "weekly", or "yearly"
    created_at: Optional[str] = None

    # Joined fields
    category_name: Optional[str] = None
    category_icon: Optional[str] = None
    currency_symbol: Optional[str] = None

    @property
    def period_days(self) -> int:
        """Approximate number of days in this budget period."""
        return {"weekly": 7, "monthly": 30, "yearly": 365}.get(self.period, 30)


# ---------------------------------------------------------------------------
# Debt model
# ---------------------------------------------------------------------------


@dataclass
class Debt:
    """A loan, credit card, or other liability."""

    id: int
    name: str                    # e.g. "DBS Credit Card"
    principal: float             # original amount borrowed
    remaining: float             # current outstanding balance
    interest_rate: float = 0.0   # annual percentage rate
    minimum_payment: float = 0.0
    currency_id: int = 1         # defaults to MMK
    due_day: Optional[int] = None  # calendar day of month (1-31)
    created_at: Optional[str] = None

    # Joined fields
    currency_symbol: Optional[str] = None
    currency_code: Optional[str] = None

    @property
    def progress_pct(self) -> float:
        """Percentage of principal already repaid."""
        if self.principal <= 0:
            return 100.0
        return max(0.0, min(100.0, 100 * (1 - self.remaining / self.principal)))

    @property
    def is_paid_off(self) -> bool:
        return self.remaining <= 0

    @property
    def monthly_interest(self) -> float:
        """Estimated monthly interest based on APR."""
        return self.remaining * (self.interest_rate / 100) / 12


# ---------------------------------------------------------------------------
# Financial Goal model
# ---------------------------------------------------------------------------


@dataclass
class Goal:
    """A savings target — short, medium, or long term."""

    id: int
    name: str                  # e.g. "Emergency Fund", "New Laptop"
    target_amount: float
    current_amount: float = 0.0
    currency_id: int = 1       # defaults to MMK
    target_date: Optional[str] = None  # ISO date string
    created_at: Optional[str] = None

    # Joined fields
    currency_symbol: Optional[str] = None
    currency_code: Optional[str] = None

    @property
    def progress_pct(self) -> float:
        """How close the goal is to completion (0-100)."""
        if self.target_amount <= 0:
            return 100.0
        return max(0.0, min(100.0, 100 * self.current_amount / self.target_amount))

    @property
    def is_complete(self) -> bool:
        return self.current_amount >= self.target_amount

    @property
    def remaining(self) -> float:
        """Amount still needed to reach the target."""
        return max(0.0, self.target_amount - self.current_amount)

    @property
    def days_remaining(self) -> Optional[int]:
        """Days until target_date, or None if no deadline set."""
        if not self.target_date:
            return None
        try:
            target = date.fromisoformat(self.target_date)
            return (target - date.today()).days
        except (ValueError, TypeError):
            return None


# ---------------------------------------------------------------------------
# Report / summary models
# ---------------------------------------------------------------------------


@dataclass
class MonthlySummary:
    """Income, expense, and balance for a given month."""

    year: int
    month: int
    income: float = 0.0
    expense: float = 0.0

    @property
    def balance(self) -> float:
        return self.income - self.expense


@dataclass
class NetWorth:
    """High-level assets-minus-liabilities snapshot."""

    cash: float = 0.0
    debt: float = 0.0

    @property
    def net_worth(self) -> float:
        return self.cash - self.debt


# ---------------------------------------------------------------------------
# Factory helpers — build model instances from database row dicts
# ---------------------------------------------------------------------------


def currency_from_row(row: dict) -> Currency:
    return Currency(
        id=row["id"],
        code=row["code"],
        name=row["name"],
        symbol=row["symbol"],
        is_default=bool(row.get("is_default", False)),
    )


def category_from_row(row: dict) -> Category:
    return Category(
        id=row["id"],
        name=row["name"],
        icon=row.get("icon", "📁"),
        type=row["type"],
    )


def transaction_from_row(row: dict) -> Transaction:
    return Transaction(
        id=row["id"],
        type=row["type"],
        amount=row["amount"],
        currency_id=row["currency_id"],
        category_id=row.get("category_id"),
        note=row.get("note"),
        created_at=row.get("created_at"),
        category_name=row.get("category_name"),
        category_icon=row.get("category_icon"),
        currency_symbol=row.get("currency_symbol"),
        currency_code=row.get("currency_code"),
    )


def budget_from_row(row: dict) -> Budget:
    return Budget(
        id=row["id"],
        category_id=row["category_id"],
        amount=row["amount"],
        currency_id=row["currency_id"],
        period=row.get("period", "monthly"),
        created_at=row.get("created_at"),
        category_name=row.get("category_name"),
        category_icon=row.get("category_icon"),
        currency_symbol=row.get("currency_symbol"),
    )


def debt_from_row(row: dict) -> Debt:
    return Debt(
        id=row["id"],
        name=row["name"],
        principal=row["principal"],
        remaining=row["remaining"],
        interest_rate=row.get("interest_rate", 0.0),
        minimum_payment=row.get("minimum_payment", 0.0),
        currency_id=row["currency_id"],
        due_day=row.get("due_day"),
        created_at=row.get("created_at"),
        currency_symbol=row.get("currency_symbol"),
        currency_code=row.get("currency_code"),
    )


def goal_from_row(row: dict) -> Goal:
    return Goal(
        id=row["id"],
        name=row["name"],
        target_amount=row["target_amount"],
        current_amount=row.get("current_amount", 0.0),
        currency_id=row["currency_id"],
        target_date=row.get("target_date"),
        created_at=row.get("created_at"),
        currency_symbol=row.get("currency_symbol"),
        currency_code=row.get("currency_code"),
    )
