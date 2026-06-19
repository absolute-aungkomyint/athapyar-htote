---
marp: true
theme: uncover
class:
  - lead
  - invert
paginate: true
size: 16:9
---

<!--
PechaKucha-style: 6 slides × 20 seconds each = 2 minutes total
-->

---

# 💰 AthaPyar Htote
## အသပြာထုပ်

**Your money, your device, your control.**

A local-first personal budget manager
built for Myanmar citizens.

---

<!-- _class: default -->

# 🤔 The Problem

- **Spreadsheet fatigue** — tracking finances in massive tables is exhausting
- **Privacy anxiety** — cloud services mean your data lives on someone else's server
- **Complexity overload** — full accounting suites are overkill for personal budgets
- **No internet? No access.** — most tools stop working offline

<div style="margin-top: 2rem;">

**People lose track of their financial progress
because tracking feels like a chore.**

</div>

---

<!-- _class: default -->

# ⚡ What It Does

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; text-align: left;">

**1. Record Income** 💼
Log salary, freelance, gifts — know what you have.

**2. Track Expenses** 🍜
Categorize every kyat spent.

**3. Budget Management** 📊
Set spending limits per category.

**4. Debt Management** 💳
Track loans, credit cards, and repayment plans.

**5. Financial Goals** 🎯
Define short, medium & long-term targets.

**6. Net-Worth Reports** 📈
Assets minus liabilities — know where you stand.

</div>

---

<!-- _class: default -->

# 🔧 Under the Hood

<div style="text-align: left;">

| Layer | Tech |
|-------|------|
| **Language** | Python 3 |
| **Database** | SQLite (local file) |
| **Terminal UI** | Rich library |
| **Connectivity** | **None required** |

</div>

<div style="margin-top: 2rem; text-align: left;">

**7 database tables** — currencies, exchange rates,
categories, transactions, budgets, debts, goals.

**~360 lines of Python** — lightweight, fast, readable.

</div>

---

<!-- _class: default -->

# 🎯 Design Principles

<div style="text-align: left;">

🇲🇲 **Myanmar-first**
Built for Myanmar citizens — bilingual UI
(Myanmar + English) planned.

💱 **Multi-currency**
MMK, USD, SGD, THB with exchange rates —
for citizens at home and abroad.

🔒 **Local-first & offline-first**
Data never leaves your device. No accounts,
no cloud, no internet dependency.

⚡ **Frictionless**
Terminal UI with emoji-rich menus —
log a transaction in seconds, not minutes.

</div>

---

<!-- _class: default invert -->

# 🚀 What's Next

<div style="text-align: left;">

✅ Core SQLite schema implemented
✅ Transaction entry — fast & functional
⬜ Monthly budget visualizations
⬜ Myanmar language (bilingual UI)
⬜ Recurring transactions
⬜ Enhanced reporting & charts
⬜ Mobile-friendly interface

</div>

<div style="margin-top: 3rem;">

### **Offline. Private. Yours.**
`python main.py` — that's all it takes.

</div>
