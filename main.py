#!/usr/bin/env python3
"""
AthaPyar Htote — Personal Budget Manager.

A terminal-based, local-first personal finance app for Myanmar citizens.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, FloatPrompt, IntPrompt, Prompt
from rich.table import Table
from rich.text import Text

import database as db

console = Console()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

HEADER = Text(
    "💰 AthaPyar Htote · အသပြာထုပ်",
    style="bold bright_yellow",
)

FOOTER = Text("q — back  ·  Ctrl+C — quit", style="dim")


def _header() -> None:
    console.clear()
    console.print(HEADER)
    console.print()


def _info(msg: str) -> None:
    console.print(f"[dim]{msg}[/dim]")


def _menu(options: list[tuple[str, str, str]]) -> Table:
    """Build a vertical menu table.  Each entry is (key, label, description)."""
    table = Table(box=box.SIMPLE, show_header=False, padding=(1, 2))
    table.add_column("key", style="bold cyan", width=4)
    table.add_column("label", style="bold")
    table.add_column("desc", style="dim")
    for key, label, desc in options:
        table.add_row(key, label, desc)
    return table


def _pick_category(type_: str) -> Optional[dict]:
    """Let the user pick a category from a numbered list; returns the row dict."""
    cats = db.get_categories(type_)
    if not cats:
        _info(f"No {type_} categories found.")
        Prompt.ask("[dim]Press Enter[/dim]")
        return None
    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    table.add_column("#", style="cyan", width=4)
    table.add_column("Category", style="bold")
    for i, c in enumerate(cats, 1):
        table.add_row(str(i), f"{c['icon']} {c['name']}")
    console.print(table)
    idx = IntPrompt.ask("Choose category", choices=[str(i) for i in range(1, len(cats) + 1)])
    return cats[idx - 1]


def _pick_currency() -> dict:
    currencies = db.get_currencies()
    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    table.add_column("#", style="cyan", width=4)
    table.add_column("Currency", style="bold")
    for i, cu in enumerate(currencies, 1):
        default_marker = " ★" if cu["is_default"] else ""
        table.add_row(str(i), f"{cu['symbol']}  {cu['code']} — {cu['name']}{default_marker}")
    console.print(table)
    idx = IntPrompt.ask("Choose currency", choices=[str(i) for i in range(1, len(currencies) + 1)])
    return currencies[idx - 1]


# ---------------------------------------------------------------------------
# Screens
# ---------------------------------------------------------------------------

def dashboard() -> None:
    """Show a high-level financial snapshot."""
    _header()
    now = datetime.now()
    summary = db.get_monthly_summary(now.year, now.month)
    net = db.get_net_worth()

    def fmt(v: float) -> str:
        return f"{v:,.0f} Ks"

    table = Table(title=f"📊  Dashboard — {now.strftime('%B %Y')}", box=box.SIMPLE_HEAVY)
    table.add_column("Item", style="bold")
    table.add_column("Amount", justify="right")

    table.add_row("[green]Income (this month)[/green]", fmt(summary["income"]))
    table.add_row("[red]Expenses (this month)[/red]", fmt(summary["expense"]))
    table.add_row(
        "[bold]Balance[/bold]",
        f"[{'green' if summary['balance'] >= 0 else 'red'}]{fmt(summary['balance'])}[/]",
    )
    table.add_section()
    table.add_row("Cash on hand", fmt(net["cash"]))
    table.add_row("[red]Total debt[/red]", fmt(net["debt"]))
    table.add_row(
        "[bold bright_yellow]Net worth[/bold bright_yellow]",
        f"[{'green' if net['net_worth'] >= 0 else 'red'}]{fmt(net['net_worth'])}[/]",
    )
    console.print(table)
    console.print()
    Prompt.ask("[dim]Press Enter for menu[/dim]")


def add_transaction_screen() -> None:
    """Prompt-driven flow to log an income or expense."""
    _header()
    console.print("[bold]➕  Add Transaction[/bold]\n")

    t_type = Prompt.ask("Type", choices=["income", "expense"])
    amount = FloatPrompt.ask("Amount")

    console.print()
    currency = _pick_currency()

    console.print()
    cat = _pick_category(t_type)

    note = Prompt.ask("Note (optional)", default="")

    db.add_transaction(
        type_=t_type,
        amount=amount,
        currency_id=currency["id"],
        category_id=cat["id"],
        note=note or None,
    )
    console.print("\n[green]✓ Transaction saved![/green]")
    Prompt.ask("[dim]Press Enter[/dim]")


def view_transactions_screen() -> None:
    """List recent transactions in a table."""
    _header()
    console.print("[bold]📋  Recent Transactions[/bold]\n")

    txns = db.get_transactions(limit=50)
    if not txns:
        _info("No transactions yet.")
        Prompt.ask("[dim]Press Enter[/dim]")
        return

    table = Table(box=box.SIMPLE, show_lines=False)
    table.add_column("Date", style="dim")
    table.add_column("Type")
    table.add_column("Category")
    table.add_column("Amount", justify="right")
    table.add_column("Note", style="dim")

    for t in txns:
        sign = "+" if t["type"] == "income" else "-"
        color = "green" if t["type"] == "income" else "red"
        cat_label = f"{t['category_icon']} {t['category_name']}" if t["category_name"] else "—"
        table.add_row(
            t["created_at"][:10],
            t["type"].capitalize(),
            cat_label,
            f"[{color}]{sign}{t['amount']:,.0f} {t['currency_symbol']}[/{color}]",
            t["note"] or "",
        )
    console.print(table)
    console.print()
    Prompt.ask("[dim]Press Enter[/dim]")


def budgets_screen() -> None:
    """Show budgets and set new ones."""
    _header()
    console.print("[bold]📊  Budgets[/bold]\n")

    budgets = db.get_budgets()
    if budgets:
        table = Table(box=box.SIMPLE, show_header=True)
        table.add_column("Category")
        table.add_column("Limit", justify="right")
        table.add_column("Period")
        for b in budgets:
            table.add_row(
                f"{b['category_icon']} {b['category_name']}",
                f"{b['amount']:,.0f} {b['currency_symbol']}",
                b["period"].capitalize(),
            )
        console.print(table)
    else:
        _info("No budgets set yet.\n")

    if Confirm.ask("Set a new budget?", default=True):
        console.print()
        cat = _pick_category("expense")
        if cat is None:
            return
        amount = FloatPrompt.ask("Monthly limit")
        currency = _pick_currency()
        period = Prompt.ask("Period", choices=["monthly", "weekly", "yearly"], default="monthly")
        db.set_budget(cat["id"], amount, currency["id"], period)
        console.print("\n[green]✓ Budget set![/green]")
    Prompt.ask("[dim]Press Enter[/dim]")


def debts_screen() -> None:
    """View and manage debts."""
    _header()
    console.print("[bold]💳  Debt Management[/bold]\n")

    debts = db.get_debts()
    if debts:
        table = Table(box=box.SIMPLE)
        table.add_column("Name", style="bold")
        table.add_column("Remaining", justify="right")
        table.add_column("Principal", justify="right", style="dim")
        table.add_column("APR %", justify="right")
        table.add_column("Min. Pay", justify="right")
        for d in debts:
            progress = 100 * (1 - d["remaining"] / max(d["principal"], 1))
            remaining_text = f"[red]{d['remaining']:,.0f} {d['currency_symbol']}[/red]" if d["remaining"] > 0 else f"[green]Paid ✓[/green]"
            table.add_row(
                d["name"],
                remaining_text,
                f"{d['principal']:,.0f}",
                f"{d['interest_rate']:.1f}%" if d["interest_rate"] else "—",
                f"{d['minimum_payment']:,.0f}" if d["minimum_payment"] else "—",
            )
        console.print(table)
    else:
        _info("No debts recorded.\n")

    if Confirm.ask("Add a debt?", default=True):
        console.print()
        name = Prompt.ask("Debt name (e.g. 'CB Credit Card')")
        principal = FloatPrompt.ask("Principal amount")
        remaining = FloatPrompt.ask("Remaining balance", default=principal)
        interest = FloatPrompt.ask("Annual interest rate %", default=0.0)
        min_pay = FloatPrompt.ask("Minimum monthly payment", default=0.0)
        currency = _pick_currency()
        due_day = IntPrompt.ask("Due day of month (1-31, 0 to skip)", default=0)
        db.add_debt(
            name=name,
            principal=principal,
            remaining=remaining,
            interest_rate=interest,
            minimum_payment=min_pay,
            currency_id=currency["id"],
            due_day=due_day if due_day > 0 else None,
        )
        console.print("\n[green]✓ Debt recorded![/green]")
    Prompt.ask("[dim]Press Enter[/dim]")


def goals_screen() -> None:
    """View and manage financial goals."""
    _header()
    console.print("[bold]🎯  Financial Goals[/bold]\n")

    goals = db.get_goals()
    if goals:
        table = Table(box=box.SIMPLE)
        table.add_column("Goal", style="bold")
        table.add_column("Progress", justify="center", width=20)
        table.add_column("Target", justify="right")
        table.add_column("By", style="dim")
        for g in goals:
            pct = 100 * g["current_amount"] / max(g["target_amount"], 1)
            bar_len = 14
            filled = int(bar_len * min(pct / 100, 1))
            bar = f"[green]{'█' * filled}[/green]{'░' * (bar_len - filled)}"
            table.add_row(
                g["name"],
                f"{bar}  {pct:.0f}%",
                f"{g['target_amount']:,.0f} {g['currency_symbol']}",
                g["target_date"] or "—",
            )
        console.print(table)
    else:
        _info("No goals set yet.\n")

    if Confirm.ask("Add a goal?", default=True):
        console.print()
        name = Prompt.ask("Goal name (e.g. 'Emergency Fund')")
        target = FloatPrompt.ask("Target amount")
        currency = _pick_currency()
        target_date = Prompt.ask("Target date (YYYY-MM-DD, or leave blank)", default="")
        db.add_goal(
            name=name,
            target_amount=target,
            currency_id=currency["id"],
            target_date=target_date or None,
        )
        console.print("\n[green]✓ Goal created![/green]")
    Prompt.ask("[dim]Press Enter[/dim]")


# ---------------------------------------------------------------------------
# Main menu
# ---------------------------------------------------------------------------

MENU_OPTIONS = [
    ("1", "🏠  Dashboard",          "Overview of income, expenses & net worth"),
    ("2", "➕  Add Transaction",    "Log income or expense"),
    ("3", "📋  Transactions",       "View recent transactions"),
    ("4", "📊  Budgets",            "Set and view category budgets"),
    ("5", "💳  Debts",              "Track loans, credit cards & repayments"),
    ("6", "🎯  Goals",              "Savings targets & financial goals"),
]


def main() -> None:
    db.init_db()

    while True:
        try:
            _header()
            console.print(_menu(MENU_OPTIONS))
            console.print()
            console.print(FOOTER)

            choice = Prompt.ask("Choose", choices=["1", "2", "3", "4", "5", "6", "q"])

            if choice == "1":
                dashboard()
            elif choice == "2":
                add_transaction_screen()
            elif choice == "3":
                view_transactions_screen()
            elif choice == "4":
                budgets_screen()
            elif choice == "5":
                debts_screen()
            elif choice == "6":
                goals_screen()
            elif choice == "q":
                console.print("\n[dark_orange]Mingalaba! 👋[/dark_orange]")
                break

        except KeyboardInterrupt:
            console.print("\n\n[dark_orange]Mingalaba! 👋[/dark_orange]")
            break


if __name__ == "__main__":
    main()
