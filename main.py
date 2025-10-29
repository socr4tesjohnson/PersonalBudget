#!/usr/bin/env python3
"""
Interactive CLI for Personal Budget Planner
"""

import sys
import os
from datetime import datetime
from budget_planner import (
    BudgetPlanner, BudgetItem, Transaction,
    TransactionType, Frequency
)


def clear_screen():
    """Clear the terminal screen"""
    os.system('clear' if os.name != 'nt' else 'cls')


def display_menu():
    """Display main menu"""
    print("\n" + "=" * 60)
    print("PERSONAL BUDGET PLANNER")
    print("=" * 60)
    print("1.  View Budget Report")
    print("2.  Add Budget Item")
    print("3.  View All Budget Items")
    print("4.  Set Custom Amount for Month")
    print("5.  Generate Monthly Transactions")
    print("6.  Mark Transaction as Paid")
    print("7.  View Unpaid Transactions")
    print("8.  View Monthly Summary")
    print("9.  View Balance Forecast")
    print("10. Save Budget to File")
    print("11. Load Budget from File")
    print("12. Set Starting Balance")
    print("0.  Exit")
    print("=" * 60)


def add_budget_item(planner: BudgetPlanner):
    """Add a new budget item"""
    print("\n--- Add Budget Item ---")
    name = input("Item Name: ").strip()

    print("Transaction Type:")
    print("  1. Income")
    print("  2. Expense")
    trans_type_choice = input("Choice (1-2): ").strip()
    trans_type = TransactionType.INCOME if trans_type_choice == "1" else TransactionType.EXPENSE

    amount = float(input("Default Amount: $").strip())

    print("Frequency:")
    print("  1. Monthly")
    print("  2. One-time")
    freq_choice = input("Choice (1-2): ").strip()
    frequency = Frequency.MONTHLY if freq_choice == "1" else Frequency.ONE_TIME

    category = input("Category (default: General): ").strip() or "General"
    due_day = int(input("Due Day of Month (1-31, default: 1): ").strip() or "1")

    item = BudgetItem(
        name=name,
        transaction_type=trans_type,
        default_amount=amount,
        frequency=frequency,
        category=category,
        due_day=due_day
    )

    planner.add_budget_item(item)
    print(f"\n✓ Budget item '{name}' added successfully!")


def view_budget_items(planner: BudgetPlanner):
    """View all budget items"""
    print("\n--- All Budget Items ---")
    if not planner.budget_items:
        print("No budget items found.")
        return

    for name, item in planner.budget_items.items():
        print(f"\n{name}:")
        print(f"  Type: {item.transaction_type.value.title()}")
        print(f"  Amount: ${item.default_amount:,.2f}")
        print(f"  Frequency: {item.frequency.value.title()}")
        print(f"  Category: {item.category}")
        print(f"  Due Day: {item.due_day}")


def set_custom_amount(planner: BudgetPlanner):
    """Set a custom amount for a specific month"""
    print("\n--- Set Custom Amount ---")

    if not planner.budget_items:
        print("No budget items found. Add budget items first.")
        return

    print("Available items:")
    for i, name in enumerate(planner.budget_items.keys(), 1):
        print(f"  {i}. {name}")

    item_name = input("\nItem Name: ").strip()

    if item_name not in planner.budget_items:
        print(f"Error: Item '{item_name}' not found.")
        return

    year = int(input("Year (YYYY): ").strip())
    month = int(input("Month (1-12): ").strip())
    amount = float(input("Custom Amount: $").strip())

    planner.set_custom_amount(item_name, year, month, amount)
    print(f"\n✓ Custom amount ${amount:,.2f} set for {item_name} in {year}-{month:02d}")


def generate_monthly_transactions(planner: BudgetPlanner):
    """Generate transactions for a specific month"""
    print("\n--- Generate Monthly Transactions ---")
    year = int(input("Year (YYYY): ").strip())
    month = int(input("Month (1-12): ").strip())

    planner.generate_monthly_transactions(year, month)
    print(f"\n✓ Transactions generated for {year}-{month:02d}")


def mark_transaction_paid(planner: BudgetPlanner):
    """Mark a transaction as paid"""
    print("\n--- Mark Transaction as Paid ---")

    unpaid = planner.get_unpaid_transactions()
    if not unpaid:
        print("No unpaid transactions found.")
        return

    print("\nUnpaid Transactions:")
    for i, trans in enumerate(unpaid, 1):
        print(f"  {i}. {trans.budget_item_name} - {trans.year}/{trans.month:02d} - ${trans.amount:,.2f}")

    choice = int(input("\nSelect transaction number to mark as paid: ").strip())

    if 1 <= choice <= len(unpaid):
        trans = unpaid[choice - 1]
        planner.mark_transaction_paid(trans.budget_item_name, trans.year, trans.month)
        print(f"\n✓ Transaction marked as paid: {trans.budget_item_name} - {trans.year}/{trans.month:02d}")
    else:
        print("Invalid choice.")


def view_unpaid_transactions(planner: BudgetPlanner):
    """View all unpaid transactions"""
    print("\n--- Unpaid Transactions ---")
    unpaid = planner.get_unpaid_transactions()

    if not unpaid:
        print("No unpaid transactions found!")
        return

    total = 0.0
    for trans in sorted(unpaid, key=lambda t: (t.year, t.month)):
        item = planner.budget_items.get(trans.budget_item_name)
        if item:
            print(f"{trans.budget_item_name:30} {trans.year}/{trans.month:02d}  "
                  f"${trans.amount:>12,.2f}  [{item.transaction_type.value}]")
            if item.transaction_type == TransactionType.EXPENSE:
                total += trans.amount

    print(f"\nTotal Accumulated Unpaid Expenses: ${total:,.2f}")


def view_monthly_summary(planner: BudgetPlanner):
    """View summary for a specific month"""
    print("\n--- Monthly Summary ---")
    year = int(input("Year (YYYY): ").strip())
    month = int(input("Month (1-12): ").strip())

    summary = planner.get_monthly_summary(year, month)

    print(f"\nSummary for {datetime(year, month, 1).strftime('%B %Y')}:")
    print("-" * 60)
    print(f"Planned Income:   ${summary['planned_income']:>12,.2f}")
    print(f"Planned Expenses: ${summary['planned_expenses']:>12,.2f}")
    print(f"Planned Net:      ${summary['planned_net']:>12,.2f}")
    print()
    print(f"Paid Income:      ${summary['paid_income']:>12,.2f}")
    print(f"Paid Expenses:    ${summary['paid_expenses']:>12,.2f}")
    print(f"Paid Net:         ${summary['paid_net']:>12,.2f}")
    print()
    print(f"Unpaid Income:    ${summary['unpaid_income']:>12,.2f}")
    print(f"Unpaid Expenses:  ${summary['unpaid_expenses']:>12,.2f}")


def view_forecast(planner: BudgetPlanner):
    """View balance forecast"""
    print("\n--- Balance Forecast ---")
    months = int(input("Number of months to forecast (default: 12): ").strip() or "12")

    forecast = planner.forecast_balance(months)

    print(f"\nBalance Forecast for Next {months} Months:")
    print("-" * 80)
    print(f"{'Month':^20} {'Income':>12} {'Expenses':>12} {'Net':>12} {'Balance':>12}")
    print("-" * 80)

    for entry in forecast:
        print(f"{entry['month_name']:>20} "
              f"${entry['planned_income']:>11,.2f} "
              f"${entry['planned_expenses']:>11,.2f} "
              f"${entry['net']:>11,.2f} "
              f"${entry['projected_balance']:>11,.2f}")


def save_budget(planner: BudgetPlanner):
    """Save budget to file"""
    print("\n--- Save Budget ---")
    filename = input("Filename (default: budget.json): ").strip() or "budget.json"

    try:
        planner.save_to_file(filename)
        print(f"\n✓ Budget saved to {filename}")
    except Exception as e:
        print(f"\n✗ Error saving budget: {e}")


def load_budget(planner: BudgetPlanner):
    """Load budget from file"""
    print("\n--- Load Budget ---")
    filename = input("Filename (default: budget.json): ").strip() or "budget.json"

    try:
        planner.load_from_file(filename)
        print(f"\n✓ Budget loaded from {filename}")
    except FileNotFoundError:
        print(f"\n✗ File {filename} not found.")
    except Exception as e:
        print(f"\n✗ Error loading budget: {e}")


def set_starting_balance(planner: BudgetPlanner):
    """Set the starting balance"""
    print("\n--- Set Starting Balance ---")
    print(f"Current starting balance: ${planner.starting_balance:,.2f}")
    balance = float(input("New starting balance: $").strip())
    planner.starting_balance = balance
    print(f"\n✓ Starting balance set to ${balance:,.2f}")


def main():
    """Main program loop"""
    planner = BudgetPlanner()

    print("\nWelcome to Personal Budget Planner!")
    print("\nTip: You can load an existing budget file or start creating a new budget.")

    while True:
        display_menu()
        choice = input("\nEnter your choice: ").strip()

        try:
            if choice == "0":
                print("\nThank you for using Personal Budget Planner!")
                sys.exit(0)
            elif choice == "1":
                print(planner.get_budget_report())
            elif choice == "2":
                add_budget_item(planner)
            elif choice == "3":
                view_budget_items(planner)
            elif choice == "4":
                set_custom_amount(planner)
            elif choice == "5":
                generate_monthly_transactions(planner)
            elif choice == "6":
                mark_transaction_paid(planner)
            elif choice == "7":
                view_unpaid_transactions(planner)
            elif choice == "8":
                view_monthly_summary(planner)
            elif choice == "9":
                view_forecast(planner)
            elif choice == "10":
                save_budget(planner)
            elif choice == "11":
                load_budget(planner)
            elif choice == "12":
                set_starting_balance(planner)
            else:
                print("\nInvalid choice. Please try again.")

            input("\nPress Enter to continue...")

        except KeyboardInterrupt:
            print("\n\nThank you for using Personal Budget Planner!")
            sys.exit(0)
        except Exception as e:
            print(f"\n✗ Error: {e}")
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
