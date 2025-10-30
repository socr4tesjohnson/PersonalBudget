"""
Personal Budget Planner
A flexible budget management system that tracks monthly budgets, handles unpaid amounts,
supports variable expenses, and forecasts account balance.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import defaultdict


class TransactionType(Enum):
    INCOME = "income"
    EXPENSE = "expense"


class Frequency(Enum):
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    BIMONTHLY = "bimonthly"  # Every 2 months
    QUARTERLY = "quarterly"  # Every 3 months
    SEMIANNUALLY = "semiannually"  # Every 6 months
    ANNUALLY = "annually"
    ONE_TIME = "one_time"


@dataclass
class BudgetItem:
    """Represents a budget item (income or expense)"""
    name: str
    transaction_type: TransactionType
    default_amount: float
    frequency: Frequency
    category: str = "General"
    due_day: int = 1  # Day of month (1-31)
    start_month: int = 1  # Starting month for recurring patterns (1-12)

    def get_amount_for_month(self, year: int, month: int, custom_amounts: Dict = None) -> float:
        """Get amount for specific month, allowing for variable amounts"""
        if custom_amounts and f"{year}-{month:02d}" in custom_amounts:
            return custom_amounts[f"{year}-{month:02d}"]
        return self.default_amount

    def should_generate_for_month(self, year: int, month: int) -> bool:
        """Determine if transaction should be generated for this month based on frequency"""
        if self.frequency == Frequency.MONTHLY:
            return True
        elif self.frequency == Frequency.WEEKLY or self.frequency == Frequency.BIWEEKLY:
            return True  # Weekly/biweekly generate every month
        elif self.frequency == Frequency.BIMONTHLY:
            # Every 2 months starting from start_month
            months_since_start = (month - self.start_month) % 12
            return months_since_start % 2 == 0
        elif self.frequency == Frequency.QUARTERLY:
            # Every 3 months starting from start_month
            months_since_start = (month - self.start_month) % 12
            return months_since_start % 3 == 0
        elif self.frequency == Frequency.SEMIANNUALLY:
            # Every 6 months starting from start_month
            months_since_start = (month - self.start_month) % 12
            return months_since_start % 6 == 0
        elif self.frequency == Frequency.ANNUALLY:
            # Once per year in the start_month
            return month == self.start_month
        elif self.frequency == Frequency.ONE_TIME:
            return False  # One-time items handled separately
        return False

    def get_occurrences_in_month(self, year: int, month: int) -> int:
        """Get number of times this item occurs in the given month"""
        if self.frequency == Frequency.WEEKLY:
            # Calculate weeks in month (approximately 4-5)
            import calendar
            days_in_month = calendar.monthrange(year, month)[1]
            return days_in_month // 7  # Roughly 4 per month
        elif self.frequency == Frequency.BIWEEKLY:
            # Biweekly is roughly 2 per month
            return 2
        else:
            # All other frequencies: 1 occurrence per applicable month
            return 1 if self.should_generate_for_month(year, month) else 0


@dataclass
class Transaction:
    """Represents an actual transaction/payment"""
    budget_item_name: str
    amount: float
    year: int
    month: int
    paid: bool = False
    paid_date: Optional[datetime] = None
    notes: str = ""

    def mark_paid(self, date: Optional[datetime] = None):
        """Mark transaction as paid"""
        self.paid = True
        self.paid_date = date or datetime.now()


class BudgetPlanner:
    """Main budget planner class"""

    def __init__(self, starting_balance: float = 0.0):
        self.budget_items: Dict[str, BudgetItem] = {}
        self.transactions: List[Transaction] = []
        self.custom_amounts: Dict[str, Dict[str, float]] = defaultdict(dict)  # item_name -> {month_key -> amount}
        self.starting_balance = starting_balance

    def add_budget_item(self, item: BudgetItem):
        """Add a budget item"""
        self.budget_items[item.name] = item

    def set_custom_amount(self, item_name: str, year: int, month: int, amount: float):
        """Set a custom amount for a specific month (e.g., higher electric bill in summer)"""
        month_key = f"{year}-{month:02d}"
        self.custom_amounts[item_name][month_key] = amount

    def add_transaction(self, transaction: Transaction):
        """Add a transaction"""
        self.transactions.append(transaction)

    def generate_monthly_transactions(self, year: int, month: int):
        """Generate expected transactions for a given month based on budget items"""
        for item_name, item in self.budget_items.items():
            # Get number of occurrences for this item in this month
            occurrences = item.get_occurrences_in_month(year, month)

            if occurrences > 0:
                # Check if transaction already exists
                existing = self._find_transaction(item_name, year, month)
                if not existing:
                    # For weekly/biweekly, multiply amount by occurrences
                    base_amount = item.get_amount_for_month(year, month, self.custom_amounts.get(item_name))

                    if item.frequency in [Frequency.WEEKLY, Frequency.BIWEEKLY]:
                        # Generate single transaction with total amount for the month
                        total_amount = base_amount * occurrences
                        transaction = Transaction(
                            budget_item_name=item_name,
                            amount=total_amount,
                            year=year,
                            month=month,
                            paid=False,
                            notes=f"{occurrences}x {item.frequency.value}"
                        )
                        self.transactions.append(transaction)
                    else:
                        # For other frequencies, single occurrence
                        transaction = Transaction(
                            budget_item_name=item_name,
                            amount=base_amount,
                            year=year,
                            month=month,
                            paid=False
                        )
                        self.transactions.append(transaction)

    def _find_transaction(self, item_name: str, year: int, month: int) -> Optional[Transaction]:
        """Find a transaction for a specific item and month"""
        for trans in self.transactions:
            if trans.budget_item_name == item_name and trans.year == year and trans.month == month:
                return trans
        return None

    def mark_transaction_paid(self, item_name: str, year: int, month: int, paid_date: Optional[datetime] = None):
        """Mark a transaction as paid"""
        transaction = self._find_transaction(item_name, year, month)
        if transaction:
            transaction.mark_paid(paid_date)
            return True
        return False

    def get_unpaid_transactions(self, up_to_year: int = None, up_to_month: int = None) -> List[Transaction]:
        """Get all unpaid transactions up to a specific month"""
        if up_to_year is None:
            now = datetime.now()
            up_to_year = now.year
            up_to_month = now.month

        unpaid = []
        for trans in self.transactions:
            if not trans.paid:
                # Check if transaction is due
                if trans.year < up_to_year or (trans.year == up_to_year and trans.month <= up_to_month):
                    unpaid.append(trans)
        return unpaid

    def get_accumulated_unpaid_amount(self, transaction_type: TransactionType = None) -> float:
        """Calculate total unpaid amount (accumulated debt)"""
        unpaid = self.get_unpaid_transactions()
        total = 0.0

        for trans in unpaid:
            if transaction_type is None:
                item = self.budget_items.get(trans.budget_item_name)
                if item:
                    if item.transaction_type == TransactionType.EXPENSE:
                        total += trans.amount
            elif self.budget_items.get(trans.budget_item_name).transaction_type == transaction_type:
                total += trans.amount

        return total

    def get_monthly_summary(self, year: int, month: int) -> Dict:
        """Get summary for a specific month"""
        # Generate transactions if not already present
        self.generate_monthly_transactions(year, month)

        income = 0.0
        expenses = 0.0
        paid_income = 0.0
        paid_expenses = 0.0
        unpaid_income = 0.0
        unpaid_expenses = 0.0

        month_transactions = [t for t in self.transactions if t.year == year and t.month == month]

        for trans in month_transactions:
            item = self.budget_items.get(trans.budget_item_name)
            if not item:
                continue

            if item.transaction_type == TransactionType.INCOME:
                income += trans.amount
                if trans.paid:
                    paid_income += trans.amount
                else:
                    unpaid_income += trans.amount
            else:
                expenses += trans.amount
                if trans.paid:
                    paid_expenses += trans.amount
                else:
                    unpaid_expenses += trans.amount

        return {
            'year': year,
            'month': month,
            'planned_income': income,
            'planned_expenses': expenses,
            'planned_net': income - expenses,
            'paid_income': paid_income,
            'paid_expenses': paid_expenses,
            'paid_net': paid_income - paid_expenses,
            'unpaid_income': unpaid_income,
            'unpaid_expenses': unpaid_expenses,
            'transactions': month_transactions
        }

    def forecast_balance(self, months_ahead: int = 12, assume_all_paid: bool = False) -> List[Dict]:
        """Forecast balance for upcoming months"""
        now = datetime.now()
        current_year = now.year
        current_month = now.month

        # Calculate current balance
        balance = self.starting_balance

        # Add/subtract all paid transactions
        for trans in self.transactions:
            if trans.paid:
                item = self.budget_items.get(trans.budget_item_name)
                if item:
                    if item.transaction_type == TransactionType.INCOME:
                        balance += trans.amount
                    else:
                        balance -= trans.amount

        # Subtract accumulated unpaid expenses (debt)
        if not assume_all_paid:
            balance -= self.get_accumulated_unpaid_amount(TransactionType.EXPENSE)

        forecast = []

        for i in range(months_ahead):
            # Calculate target month
            target_month = current_month + i
            target_year = current_year

            while target_month > 12:
                target_month -= 12
                target_year += 1

            # Generate transactions for this month
            self.generate_monthly_transactions(target_year, target_month)
            summary = self.get_monthly_summary(target_year, target_month)

            # If we're forecasting, assume future transactions will be paid
            if i > 0 or assume_all_paid:
                month_net = summary['planned_net']
            else:
                # For current month, only count paid transactions
                month_net = summary['paid_net']

            balance += month_net

            forecast.append({
                'year': target_year,
                'month': target_month,
                'month_name': datetime(target_year, target_month, 1).strftime('%B %Y'),
                'planned_income': summary['planned_income'],
                'planned_expenses': summary['planned_expenses'],
                'net': month_net,
                'projected_balance': balance
            })

        return forecast

    def get_budget_report(self) -> str:
        """Generate a comprehensive budget report"""
        report = []
        report.append("=" * 80)
        report.append("PERSONAL BUDGET PLANNER - COMPREHENSIVE REPORT")
        report.append("=" * 80)
        report.append("")

        # Budget Items
        report.append("BUDGET ITEMS:")
        report.append("-" * 80)
        for name, item in self.budget_items.items():
            report.append(f"  {name}")
            report.append(f"    Type: {item.transaction_type.value.title()}")
            report.append(f"    Default Amount: ${item.default_amount:,.2f}")
            report.append(f"    Frequency: {item.frequency.value.title()}")
            report.append(f"    Category: {item.category}")
            report.append(f"    Due Day: {item.due_day}")
            report.append("")

        # Unpaid Transactions
        unpaid = self.get_unpaid_transactions()
        if unpaid:
            report.append("")
            report.append("UNPAID TRANSACTIONS (ACCUMULATED):")
            report.append("-" * 80)
            total_unpaid = 0.0
            for trans in sorted(unpaid, key=lambda t: (t.year, t.month)):
                item = self.budget_items.get(trans.budget_item_name)
                if item and item.transaction_type == TransactionType.EXPENSE:
                    total_unpaid += trans.amount
                    report.append(f"  {trans.budget_item_name} - {trans.year}/{trans.month:02d}: ${trans.amount:,.2f}")
            report.append(f"\n  TOTAL ACCUMULATED UNPAID: ${total_unpaid:,.2f}")
            report.append("")

        # Current Month Summary
        now = datetime.now()
        current_summary = self.get_monthly_summary(now.year, now.month)
        report.append(f"CURRENT MONTH ({now.strftime('%B %Y')}):")
        report.append("-" * 80)
        report.append(f"  Planned Income:   ${current_summary['planned_income']:>12,.2f}")
        report.append(f"  Planned Expenses: ${current_summary['planned_expenses']:>12,.2f}")
        report.append(f"  Planned Net:      ${current_summary['planned_net']:>12,.2f}")
        report.append("")
        report.append(f"  Paid Income:      ${current_summary['paid_income']:>12,.2f}")
        report.append(f"  Paid Expenses:    ${current_summary['paid_expenses']:>12,.2f}")
        report.append(f"  Paid Net:         ${current_summary['paid_net']:>12,.2f}")
        report.append("")
        report.append(f"  Unpaid Income:    ${current_summary['unpaid_income']:>12,.2f}")
        report.append(f"  Unpaid Expenses:  ${current_summary['unpaid_expenses']:>12,.2f}")
        report.append("")

        # Balance Forecast
        report.append("BALANCE FORECAST (12 Months):")
        report.append("-" * 80)
        forecast = self.forecast_balance(12)
        for entry in forecast:
            report.append(f"  {entry['month_name']:>15}: "
                         f"Income ${entry['planned_income']:>10,.2f} | "
                         f"Expenses ${entry['planned_expenses']:>10,.2f} | "
                         f"Net ${entry['net']:>10,.2f} | "
                         f"Balance ${entry['projected_balance']:>12,.2f}")

        report.append("")
        report.append("=" * 80)

        return "\n".join(report)

    def save_to_file(self, filename: str):
        """Save budget data to JSON file"""
        data = {
            'starting_balance': self.starting_balance,
            'budget_items': {
                name: {
                    'name': item.name,
                    'transaction_type': item.transaction_type.value,
                    'default_amount': item.default_amount,
                    'frequency': item.frequency.value,
                    'category': item.category,
                    'due_day': item.due_day,
                    'start_month': item.start_month
                }
                for name, item in self.budget_items.items()
            },
            'transactions': [
                {
                    'budget_item_name': t.budget_item_name,
                    'amount': t.amount,
                    'year': t.year,
                    'month': t.month,
                    'paid': t.paid,
                    'paid_date': t.paid_date.isoformat() if t.paid_date else None,
                    'notes': t.notes
                }
                for t in self.transactions
            ],
            'custom_amounts': dict(self.custom_amounts)
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

    def load_from_file(self, filename: str):
        """Load budget data from JSON file"""
        with open(filename, 'r') as f:
            data = json.load(f)

        self.starting_balance = data.get('starting_balance', 0.0)

        # Load budget items
        for item_data in data.get('budget_items', {}).values():
            item = BudgetItem(
                name=item_data['name'],
                transaction_type=TransactionType(item_data['transaction_type']),
                default_amount=item_data['default_amount'],
                frequency=Frequency(item_data['frequency']),
                category=item_data.get('category', 'General'),
                due_day=item_data.get('due_day', 1),
                start_month=item_data.get('start_month', 1)
            )
            self.budget_items[item.name] = item

        # Load transactions
        self.transactions = []
        for trans_data in data.get('transactions', []):
            trans = Transaction(
                budget_item_name=trans_data['budget_item_name'],
                amount=trans_data['amount'],
                year=trans_data['year'],
                month=trans_data['month'],
                paid=trans_data['paid'],
                paid_date=datetime.fromisoformat(trans_data['paid_date']) if trans_data['paid_date'] else None,
                notes=trans_data.get('notes', '')
            )
            self.transactions.append(trans)

        # Load custom amounts
        self.custom_amounts = defaultdict(dict, data.get('custom_amounts', {}))
