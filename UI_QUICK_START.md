# 🚀 Quick Start - BChainCA UI

## Start the Application

```bash
# Install dependencies (if not already done)
npm install

# Start the Angular development server
npm start

# Application will open at http://localhost:4200
```

## Login to the System

### Option 1: Use Demo Accounts (Quick)

When you see the login page, click **"Use"** button on any demo account:

- **Admin Account**: Full access
  - Username: `admin`
  - Password: `admin123`

- **User Account**: Standard access
  - Username: `user`
  - Password: `user123`

- **Operator Account**: Operational access
  - Username: `operator`
  - Password: `operator123`

### Option 2: Manual Login

1. Enter username in the first field
2. Enter password in the second field
3. Click the **"Login"** button

## After Login

You'll be redirected to the **Dashboard** where you can:

1. **View Statistics** - See blockchain metrics (blocks, batches, transactions)
2. **Quick Actions** - Access main features:
   - Explorer
   - State Monitor
   - Certificates
   - Network Info
3. **Recent Activity** - View recent blocks

## Navigation

Use the top navigation bar to access:
- **Dashboard** - Home page with overview
- **Explorer** - Browse blockchain data
- **State Monitor** - Real-time state monitoring

## User Menu

Click on your **user avatar** (top right) to:
- View your email
- **Logout** from the system

## Screenshots

### Login Page
- Beautiful animated background with blockchain nodes
- Demo accounts for quick access
- Password visibility toggle
- Responsive design

### Dashboard
- Welcome section with personalized greeting
- Statistics cards showing network metrics
- Quick action cards for navigation
- Recent blocks list with details

## Troubleshooting

### Can't see login page?
- Ensure Angular dev server is running (`npm start`)
- Open browser to `http://localhost:4200`

### Login button not working?
- Fill in both username and password fields
- Use one of the demo accounts listed above

### Redirected to login after successful login?
- Clear browser cache: `Ctrl+Shift+Delete` (Windows) or `Cmd+Shift+Delete` (Mac)
- Try incognito/private browsing mode

### Dashboard shows "Offline"?
- Start the Sawtooth blockchain network first:
  ```bash
  python main.py --node_count 2 --load 100
  ```
- Ensure port 8008 is accessible

## Next Steps

1. ✅ Explore the blockchain using the Explorer
2. ✅ Monitor state changes in real-time
3. ✅ View block details and transactions
4. ✅ Check network status

## Need Help?

- 📖 Read [UI_DOCUMENTATION.md](UI_DOCUMENTATION.md) for detailed guide
- 📚 Check [README.md](README.md) for complete setup
- 🔍 Review browser console for errors

---

**Enjoy exploring your blockchain! 🎉**
