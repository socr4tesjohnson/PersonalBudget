// API Base URL
const API_BASE = '/api';

// Initialize app on page load
document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    loadCurrentMonth();
    loadBudgetInfo();
    loadCurrentMonthSummary();
    loadUnpaidTransactions();
    setCurrentDateDefaults();
});

// Tab Management
function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.dataset.tab;

            // Remove active class from all
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // Add active class to clicked
            button.classList.add('active');
            document.getElementById(tabName).classList.add('active');

            // Load data when tab is opened
            if (tabName === 'budget-items') {
                loadBudgetItems();
                updateCustomItemDropdown();
            } else if (tabName === 'transactions') {
                loadUnpaidTransactionsForPayment();
            } else if (tabName === 'forecast') {
                loadForecast();
            }
        });
    });
}

// Toast Notifications
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.add('show');

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Set current date defaults
function setCurrentDateDefaults() {
    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth() + 1;

    document.getElementById('customYear').value = year;
    document.getElementById('customMonth').value = month;
    document.getElementById('viewYear').value = year;
    document.getElementById('viewMonth').value = month;

    // Set start month to current month
    const startMonthSelect = document.getElementById('itemStartMonth');
    if (startMonthSelect) {
        startMonthSelect.value = month;
    }
}

// Toggle start month visibility based on frequency
function toggleStartMonth() {
    const frequency = document.getElementById('itemFrequency').value;
    const startMonthGroup = document.getElementById('startMonthGroup');

    // Show start month for frequencies that use it
    const needsStartMonth = ['bimonthly', 'quarterly', 'semiannually', 'annually'];

    if (needsStartMonth.includes(frequency)) {
        startMonthGroup.style.display = 'block';
    } else {
        startMonthGroup.style.display = 'none';
    }
}

// Load current month info
async function loadCurrentMonth() {
    try {
        const response = await fetch(`${API_BASE}/current-month`);
        const data = await response.json();
        document.getElementById('currentMonthName').textContent = data.month_name;
    } catch (error) {
        console.error('Error loading current month:', error);
    }
}

// Load budget info
async function loadBudgetInfo() {
    try {
        const response = await fetch(`${API_BASE}/budget/info`);
        const data = await response.json();
        document.getElementById('balanceAmount').textContent = formatCurrency(data.starting_balance);
        document.getElementById('startingBalanceInput').value = data.starting_balance;
    } catch (error) {
        console.error('Error loading budget info:', error);
    }
}

// Set starting balance
async function setStartingBalance() {
    const balance = parseFloat(document.getElementById('startingBalanceInput').value);

    if (isNaN(balance)) {
        showToast('Please enter a valid number', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/budget/starting-balance`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ balance })
        });

        if (response.ok) {
            const data = await response.json();
            document.getElementById('balanceAmount').textContent = formatCurrency(data.balance);
            showToast('Starting balance updated!', 'success');
            loadCurrentMonthSummary();
            loadForecast();
        }
    } catch (error) {
        showToast('Error updating balance', 'error');
        console.error(error);
    }
}

// Add budget item
async function addBudgetItem(event) {
    event.preventDefault();

    const data = {
        name: document.getElementById('itemName').value,
        transaction_type: document.getElementById('itemType').value,
        default_amount: parseFloat(document.getElementById('itemAmount').value),
        frequency: document.getElementById('itemFrequency').value,
        category: document.getElementById('itemCategory').value,
        due_day: parseInt(document.getElementById('itemDueDay').value),
        start_month: parseInt(document.getElementById('itemStartMonth').value)
    };

    try {
        const response = await fetch(`${API_BASE}/budget-items`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            showToast('Budget item added!', 'success');
            document.getElementById('addBudgetItemForm').reset();
            loadBudgetItems();
            updateCustomItemDropdown();
        }
    } catch (error) {
        showToast('Error adding budget item', 'error');
        console.error(error);
    }
}

// Load budget items
async function loadBudgetItems() {
    try {
        const response = await fetch(`${API_BASE}/budget-items`);
        const items = await response.json();

        const container = document.getElementById('budgetItemsList');

        if (items.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📋</div>
                    <div class="empty-state-text">No budget items yet. Add your first one above!</div>
                </div>
            `;
            return;
        }

        container.innerHTML = items.map(item => `
            <div class="budget-item ${item.transaction_type}">
                <div class="budget-item-header">
                    <span class="budget-item-name">${item.name}</span>
                    <span class="budget-item-amount">${formatCurrency(item.default_amount)}</span>
                </div>
                <div class="budget-item-details">
                    <div class="budget-item-detail">
                        <strong>Type:</strong> ${item.transaction_type}
                    </div>
                    <div class="budget-item-detail">
                        <strong>Frequency:</strong> ${item.frequency}
                    </div>
                    <div class="budget-item-detail">
                        <strong>Category:</strong> ${item.category}
                    </div>
                    <div class="budget-item-detail">
                        <strong>Due Day:</strong> ${item.due_day}
                    </div>
                </div>
                <button class="btn btn-danger" onclick="deleteBudgetItem('${item.name}')">Delete</button>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading budget items:', error);
    }
}

// Delete budget item
async function deleteBudgetItem(itemName) {
    if (!confirm(`Delete "${itemName}"?`)) return;

    try {
        const response = await fetch(`${API_BASE}/budget-items/${encodeURIComponent(itemName)}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showToast('Budget item deleted!', 'success');
            loadBudgetItems();
            updateCustomItemDropdown();
        }
    } catch (error) {
        showToast('Error deleting budget item', 'error');
        console.error(error);
    }
}

// Update custom item dropdown
async function updateCustomItemDropdown() {
    try {
        const response = await fetch(`${API_BASE}/budget-items`);
        const items = await response.json();

        const select = document.getElementById('customItemName');
        select.innerHTML = '<option value="">Select item...</option>' +
            items.map(item => `<option value="${item.name}">${item.name}</option>`).join('');
    } catch (error) {
        console.error('Error updating dropdown:', error);
    }
}

// Set custom amount
async function setCustomAmount(event) {
    event.preventDefault();

    const data = {
        item_name: document.getElementById('customItemName').value,
        year: parseInt(document.getElementById('customYear').value),
        month: parseInt(document.getElementById('customMonth').value),
        amount: parseFloat(document.getElementById('customAmount').value)
    };

    try {
        const response = await fetch(`${API_BASE}/custom-amounts`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            showToast('Custom amount set!', 'success');
            document.getElementById('customAmountForm').reset();
        }
    } catch (error) {
        showToast('Error setting custom amount', 'error');
        console.error(error);
    }
}

// Generate current month transactions
async function generateCurrentMonthTransactions() {
    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth() + 1;

    try {
        const response = await fetch(`${API_BASE}/transactions/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ year, month })
        });

        if (response.ok) {
            showToast('Transactions generated!', 'success');
            loadCurrentMonthSummary();
            loadUnpaidTransactions();
        }
    } catch (error) {
        showToast('Error generating transactions', 'error');
        console.error(error);
    }
}

// Load current month summary
async function loadCurrentMonthSummary() {
    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth() + 1;

    try {
        const response = await fetch(`${API_BASE}/summary/monthly?year=${year}&month=${month}`);
        const summary = await response.json();

        document.getElementById('plannedIncome').textContent = formatCurrency(summary.planned_income);
        document.getElementById('plannedExpenses').textContent = formatCurrency(summary.planned_expenses);
        document.getElementById('plannedNet').textContent = formatCurrency(summary.planned_net);
        document.getElementById('paidIncome').textContent = formatCurrency(summary.paid_income);
        document.getElementById('paidExpenses').textContent = formatCurrency(summary.paid_expenses);
        document.getElementById('paidNet').textContent = formatCurrency(summary.paid_net);
        document.getElementById('unpaidExpenses').textContent = formatCurrency(summary.unpaid_expenses);
    } catch (error) {
        console.error('Error loading monthly summary:', error);
    }
}

// Load unpaid transactions
async function loadUnpaidTransactions() {
    try {
        const response = await fetch(`${API_BASE}/transactions/unpaid`);
        const data = await response.json();

        const container = document.getElementById('unpaidTransactionsList');

        if (data.transactions.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">✅</div>
                    <div class="empty-state-text">No unpaid transactions! You're all caught up!</div>
                </div>
            `;
            document.getElementById('totalUnpaid').textContent = 'Total Accumulated: $0.00';
            return;
        }

        container.innerHTML = data.transactions.map(trans => `
            <div class="transaction-item">
                <div class="transaction-info">
                    <div class="transaction-name">${trans.budget_item_name}</div>
                    <div class="transaction-date">${trans.year}/${String(trans.month).padStart(2, '0')}</div>
                </div>
                <div class="transaction-amount">${formatCurrency(trans.amount)}</div>
            </div>
        `).join('');

        document.getElementById('totalUnpaid').textContent =
            `Total Accumulated: ${formatCurrency(data.total_unpaid)}`;
    } catch (error) {
        console.error('Error loading unpaid transactions:', error);
    }
}

// Load unpaid transactions for payment
async function loadUnpaidTransactionsForPayment() {
    try {
        const response = await fetch(`${API_BASE}/transactions/unpaid`);
        const data = await response.json();

        const container = document.getElementById('unpaidTransactionsForPayment');

        if (data.transactions.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">✅</div>
                    <div class="empty-state-text">No unpaid transactions!</div>
                </div>
            `;
            return;
        }

        container.innerHTML = data.transactions.map(trans => `
            <div class="transaction-item">
                <div class="transaction-info">
                    <div class="transaction-name">${trans.budget_item_name}</div>
                    <div class="transaction-date">${trans.year}/${String(trans.month).padStart(2, '0')}</div>
                </div>
                <div class="transaction-amount">${formatCurrency(trans.amount)}</div>
                <div class="transaction-actions">
                    <button class="btn btn-success"
                            onclick="markAsPaid('${trans.budget_item_name}', ${trans.year}, ${trans.month})">
                        Mark Paid
                    </button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading unpaid transactions:', error);
    }
}

// Mark transaction as paid
async function markAsPaid(itemName, year, month) {
    try {
        const response = await fetch(`${API_BASE}/transactions/mark-paid`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ item_name: itemName, year, month })
        });

        if (response.ok) {
            showToast('Transaction marked as paid!', 'success');
            loadUnpaidTransactions();
            loadUnpaidTransactionsForPayment();
            loadCurrentMonthSummary();
            loadForecast();
        }
    } catch (error) {
        showToast('Error marking transaction as paid', 'error');
        console.error(error);
    }
}

// View month transactions
async function viewMonthTransactions() {
    const year = parseInt(document.getElementById('viewYear').value);
    const month = parseInt(document.getElementById('viewMonth').value);

    try {
        const response = await fetch(`${API_BASE}/summary/monthly?year=${year}&month=${month}`);
        const summary = await response.json();

        const message = `
            ${summary.month_name}

            Planned Income: ${formatCurrency(summary.planned_income)}
            Planned Expenses: ${formatCurrency(summary.planned_expenses)}
            Planned Net: ${formatCurrency(summary.planned_net)}

            Paid Income: ${formatCurrency(summary.paid_income)}
            Paid Expenses: ${formatCurrency(summary.paid_expenses)}
            Paid Net: ${formatCurrency(summary.paid_net)}

            Unpaid Income: ${formatCurrency(summary.unpaid_income)}
            Unpaid Expenses: ${formatCurrency(summary.unpaid_expenses)}
        `;

        alert(message);
    } catch (error) {
        showToast('Error loading month summary', 'error');
        console.error(error);
    }
}

// Load forecast
async function loadForecast() {
    const months = parseInt(document.getElementById('forecastMonths').value) || 12;

    try {
        const response = await fetch(`${API_BASE}/forecast?months=${months}`);
        const forecast = await response.json();

        const container = document.getElementById('forecastDisplay');

        if (forecast.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-text">Add budget items to see forecast</div>
                </div>
            `;
            return;
        }

        container.innerHTML = `
            <div class="forecast-table">
                <div class="forecast-row header">
                    <div class="forecast-cell">Month</div>
                    <div class="forecast-cell">Income</div>
                    <div class="forecast-cell">Expenses</div>
                    <div class="forecast-cell">Balance</div>
                </div>
                ${forecast.map(entry => `
                    <div class="forecast-row">
                        <div class="forecast-cell month">${entry.month_name}</div>
                        <div class="forecast-cell">${formatCurrency(entry.planned_income)}</div>
                        <div class="forecast-cell">${formatCurrency(entry.planned_expenses)}</div>
                        <div class="forecast-cell ${entry.projected_balance >= 0 ? 'positive' : 'negative'}">
                            ${formatCurrency(entry.projected_balance)}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    } catch (error) {
        console.error('Error loading forecast:', error);
    }
}

// Save budget
async function saveBudget() {
    const filename = document.getElementById('budgetFilename').value.trim() || 'budget';

    try {
        const response = await fetch(`${API_BASE}/budget/save`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename })
        });

        if (response.ok) {
            showToast('Budget saved!', 'success');
            listBudgetFiles();
        }
    } catch (error) {
        showToast('Error saving budget', 'error');
        console.error(error);
    }
}

// Load budget
async function loadBudget() {
    const filename = document.getElementById('budgetFilename').value.trim() || 'budget';

    try {
        const response = await fetch(`${API_BASE}/budget/load`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename })
        });

        if (response.ok) {
            showToast('Budget loaded!', 'success');
            loadBudgetInfo();
            loadBudgetItems();
            loadCurrentMonthSummary();
            loadUnpaidTransactions();
            loadForecast();
        } else {
            showToast('Budget file not found', 'error');
        }
    } catch (error) {
        showToast('Error loading budget', 'error');
        console.error(error);
    }
}

// List budget files
async function listBudgetFiles() {
    try {
        const response = await fetch(`${API_BASE}/budget/files`);
        const files = await response.json();

        const container = document.getElementById('budgetFilesList');

        if (files.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-text">No saved budgets yet</div>
                </div>
            `;
            return;
        }

        container.innerHTML = `
            <div style="margin-top: 15px;">
                <h3>Saved Budgets:</h3>
                ${files.map(file => `
                    <div class="budget-item">
                        <div class="budget-item-header">
                            <span class="budget-item-name">${file}</span>
                            <button class="btn btn-secondary"
                                    onclick="document.getElementById('budgetFilename').value='${file.replace('.json', '')}'; loadBudget();">
                                Load
                            </button>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    } catch (error) {
        console.error('Error listing budget files:', error);
    }
}

// Utility: Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}
