---
marp: true
paginate: true
transition: fade
auto-advance: 20
---

# 💰 AthaPyar Htote · အသပြာထုပ်

**Your money, your device, your control.**

A local-first personal budget manager
built for Myanmar citizens, by a Myanmar citizen.

---

# 🤔 Problem & Evidence

- **Spreadsheet fatigue** — tracking finances in massive tables is exhausting
- **Privacy anxiety** — cloud services mean your data lives on someone else's server
- **No internet, no access** — most tools stop working offline
- **Complexity overload** — full accounting suites are overkill for personal budgets

<br>

> *"People keep losing traces of their financial progress.
> Financial clarity should be frictionless — not a chore."*
>
> — @absolute-aungkomyint, proposal

---

# ⚡ What It Does

| # | Feature | What it means |
|---|---------|---------------|
| 1 | **Record Income** 💼 | Log salary, freelance, gifts |
| 2 | **Track Expenses** 🍜 | Categorize every kyat spent |
| 3 | **Budget Management** 📊 | Per-category spending limits |
| 4 | **Debt Management** 💳 | Loans, credit cards, repayment plans |
| 5 | **Financial Goals** 🎯 | Short, medium & long-term targets |
| 6 | **Net-Worth Reports** 📈 | Assets minus liabilities |

**MVP delivered** — all six features wired to a SQLite schema,
terminal UI with emoji-rich menus, ~360 lines of Python.

---

# 🔧 Architecture & Tooling

```text
main.py         ← Rich terminal UI (menu-driven screens)
database.py     ← SQLite schema + CRUD + auto-seed
models.py       ← Dataclass layer with helper properties
```

| Layer | Choice |
|-------|--------|
| Language | Python 3 |
| Database | SQLite (local file, WAL mode) |
| UI | Rich library (tables, panels, prompts) |
| Connectivity | **None required** — offline-first |

**7 tables**: currencies, exchange_rates, categories,
transactions, budgets, debts, goals.

**MCP / Skills / Agents**: `.mcp.json` filesystem server ·
`budget-analyzer` skill (read-only reports) ·
`budget-assistant` agent (financial coach)

---

# 🎯 Design Principles & Lessons

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;">

<div>

**What worked**
- SQLite + Rich = zero-dependency simplicity
- Emoji categories make scanning effortless
- Local-first: no auth, no latency, no privacy risk

**What was hard**
- Bilingual UI is planned but not yet built
- Reports need visual charts (still text-only)
- No recurring-transaction support yet

</div>

<div>

**Principles**
- 🇲🇲 Myanmar-first, bilingual planned
- 💱 Multi-currency (MMK, USD, SGD, THB)
- 🔒 Data never leaves the device
- ⚡ Transaction entry in seconds, not minutes

</div>

</div>

---

# 🚀 Roadmap & Next Steps

| Status | Item |
|--------|------|
| ✅ | Core SQLite schema & seed data |
| ✅ | Transaction CRUD with categories |
| ✅ | Budget, debt & goal screens |
| ✅ | Monthly dashboard + net-worth report |
| ✅ | MCP filesystem server + skills + agents |
| ⬜ | Monthly budget visualizations (charts) |
| ⬜ | Myanmar language bilingual UI |
| ⬜ | Recurring / scheduled transactions |
| ⬜ | Export reports (CSV / PDF) |

<br>

### **Offline. Private. Yours.**
`python main.py` — that's all it takes.

**Mingalaba!** 👋
