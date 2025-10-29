# Personal Budget Planner

A flexible, powerful personal budget management system that helps you plan monthly budgets, track payments, handle unpaid amounts that accumulate over time, and forecast your account balance.

## Features

### Core Capabilities

1. **Monthly Budget Planning**
   - Create budget items for income and expenses
   - Set default amounts and customize per month
   - Categorize items (Housing, Utilities, Food, etc.)
   - Define due dates for each budget item

2. **Flexible Variable Expenses**
   - Set different amounts for the same item across months
   - Perfect for utilities like electric bills that vary by season
   - Handle irregular expenses like holiday shopping

3. **Payment Tracking**
   - Mark transactions as paid or unpaid
   - Track payment dates
   - Add notes to transactions

4. **Unpaid Amount Accumulation**
   - Unpaid bills automatically accumulate until paid
   - Clear visibility into accumulated debt
   - Impacts balance forecasting

5. **Balance Forecasting**
   - Project your balance up to 12+ months ahead
   - Accounts for unpaid amounts
   - Helps you plan for future expenses

6. **Persistence**
   - Save and load budgets to/from JSON files
   - Multiple budget scenarios supported

## Installation

No dependencies required! This project uses only Python standard library.

**Requirements:**
- Python 3.7 or higher

**Clone and use:**
```bash
git clone <repository-url>
cd PersonalBudget
python3 main.py  # Start interactive interface
```

## Quick Start

### Option 1: Run the Demo

See all features in action with a realistic example:

```bash
python3 example_demo.py
```

This creates a sample budget showing:
- Multiple income and expense items
- Variable electric/gas bills by season
- Unpaid transactions that accumulate
- 12-month balance forecast

### Option 2: Interactive Interface

Launch the interactive CLI menu:

```bash
python3 main.py
```

Then:
1. Set your starting balance (option 12)
2. Add budget items (option 2)
3. Generate monthly transactions (option 5)
4. Mark payments as paid (option 6)
5. View reports and forecasts (options 1, 7, 9)
6. Save your budget (option 10)

### Option 3: Python API

Use the budget planner programmatically:

```python
from budget_planner import BudgetPlanner, BudgetItem, TransactionType, Frequency

# Create planner
planner = BudgetPlanner(starting_balance=5000.00)

# Add income
planner.add_budget_item(BudgetItem(
    name="Monthly Salary",
    transaction_type=TransactionType.INCOME,
    default_amount=4500.00,
    frequency=Frequency.MONTHLY,
    due_day=1
))

# Add expense
planner.add_budget_item(BudgetItem(
    name="Rent",
    transaction_type=TransactionType.EXPENSE,
    default_amount=1200.00,
    frequency=Frequency.MONTHLY,
    due_day=1
))

# Set variable amount for a specific month
planner.set_custom_amount("Electric Bill", 2025, 7, 180.00)  # Summer is expensive!

# Generate transactions for current month
from datetime import datetime
now = datetime.now()
planner.generate_monthly_transactions(now.year, now.month)

# Mark a payment as paid
planner.mark_transaction_paid("Rent", 2025, 10)

# View unpaid transactions
unpaid = planner.get_unpaid_transactions()
for trans in unpaid:
    print(f"{trans.budget_item_name}: ${trans.amount}")

# Forecast balance
forecast = planner.forecast_balance(months_ahead=12)
for month in forecast:
    print(f"{month['month_name']}: ${month['projected_balance']:,.2f}")

# Save your budget
planner.save_to_file("my_budget.json")
```

## Key Concepts

### Budget Items

Budget items are templates for recurring income or expenses:

- **Name**: Descriptive name (e.g., "Electric Bill", "Salary")
- **Transaction Type**: INCOME or EXPENSE
- **Default Amount**: Standard monthly amount
- **Frequency**: MONTHLY or ONE_TIME
- **Category**: Grouping (e.g., "Utilities", "Housing")
- **Due Day**: Day of month (1-31)

### Transactions

Transactions are actual occurrences of budget items:

- Generated from budget items
- Can be marked as paid or unpaid
- Track payment dates
- Accumulate if unpaid

### Variable Amounts

Set custom amounts for specific months:

```python
# Electric bill varies by season
planner.set_custom_amount("Electric Bill", 2025, 7, 180.00)  # Summer
planner.set_custom_amount("Electric Bill", 2025, 12, 140.00) # Winter
planner.set_custom_amount("Electric Bill", 2025, 4, 100.00)  # Spring
```

### Unpaid Accumulation

When you don't pay a bill in a given month:

1. Transaction remains marked as "unpaid"
2. Amount accumulates in your total unpaid
3. Reduces your effective balance
4. Stays in the system until marked as paid
5. Shows up in reports and forecasts

Example:
```
October Electric Bill: $120 (unpaid)
November Electric Bill: $130 (unpaid)
Total accumulated: $250
```

### Balance Forecasting

Projects future balance based on:

- Your starting balance
- All paid transactions (actual money in/out)
- Accumulated unpaid amounts (debt)
- Planned future income and expenses

```python
forecast = planner.forecast_balance(months_ahead=12)
# Shows projected balance at end of each month
```

## Usage Examples

### Example 1: Basic Monthly Budget

```python
planner = BudgetPlanner(starting_balance=10000.00)

# Income
planner.add_budget_item(BudgetItem(
    name="Salary",
    transaction_type=TransactionType.INCOME,
    default_amount=5000.00,
    frequency=Frequency.MONTHLY
))

# Fixed expenses
planner.add_budget_item(BudgetItem(
    name="Rent",
    transaction_type=TransactionType.EXPENSE,
    default_amount=1500.00,
    frequency=Frequency.MONTHLY
))

# Generate and pay for October 2025
planner.generate_monthly_transactions(2025, 10)
planner.mark_transaction_paid("Salary", 2025, 10)
planner.mark_transaction_paid("Rent", 2025, 10)

# Check balance
print(planner.get_budget_report())
```

### Example 2: Variable Electric Bill

```python
planner.add_budget_item(BudgetItem(
    name="Electric",
    transaction_type=TransactionType.EXPENSE,
    default_amount=100.00,  # Base amount
    frequency=Frequency.MONTHLY
))

# Higher in summer (A/C usage)
for month in [6, 7, 8]:
    planner.set_custom_amount("Electric", 2025, month, 180.00)

# Lower in spring/fall
for month in [4, 5, 9, 10]:
    planner.set_custom_amount("Electric", 2025, month, 90.00)
```

### Example 3: Tracking Unpaid Bills

```python
# Generate last 3 months
for month in [8, 9, 10]:
    planner.generate_monthly_transactions(2025, month)

# Only paid some bills
planner.mark_transaction_paid("Salary", 2025, 8)
planner.mark_transaction_paid("Rent", 2025, 8)
# Forgot to pay electric in August!

planner.mark_transaction_paid("Salary", 2025, 9)
planner.mark_transaction_paid("Rent", 2025, 9)
planner.mark_transaction_paid("Electric", 2025, 9)

# View unpaid
unpaid = planner.get_unpaid_transactions()
# Shows: Electric (August) - still unpaid, accumulating
```

### Example 4: 12-Month Forecast

```python
# See your projected balance for the next year
forecast = planner.forecast_balance(12)

for entry in forecast:
    print(f"{entry['month_name']:>15}: "
          f"Income ${entry['planned_income']:>8,.2f} | "
          f"Expenses ${entry['planned_expenses']:>8,.2f} | "
          f"Balance ${entry['projected_balance']:>10,.2f}")
```

## File Structure

```
PersonalBudget/
├── budget_planner.py    # Core budget logic and classes
├── main.py              # Interactive CLI interface
├── example_demo.py      # Demonstration script
├── README.md            # This file
└── *.json              # Saved budget files
```

## Data Model

### BudgetItem
```python
{
    "name": "Electric Bill",
    "transaction_type": "expense",  # or "income"
    "default_amount": 100.00,
    "frequency": "monthly",  # or "one_time"
    "category": "Utilities",
    "due_day": 12
}
```

### Transaction
```python
{
    "budget_item_name": "Electric Bill",
    "amount": 120.00,
    "year": 2025,
    "month": 10,
    "paid": false,
    "paid_date": null,
    "notes": ""
}
```

### Saved Budget File
```json
{
    "starting_balance": 5000.00,
    "budget_items": { ... },
    "transactions": [ ... ],
    "custom_amounts": { ... }
}
```

## Tips and Best Practices

1. **Set Realistic Amounts**: Review past statements to set accurate default amounts

2. **Use Categories**: Group items logically (Housing, Food, Transportation, etc.)

3. **Regular Updates**: Mark transactions as paid regularly to maintain accuracy

4. **Plan for Variables**: Identify expenses that vary by season/month

5. **Review Forecasts**: Check 3-month and 12-month forecasts regularly

6. **Handle Unpaid Promptly**: Address accumulated unpaid amounts to maintain budget health

7. **Save Often**: Save your budget to file after making changes

8. **Multiple Scenarios**: Create different budget files for different scenarios

## CLI Menu Reference

```
1.  View Budget Report       - Comprehensive overview
2.  Add Budget Item          - Create new income/expense item
3.  View All Budget Items    - List all budget items
4.  Set Custom Amount        - Vary amount for specific month
5.  Generate Transactions    - Create transactions for a month
6.  Mark Transaction Paid    - Record payment
7.  View Unpaid Transactions - See accumulated unpaid amounts
8.  View Monthly Summary     - Detailed month view
9.  View Balance Forecast    - Project future balance
10. Save Budget to File      - Persist your budget
11. Load Budget from File    - Load saved budget
12. Set Starting Balance     - Update starting balance
0.  Exit
```

## Advanced Features

### Custom Monthly Amounts

Perfect for:
- Seasonal utility bills
- Variable income (freelance, commissions)
- Holiday shopping budgets
- Irregular medical expenses
- Annual or semi-annual payments

### Unpaid Transaction Management

Automatically handles:
- Missed payments that carry forward
- Accumulating debt tracking
- Impact on future balance projections
- Historical payment patterns

### Flexible Reporting

Multiple views:
- Full budget report with all details
- Monthly summaries (planned vs actual)
- Unpaid transaction list
- Multi-month balance forecast
- Category breakdowns

## Troubleshooting

**Q: Transactions not appearing?**
- Run "Generate Monthly Transactions" first (option 5)

**Q: Forecast seems wrong?**
- Check for unpaid transactions (option 7)
- Verify starting balance (option 12)
- Ensure all income/expenses are added

**Q: Can't mark transaction as paid?**
- Generate transactions for that month first
- Check the item name matches exactly

**Q: Lost my budget?**
- Load from saved file (option 11)
- Check for .json files in directory

## Future Enhancements

Potential additions:
- Multiple budget scenarios/profiles
- CSV import/export
- Graphical charts and visualizations
- Recurring one-time expenses
- Budget vs actual reporting
- Email/SMS payment reminders
- Multi-currency support
- Shared budgets for households

## License

This project is open source. Feel free to use, modify, and distribute.

## Support

For issues, questions, or suggestions:
1. Check this README
2. Review the example_demo.py for guidance
3. Examine the code comments in budget_planner.py

---

**Happy budgeting!** Take control of your finances with flexible, powerful planning tools.
