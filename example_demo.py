#!/usr/bin/env python3
"""
Example/Demo script showing how to use the Personal Budget Planner
This demonstrates all key features including:
- Adding budget items
- Variable monthly amounts (like electric bills)
- Unpaid transactions that accumulate
- Balance forecasting
"""

from datetime import datetime
from budget_planner import (
    BudgetPlanner, BudgetItem,
    TransactionType, Frequency
)


def create_sample_budget():
    """Create a sample budget with realistic data"""

    # Initialize with starting balance
    planner = BudgetPlanner(starting_balance=5000.00)

    print("Creating sample budget...")

    # Add Income Items
    planner.add_budget_item(BudgetItem(
        name="Monthly Salary",
        transaction_type=TransactionType.INCOME,
        default_amount=4500.00,
        frequency=Frequency.MONTHLY,
        category="Income",
        due_day=1
    ))

    planner.add_budget_item(BudgetItem(
        name="Freelance Work",
        transaction_type=TransactionType.INCOME,
        default_amount=500.00,
        frequency=Frequency.MONTHLY,
        category="Income",
        due_day=15
    ))

    # Add Fixed Expenses
    planner.add_budget_item(BudgetItem(
        name="Rent",
        transaction_type=TransactionType.EXPENSE,
        default_amount=1200.00,
        frequency=Frequency.MONTHLY,
        category="Housing",
        due_day=1
    ))

    planner.add_budget_item(BudgetItem(
        name="Car Payment",
        transaction_type=TransactionType.EXPENSE,
        default_amount=350.00,
        frequency=Frequency.MONTHLY,
        category="Transportation",
        due_day=5
    ))

    planner.add_budget_item(BudgetItem(
        name="Car Insurance",
        transaction_type=TransactionType.EXPENSE,
        default_amount=125.00,
        frequency=Frequency.MONTHLY,
        category="Insurance",
        due_day=10
    ))

    planner.add_budget_item(BudgetItem(
        name="Internet",
        transaction_type=TransactionType.EXPENSE,
        default_amount=60.00,
        frequency=Frequency.MONTHLY,
        category="Utilities",
        due_day=15
    ))

    planner.add_budget_item(BudgetItem(
        name="Cell Phone",
        transaction_type=TransactionType.EXPENSE,
        default_amount=75.00,
        frequency=Frequency.MONTHLY,
        category="Utilities",
        due_day=20
    ))

    # Add Variable Expenses (amounts change by month)
    planner.add_budget_item(BudgetItem(
        name="Electric Bill",
        transaction_type=TransactionType.EXPENSE,
        default_amount=100.00,  # Winter/Spring default
        frequency=Frequency.MONTHLY,
        category="Utilities",
        due_day=12
    ))

    planner.add_budget_item(BudgetItem(
        name="Gas Bill",
        transaction_type=TransactionType.EXPENSE,
        default_amount=80.00,  # Summer default
        frequency=Frequency.MONTHLY,
        category="Utilities",
        due_day=14
    ))

    planner.add_budget_item(BudgetItem(
        name="Groceries",
        transaction_type=TransactionType.EXPENSE,
        default_amount=400.00,
        frequency=Frequency.MONTHLY,
        category="Food",
        due_day=1
    ))

    planner.add_budget_item(BudgetItem(
        name="Credit Card Payment",
        transaction_type=TransactionType.EXPENSE,
        default_amount=200.00,
        frequency=Frequency.MONTHLY,
        category="Debt",
        due_day=25
    ))

    # Set custom amounts for variable expenses
    # Summer months - higher electric bill
    now = datetime.now()
    current_year = now.year

    print("Setting variable amounts for different months...")

    # Electric bill varies by season
    for month in [6, 7, 8]:  # Summer - higher A/C usage
        planner.set_custom_amount("Electric Bill", current_year, month, 180.00)

    for month in [12, 1, 2]:  # Winter - moderate usage
        planner.set_custom_amount("Electric Bill", current_year, month, 140.00)

    # Gas bill varies by season (opposite of electric)
    for month in [6, 7, 8]:  # Summer - minimal usage
        planner.set_custom_amount("Gas Bill", current_year, month, 30.00)

    for month in [12, 1, 2]:  # Winter - heating costs
        planner.set_custom_amount("Gas Bill", current_year, month, 150.00)

    # Holiday shopping in December
    planner.set_custom_amount("Credit Card Payment", current_year, 12, 450.00)

    return planner


def demonstrate_features(planner: BudgetPlanner):
    """Demonstrate the key features"""

    now = datetime.now()
    current_year = now.year
    current_month = now.month

    print("\n" + "="*80)
    print("DEMONSTRATION: Personal Budget Planner Features")
    print("="*80)

    # Feature 1: Generate transactions for multiple months
    print("\n1. Generating transactions for the last 3 months and next 3 months...")
    for month_offset in range(-3, 4):
        target_month = current_month + month_offset
        target_year = current_year

        while target_month < 1:
            target_month += 12
            target_year -= 1
        while target_month > 12:
            target_month -= 12
            target_year += 1

        planner.generate_monthly_transactions(target_year, target_month)

    print("   ✓ Transactions generated")

    # Feature 2: Mark some transactions as paid (but not all)
    print("\n2. Simulating payment of some bills (demonstrating unpaid accumulation)...")

    # Pay salary and some bills for last 3 months
    for month_offset in range(-3, 0):
        target_month = current_month + month_offset
        target_year = current_year

        while target_month < 1:
            target_month += 12
            target_year -= 1

        # Pay income
        planner.mark_transaction_paid("Monthly Salary", target_year, target_month)
        planner.mark_transaction_paid("Freelance Work", target_year, target_month)

        # Pay rent (always pay rent!)
        planner.mark_transaction_paid("Rent", target_year, target_month)

        # Pay some other bills
        planner.mark_transaction_paid("Internet", target_year, target_month)
        planner.mark_transaction_paid("Cell Phone", target_year, target_month)

        # Skip paying Electric Bill for 2 months ago (will accumulate)
        if month_offset != -2:
            planner.mark_transaction_paid("Electric Bill", target_year, target_month)

        # Skip paying Credit Card for last month (will accumulate)
        if month_offset != -1:
            planner.mark_transaction_paid("Credit Card Payment", target_year, target_month)

    print("   ✓ Some transactions marked as paid (some intentionally left unpaid)")

    # Feature 3: Show unpaid transactions
    print("\n3. Viewing unpaid transactions that have accumulated:")
    print("-" * 80)
    unpaid = planner.get_unpaid_transactions()
    total_unpaid = 0.0

    for trans in sorted(unpaid, key=lambda t: (t.year, t.month)):
        item = planner.budget_items.get(trans.budget_item_name)
        if item and item.transaction_type == TransactionType.EXPENSE:
            print(f"   {trans.budget_item_name:30} {trans.year}/{trans.month:02d}  ${trans.amount:>10,.2f}")
            total_unpaid += trans.amount

    print(f"\n   Total Accumulated Unpaid: ${total_unpaid:,.2f}")
    print("   (These unpaid amounts reduce your available balance)")

    # Feature 4: Show current month summary
    print(f"\n4. Current month summary ({datetime(current_year, current_month, 1).strftime('%B %Y')}):")
    print("-" * 80)
    summary = planner.get_monthly_summary(current_year, current_month)
    print(f"   Planned Income:   ${summary['planned_income']:>12,.2f}")
    print(f"   Planned Expenses: ${summary['planned_expenses']:>12,.2f}")
    print(f"   Planned Net:      ${summary['planned_net']:>12,.2f}")

    # Feature 5: Show balance forecast
    print("\n5. Balance Forecast (next 12 months with variable expenses):")
    print("-" * 80)
    forecast = planner.forecast_balance(12)

    print(f"   {'Month':^20} {'Income':>12} {'Expenses':>12} {'Net':>12} {'Balance':>12}")
    print("   " + "-" * 76)

    for entry in forecast:
        print(f"   {entry['month_name']:>20} "
              f"${entry['planned_income']:>11,.2f} "
              f"${entry['planned_expenses']:>11,.2f} "
              f"${entry['net']:>11,.2f} "
              f"${entry['projected_balance']:>11,.2f}")

    # Feature 6: Demonstrate variable expenses
    print("\n6. Demonstrating variable expenses (Electric Bill across months):")
    print("-" * 80)
    print("   Notice how Electric Bill varies by season:")

    for i in range(1, 13):
        item = planner.budget_items["Electric Bill"]
        amount = item.get_amount_for_month(current_year, i, planner.custom_amounts.get("Electric Bill"))
        month_name = datetime(current_year, i, 1).strftime('%B')
        print(f"   {month_name:>12}: ${amount:>6,.2f}", end="")
        if i in [6, 7, 8]:
            print("  (Summer - high A/C usage)")
        elif i in [12, 1, 2]:
            print("  (Winter - moderate usage)")
        else:
            print("  (Spring/Fall - low usage)")

    print("\n" + "="*80)


def main():
    """Main demo function"""
    print("\n" + "="*80)
    print("PERSONAL BUDGET PLANNER - DEMO")
    print("="*80)

    # Create sample budget
    planner = create_sample_budget()

    # Demonstrate features
    demonstrate_features(planner)

    # Save to file
    print("\n\nSaving budget to 'sample_budget.json'...")
    planner.save_to_file("sample_budget.json")
    print("✓ Budget saved!")

    # Show full report
    print("\n\nFull Budget Report:")
    print(planner.get_budget_report())

    print("\n" + "="*80)
    print("DEMO COMPLETE")
    print("="*80)
    print("\nYou can now:")
    print("  1. Run 'python3 main.py' for the interactive interface")
    print("  2. Load 'sample_budget.json' to see this demo budget")
    print("  3. Modify the budget and explore the features")
    print("\nKey Features Demonstrated:")
    print("  ✓ Monthly budget planning")
    print("  ✓ Variable expenses (electric/gas bills change by month)")
    print("  ✓ Unpaid transactions accumulate over time")
    print("  ✓ Balance forecasting with realistic projections")
    print("  ✓ Flexible payment tracking")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
