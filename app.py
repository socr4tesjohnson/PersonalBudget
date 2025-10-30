#!/usr/bin/env python3
"""
Flask Web Application for Personal Budget Planner
Provides a responsive web interface with REST API
"""

from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import json
import os
from budget_planner import (
    BudgetPlanner, BudgetItem, Transaction,
    TransactionType, Frequency
)

app = Flask(__name__)
app.secret_key = os.urandom(24)

# In-memory storage (in production, use database)
budgets = {}

def get_budget():
    """Get or create budget for current session"""
    session_id = session.get('session_id')
    if not session_id:
        session_id = os.urandom(16).hex()
        session['session_id'] = session_id

    if session_id not in budgets:
        budgets[session_id] = BudgetPlanner(starting_balance=0.0)

    return budgets[session_id]


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/budget/info', methods=['GET'])
def get_budget_info():
    """Get budget basic info"""
    planner = get_budget()
    return jsonify({
        'starting_balance': planner.starting_balance,
        'budget_items_count': len(planner.budget_items),
        'transactions_count': len(planner.transactions)
    })


@app.route('/api/budget/starting-balance', methods=['POST'])
def set_starting_balance():
    """Set starting balance"""
    planner = get_budget()
    data = request.json
    planner.starting_balance = float(data['balance'])
    return jsonify({'success': True, 'balance': planner.starting_balance})


@app.route('/api/budget-items', methods=['GET'])
def get_budget_items():
    """Get all budget items"""
    planner = get_budget()
    items = []
    for name, item in planner.budget_items.items():
        items.append({
            'name': item.name,
            'transaction_type': item.transaction_type.value,
            'default_amount': item.default_amount,
            'frequency': item.frequency.value,
            'category': item.category,
            'due_day': item.due_day
        })
    return jsonify(items)


@app.route('/api/budget-items', methods=['POST'])
def add_budget_item():
    """Add a new budget item"""
    planner = get_budget()
    data = request.json

    item = BudgetItem(
        name=data['name'],
        transaction_type=TransactionType(data['transaction_type']),
        default_amount=float(data['default_amount']),
        frequency=Frequency(data['frequency']),
        category=data.get('category', 'General'),
        due_day=int(data.get('due_day', 1))
    )

    planner.add_budget_item(item)
    return jsonify({'success': True, 'message': f'Budget item "{item.name}" added'})


@app.route('/api/budget-items/<item_name>', methods=['DELETE'])
def delete_budget_item(item_name):
    """Delete a budget item"""
    planner = get_budget()
    if item_name in planner.budget_items:
        del planner.budget_items[item_name]
        return jsonify({'success': True, 'message': f'Budget item "{item_name}" deleted'})
    return jsonify({'success': False, 'message': 'Item not found'}), 404


@app.route('/api/custom-amounts', methods=['POST'])
def set_custom_amount():
    """Set custom amount for a specific month"""
    planner = get_budget()
    data = request.json

    planner.set_custom_amount(
        data['item_name'],
        int(data['year']),
        int(data['month']),
        float(data['amount'])
    )

    return jsonify({'success': True, 'message': 'Custom amount set'})


@app.route('/api/transactions/generate', methods=['POST'])
def generate_transactions():
    """Generate transactions for a month"""
    planner = get_budget()
    data = request.json

    year = int(data['year'])
    month = int(data['month'])

    planner.generate_monthly_transactions(year, month)
    return jsonify({'success': True, 'message': f'Transactions generated for {year}-{month:02d}'})


@app.route('/api/transactions/unpaid', methods=['GET'])
def get_unpaid_transactions():
    """Get all unpaid transactions"""
    planner = get_budget()
    unpaid = planner.get_unpaid_transactions()

    transactions = []
    for trans in sorted(unpaid, key=lambda t: (t.year, t.month)):
        item = planner.budget_items.get(trans.budget_item_name)
        transactions.append({
            'budget_item_name': trans.budget_item_name,
            'amount': trans.amount,
            'year': trans.year,
            'month': trans.month,
            'transaction_type': item.transaction_type.value if item else 'unknown'
        })

    total_unpaid = planner.get_accumulated_unpaid_amount(TransactionType.EXPENSE)

    return jsonify({
        'transactions': transactions,
        'total_unpaid': total_unpaid
    })


@app.route('/api/transactions/mark-paid', methods=['POST'])
def mark_transaction_paid():
    """Mark a transaction as paid"""
    planner = get_budget()
    data = request.json

    success = planner.mark_transaction_paid(
        data['item_name'],
        int(data['year']),
        int(data['month'])
    )

    if success:
        return jsonify({'success': True, 'message': 'Transaction marked as paid'})
    return jsonify({'success': False, 'message': 'Transaction not found'}), 404


@app.route('/api/summary/monthly', methods=['GET'])
def get_monthly_summary():
    """Get summary for a specific month"""
    planner = get_budget()
    year = int(request.args.get('year'))
    month = int(request.args.get('month'))

    summary = planner.get_monthly_summary(year, month)

    # Convert transactions to serializable format
    transactions = []
    for trans in summary['transactions']:
        item = planner.budget_items.get(trans.budget_item_name)
        transactions.append({
            'budget_item_name': trans.budget_item_name,
            'amount': trans.amount,
            'paid': trans.paid,
            'transaction_type': item.transaction_type.value if item else 'unknown',
            'category': item.category if item else 'Unknown'
        })

    summary['transactions'] = transactions
    summary['month_name'] = datetime(year, month, 1).strftime('%B %Y')

    return jsonify(summary)


@app.route('/api/forecast', methods=['GET'])
def get_forecast():
    """Get balance forecast"""
    planner = get_budget()
    months = int(request.args.get('months', 12))

    forecast = planner.forecast_balance(months)
    return jsonify(forecast)


@app.route('/api/budget/save', methods=['POST'])
def save_budget():
    """Save budget to file"""
    planner = get_budget()
    data = request.json
    filename = data.get('filename', 'budget.json')

    # Ensure filename ends with .json
    if not filename.endswith('.json'):
        filename += '.json'

    # Save to user_budgets directory
    os.makedirs('user_budgets', exist_ok=True)
    filepath = os.path.join('user_budgets', filename)

    planner.save_to_file(filepath)
    return jsonify({'success': True, 'message': f'Budget saved to {filename}'})


@app.route('/api/budget/load', methods=['POST'])
def load_budget():
    """Load budget from file"""
    planner = get_budget()
    data = request.json
    filename = data.get('filename', 'budget.json')

    # Ensure filename ends with .json
    if not filename.endswith('.json'):
        filename += '.json'

    filepath = os.path.join('user_budgets', filename)

    try:
        planner.load_from_file(filepath)
        return jsonify({'success': True, 'message': f'Budget loaded from {filename}'})
    except FileNotFoundError:
        return jsonify({'success': False, 'message': 'File not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@app.route('/api/budget/files', methods=['GET'])
def list_budget_files():
    """List available budget files"""
    os.makedirs('user_budgets', exist_ok=True)
    files = [f for f in os.listdir('user_budgets') if f.endswith('.json')]
    return jsonify(files)


@app.route('/api/current-month', methods=['GET'])
def get_current_month():
    """Get current year and month"""
    now = datetime.now()
    return jsonify({
        'year': now.year,
        'month': now.month,
        'month_name': now.strftime('%B %Y')
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
