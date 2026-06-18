"""
Database layer for AthaPyar Htote — personal budget management.

Uses SQLite for local-first, offline-capable storage.
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "athapyar.db")


def get_connection() -> sqlite3.Connection:
    """Open (or create) the local SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS currencies (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    code        TEXT    NOT NULL UNIQUE,   -- e.g. MMK, USD, SGD, THB
    name        TEXT    NOT NULL,
    symbol      TEXT    NOT NULL,          -- e.g. Ks, $, S$, ฿
    is_default  INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS exchange_rates (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    from_currency_id INTEGER NOT NULL REFERENCES currencies(id),
    to_currency_id   INTEGER NOT NULL REFERENCES currencies(id),
    rate             REAL    NOT NULL,
    updated_at       TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE(from_currency_id, to_currency_id)
);

CREATE TABLE IF NOT EXISTS categories (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT    NOT NULL UNIQUE,
    icon     TEXT    NOT NULL DEFAULT '📁',  -- emoji for terminal UI
    type     TEXT    NOT NULL CHECK(type IN ('income', 'expense'))
);

CREATE TABLE IF NOT EXISTS transactions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    type        TEXT    NOT NULL CHECK(type IN ('income', 'expense')),
    amount      REAL    NOT NULL,
    currency_id INTEGER NOT NULL REFERENCES currencies(id),
    category_id INTEGER REFERENCES categories(id),
    note        TEXT,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS budgets (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    amount      REAL    NOT NULL,
    currency_id INTEGER NOT NULL REFERENCES currencies(id),
    period      TEXT    NOT NULL CHECK(period IN ('monthly', 'weekly', 'yearly')),
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS debts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL,            -- e.g. "DBS Credit Card"
    principal       REAL    NOT NULL,
    remaining       REAL    NOT NULL,
    interest_rate   REAL    NOT NULL DEFAULT 0,  -- annual percentage
    minimum_payment REAL    NOT NULL DEFAULT 0,
    currency_id     INTEGER NOT NULL REFERENCES currencies(id),
    due_day         INTEGER,                     -- day of month
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS goals (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL,
    target_amount   REAL    NOT NULL,
    current_amount  REAL    NOT NULL DEFAULT 0,
    currency_id     INTEGER NOT NULL REFERENCES currencies(id),
    target_date     TEXT,                        -- ISO date
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);
"""

# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------

SEED_SQL = """
INSERT OR IGNORE INTO currencies (code, name, symbol, is_default) VALUES
    ('MMK', 'Myanmar Kyat', 'Ks',  1),
    ('USD', 'US Dollar',     '$',   0),
    ('SGD', 'Singapore Dollar', 'S$', 0),
    ('THB', 'Thai Baht',     '฿',   0);

INSERT OR IGNORE INTO categories (name, icon, type) VALUES
    ('Salary',        '💼', 'income'),
    ('Freelance',     '💻', 'income'),
    ('Investment',    '📈', 'income'),
    ('Gift',          '🎁', 'income'),
    ('Food & Drinks', '🍜', 'expense'),
    ('Transport',     '🚗', 'expense'),
    ('Rent',          '🏠', 'expense'),
    ('Utilities',     '💡', 'expense'),
    ('Shopping',      '🛒', 'expense'),
    ('Healthcare',    '🏥', 'expense'),
    ('Education',     '📚', 'expense'),
    ('Entertainment', '🎬', 'expense'),
    ('Debt Payment',  '💳', 'expense');
"""


def init_db() -> None:
    """Create tables and seed initial data if the database is new."""
    conn = get_connection()
    conn.executescript(SCHEMA_SQL)
    conn.executescript(SEED_SQL)
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _row_to_dict(row: sqlite3.Row) -> dict:
    return dict(row) if row else None


def _rows_to_list(rows: list[sqlite3.Row]) -> list[dict]:
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

# -- Transactions -----------------------------------------------------------

def add_transaction(
    *,
    type_: str,
    amount: float,
    currency_id: int,
    category_id: int,
    note: Optional[str] = None,
) -> int:
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO transactions (type, amount, currency_id, category_id, note)
           VALUES (?, ?, ?, ?, ?)""",
        (type_, amount, currency_id, category_id, note),
    )
    conn.commit()
    conn.close()
    return cur.lastrowid


def get_transactions(limit: int = 50) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        """SELECT t.*, c.name AS category_name, c.icon AS category_icon,
                  cu.symbol AS currency_symbol, cu.code AS currency_code
           FROM transactions t
           LEFT JOIN categories c ON t.category_id = c.id
           JOIN currencies cu ON t.currency_id = cu.id
           ORDER BY t.created_at DESC
           LIMIT ?""",
        (limit,),
    ).fetchall()
    conn.close()
    return _rows_to_list(rows)


# -- Categories -------------------------------------------------------------

def get_categories(type_: Optional[str] = None) -> list[dict]:
    conn = get_connection()
    if type_:
        rows = conn.execute(
            "SELECT * FROM categories WHERE type = ? ORDER BY name", (type_,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM categories ORDER BY type, name").fetchall()
    conn.close()
    return _rows_to_list(rows)


# -- Budgets ----------------------------------------------------------------

def set_budget(category_id: int, amount: float, currency_id: int, period: str = "monthly") -> int:
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO budgets (category_id, amount, currency_id, period)
           VALUES (?, ?, ?, ?)""",
        (category_id, amount, currency_id, period),
    )
    conn.commit()
    conn.close()
    return cur.lastrowid


def get_budgets() -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        """SELECT b.*, c.name AS category_name, c.icon AS category_icon,
                  cu.symbol AS currency_symbol
           FROM budgets b
           JOIN categories c ON b.category_id = c.id
           JOIN currencies cu ON b.currency_id = cu.id
           ORDER BY c.name"""
    ).fetchall()
    conn.close()
    return _rows_to_list(rows)


# -- Currencies -------------------------------------------------------------

def get_currencies() -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM currencies ORDER BY is_default DESC, code").fetchall()
    conn.close()
    return _rows_to_list(rows)


def get_default_currency() -> dict:
    conn = get_connection()
    row = conn.execute("SELECT * FROM currencies WHERE is_default = 1").fetchone()
    conn.close()
    return _row_to_dict(row)


# -- Debts ------------------------------------------------------------------

def add_debt(
    *,
    name: str,
    principal: float,
    remaining: float,
    interest_rate: float = 0,
    minimum_payment: float = 0,
    currency_id: int,
    due_day: Optional[int] = None,
) -> int:
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO debts (name, principal, remaining, interest_rate, minimum_payment,
                              currency_id, due_day)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (name, principal, remaining, interest_rate, minimum_payment, currency_id, due_day),
    )
    conn.commit()
    conn.close()
    return cur.lastrowid


def get_debts() -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        """SELECT d.*, cu.symbol AS currency_symbol, cu.code AS currency_code
           FROM debts d
           JOIN currencies cu ON d.currency_id = cu.id
           ORDER BY d.remaining DESC"""
    ).fetchall()
    conn.close()
    return _rows_to_list(rows)


# -- Goals ------------------------------------------------------------------

def add_goal(
    *,
    name: str,
    target_amount: float,
    currency_id: int,
    target_date: Optional[str] = None,
) -> int:
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO goals (name, target_amount, currency_id, target_date)
           VALUES (?, ?, ?, ?)""",
        (name, target_amount, currency_id, target_date),
    )
    conn.commit()
    conn.close()
    return cur.lastrowid


def get_goals() -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        """SELECT g.*, cu.symbol AS currency_symbol, cu.code AS currency_code
           FROM goals g
           JOIN currencies cu ON g.currency_id = cu.id
           ORDER BY g.target_date"""
    ).fetchall()
    conn.close()
    return _rows_to_list(rows)


# -- Reports ----------------------------------------------------------------

def get_monthly_summary(year: int, month: int) -> dict:
    """Return total income and total expense for a given month."""
    conn = get_connection()
    period = f"{year}-{month:02d}%"
    income = conn.execute(
        """SELECT COALESCE(SUM(amount), 0) FROM transactions
           WHERE type = 'income' AND created_at LIKE ?""",
        (period,),
    ).fetchone()[0]
    expense = conn.execute(
        """SELECT COALESCE(SUM(amount), 0) FROM transactions
           WHERE type = 'expense' AND created_at LIKE ?""",
        (period,),
    ).fetchone()[0]
    conn.close()
    return {"income": income, "expense": expense, "balance": income - expense}


def get_net_worth() -> dict:
    """Assets (cash + goal savings) minus liabilities (debts remaining)."""
    conn = get_connection()
    total_income = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE type = 'income'"
    ).fetchone()[0]
    total_expense = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE type = 'expense'"
    ).fetchone()[0]
    total_debt = conn.execute(
        "SELECT COALESCE(SUM(remaining), 0) FROM debts"
    ).fetchone()[0]
    conn.close()
    cash = total_income - total_expense
    return {"cash": cash, "debt": total_debt, "net_worth": cash - total_debt}
