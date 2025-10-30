# Testing on Your Phone

## Quick Start (3 Steps)

### Step 1: Start the Server
On your computer, run:
```bash
cd PersonalBudget
./run_server.sh
```

OR simply:
```bash
python3 app.py
```

### Step 2: Find Your IP Address
The script will show your IP address automatically, or run:
```bash
hostname -I
```

### Step 3: Open on Your Phone
1. **Make sure your phone is on the SAME WiFi network as your computer**
2. Open your phone's browser (Chrome, Safari, etc.)
3. Type in the address bar:
   ```
   http://YOUR_IP_ADDRESS:5000
   ```

## Example

If your IP is `192.168.1.100`, go to:
```
http://192.168.1.100:5000
```

Based on your current setup, try:
```
http://21.0.0.28:5000
```

## Troubleshooting

### Can't Connect?
- ✓ Verify phone and computer are on the **same WiFi network**
- ✓ Check your computer's firewall isn't blocking port 5000
- ✓ Make sure the server is running (you should see Flask output)
- ✓ Try accessing `http://localhost:5000` on your computer first

### Still Not Working?
If you're on a restricted network or can't access via IP:

**Option 1: Use localhost (computer only)**
```
http://localhost:5000
```

**Option 2: Use a tunnel service (for remote testing)**
You can use tools like ngrok to create a public URL:
```bash
# Install ngrok, then run:
ngrok http 5000
```

**Option 3: Test in mobile view on computer**
Open the web app on your computer and use browser dev tools:
- Chrome: Press F12 → Click device toolbar icon
- Safari: Develop → Enter Responsive Design Mode
- Firefox: Ctrl+Shift+M

## What You'll See on Mobile

The app is fully responsive and optimized for mobile:
- ✓ Large, touch-friendly buttons
- ✓ Easy-to-read text
- ✓ Swipeable tabs
- ✓ Mobile-optimized forms
- ✓ Toast notifications
- ✓ Smooth animations

## Features to Test

1. **Dashboard Tab**
   - Set starting balance
   - View current month summary
   - See unpaid transactions
   - Generate transactions

2. **Budget Items Tab**
   - Add new income/expense items
   - View all items in cards
   - Delete items
   - Set custom monthly amounts

3. **Transactions Tab**
   - Mark transactions as paid
   - View unpaid items

4. **Forecast Tab**
   - See 12-month projection
   - Save/load budgets

Enjoy budgeting on the go! 📱💰
