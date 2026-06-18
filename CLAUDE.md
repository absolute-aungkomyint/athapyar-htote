# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AthaPyar Htote** is a personal budget management application — local-first, offline-capable, and designed as an alternative to spreadsheets. It targets Myanmar citizens, with Myanmar language support and multi-currency handling.

- **Stack:** Python + SQLite (local storage) + Rich (terminal UI).
- **Status:** Early implementation — terminal UI with core screens wired to a SQLite schema.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

## Architecture

```
main.py         — Terminal UI (Rich).  Menu-driven with screens: dashboard, add/view
                  transactions, budgets, debts, goals.  Mutates the DB via database.py.
database.py     — SQLite schema + CRUD.  Auto-seeds tables (currencies, categories) on
                  first run.  Database file is created as ./athapyar.db.
requirements.txt — Only external dependency is rich (sqlite3 is stdlib).
```

### Database schema (7 tables)

| Table           | Purpose                                 |
|-----------------|-----------------------------------------|
| `currencies`    | MMK (default), USD, SGD, THB            |
| `exchange_rates`| Conversion rates between currencies     |
| `categories`    | Typed income/expense categories + emoji |
| `transactions`  | Core log — amount, type, currency, category, note, timestamp |
| `budgets`       | Per-category monthly/weekly/yearly caps |
| `debts`         | Loans/credit cards with APR & min payment |
| `goals`         | Named savings targets with deadline     |

## Key Design Decisions (from proposal)

- **Local-first / offline-first:** No internet required. Data stays on the user's device.
- **Not a cloud service:** No multi-user collaboration, no cloud sync.
- **Not full accounting software:** No tax filing, business payroll, or double-entry accounting.
- **Lightweight & fast:** Deliberately avoids "massive tables and column views" in favor of a simpler interface.

## Core Features

1. **Record Income** — log all money received (salary, freelance, gifts, etc.)
2. **Expense Tracking & Categorization** — record every expense with category assignment
3. **Budget Management** — set per-category spending limits tied to income
4. **Debt Management** — track and prioritize debt repayment (credit cards, loans, mortgages)
5. **Financial Goals** — define short/medium/long-term objectives
6. **Financial Reports** — periodic net-worth calculation (assets minus liabilities)
7. **Myanmar Language Support** — bilingual UI (Myanmar + English)
8. **Multi-Currency** — handle exchange rates between currencies
