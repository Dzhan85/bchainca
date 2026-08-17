# BChainCA - UI Documentation

## 🎨 User Interface Overview

BChainCA now features a modern, secure web interface with authentication and a comprehensive dashboard for managing blockchain PKI operations.

## 🔐 Authentication System

### Login Page

The application features a beautiful, animated login page with:

- **Secure Authentication**: Username and password-based login
- **Demo Accounts**: Pre-configured accounts for testing
- **Password Visibility Toggle**: Show/hide password feature
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Animated Background**: Blockchain-themed visual effects

### Demo Accounts

The system includes three pre-configured demo accounts for testing:

| Username | Password | Role | Access Level |
|----------|----------|------|--------------|
| `admin` | `admin123` | Administrator | Full access to all features |
| `user` | `user123` | User | Standard user access |
| `operator` | `operator123` | Operator | Operational access |

### Security Features

- **Session Management**: Secure token-based authentication
- **Route Protection**: All routes protected by AuthGuard
- **Auto-logout**: Session management with token validation
- **Secure Storage**: Credentials stored using browser localStorage
- **Password Protection**: Passwords masked by default

## 📊 Dashboard

The dashboard provides an at-a-glance view of your blockchain network:

### Key Features

1. **Welcome Section**
   - Personalized greeting based on time of day
   - User information display
   - Quick access to key features

2. **Statistics Cards**
   - **Total Blocks**: Current blockchain height
   - **Batches**: Number of batch transactions
   - **Transactions**: Total transaction count
   - **Network Status**: Real-time network connectivity

3. **Quick Actions**
   - **Explorer**: Browse blocks, batches, and transactions
   - **State Monitor**: Real-time blockchain state monitoring
   - **Certificates**: PKI certificate management
   - **Network Info**: View network nodes and status

4. **Recent Activity**
   - List of recent blocks
   - Block details with batch count
   - Quick navigation to block details
   - Link to full explorer

## 🧭 Navigation

### Top Navigation Bar

The navigation bar (visible when logged in) includes:

- **Logo**: BChainCA branding
- **Dashboard**: Quick access to dashboard
- **Explorer**: Blockchain explorer
- **State Monitor**: Real-time state monitoring
- **User Menu**: 
  - User name and role display
  - Email address
  - Logout option

## 🎨 Design System

### Color Palette

The application uses a modern gradient-based color scheme:

- **Primary Gradient**: Purple to blue (`#667eea` → `#764ba2`)
- **Secondary Gradient**: Pink to red (`#f093fb` → `#f5576c`)
- **Accent Gradient**: Blue to cyan (`#4facfe` → `#00f2fe`)
- **Success**: Green (`#4caf50`)
- **Error**: Red (`#f44336`)
- **Background**: Light gray (`#f5f7fa`)

### Typography

- **Headers**: System font stack for optimal readability
- **Body**: Clear, legible fonts
- **Monospace**: For blockchain addresses and hashes

### Components

Built using **Angular Material Design**:
- Cards for content grouping
- Buttons for actions
- Form fields for inputs
- Icons for visual clarity
- Snackbars for notifications
- Menus for user options
- Progress spinners for loading states

## 📱 Responsive Design

The UI is fully responsive and works across devices:

- **Desktop** (1200px+): Full layout with sidebar
- **Tablet** (768px - 1199px): Optimized layout
- **Mobile** (< 768px): Stacked layout with mobile menu

## 🚀 Usage Guide

### First Time Login

1. Navigate to `http://localhost:4200`
2. You'll be automatically redirected to `/login`
3. Click "Use" on any demo account or enter credentials manually
4. Click "Login" button
5. You'll be redirected to the Dashboard

### Using the Dashboard

1. **View Statistics**: See real-time blockchain metrics at the top
2. **Quick Actions**: Click any action card to navigate to that feature
3. **Recent Blocks**: Scroll through recent blockchain activity
4. **View Details**: Click "View Details" on any block for more information

### Navigating the Application

1. Use the **top navigation bar** to switch between sections
2. Click your **user avatar** in the top right to access user menu
3. Select **Logout** from user menu to sign out

### Explorer Features

Access the blockchain explorer from:
- Dashboard quick actions
- Top navigation bar
- Or navigate to `/explorer`

Features include:
- Browse all blocks
- View batch details
- Examine transactions
- Search by ID or hash

### State Monitor

Monitor blockchain state in real-time:
- Navigate from dashboard or top menu
- View current state data
- Monitor changes live
- Export state information

## 🔧 Configuration

### Changing Demo Accounts

Edit the demo accounts in `src/app/services/auth.service.ts`:

```typescript
private readonly DEMO_USERS = [
  { 
    username: 'admin', 
    password: 'admin123', 
    email: 'admin@bchainca.com', 
    role: 'Administrator' 
  },
  // Add more users...
];
```

### Customizing Theme

Modify colors in component SCSS files:

- Login: `src/app/login/login.component.scss`
- Dashboard: `src/app/dashboard/dashboard.component.scss`
- Global: `src/styles.scss`

### API Configuration

Update API endpoints in `src/app/services/api-service/api.service.ts`

## 🛡️ Security Considerations

### Production Deployment

⚠️ **IMPORTANT**: Before deploying to production:

1. **Replace Demo Authentication**
   - Implement proper backend authentication
   - Use JWT tokens from your backend
   - Remove hardcoded demo accounts
   - Implement password hashing

2. **Enable HTTPS**
   - Configure SSL/TLS certificates
   - Redirect HTTP to HTTPS
   - Use secure cookies

3. **Implement Rate Limiting**
   - Protect against brute force attacks
   - Limit failed login attempts
   - Add CAPTCHA if needed

4. **Session Management**
   - Implement session timeout
   - Add refresh token mechanism
   - Secure token storage

5. **Environment Variables**
   - Use environment variables for API URLs
   - Never commit credentials
   - Use different configs for dev/prod

### Best Practices

- ✅ Change default demo credentials
- ✅ Implement proper backend authentication
- ✅ Use HTTPS in production
- ✅ Enable CORS properly
- ✅ Validate all inputs
- ✅ Implement logging and monitoring
- ✅ Regular security audits
- ✅ Keep dependencies updated

## 🐛 Troubleshooting

### Login Issues

**Problem**: Cannot login with demo accounts
- **Solution**: Ensure you're using correct credentials from the demo account cards
- **Check**: Browser console for errors

**Problem**: Redirected to login after successful authentication
- **Solution**: Check if token is being stored in localStorage
- **Clear**: Browser cache and localStorage

### Navigation Issues

**Problem**: Navbar not showing
- **Solution**: Ensure you're on a protected route (not /login)
- **Check**: AuthGuard is properly configured

**Problem**: 404 errors on routes
- **Solution**: Verify routing module is properly configured
- **Check**: All components are declared in app.module.ts

### API Connection Issues

**Problem**: Dashboard showing "Offline" status
- **Solution**: Ensure Sawtooth REST API is running
- **Check**: API URL in environment configuration
- **Verify**: CORS headers are properly set

**Problem**: Cannot load blockchain data
- **Solution**: Start the Sawtooth network first
- **Check**: Docker containers are running
- **Verify**: Port 8008 is accessible

## 📚 Component Structure

```
src/app/
├── login/                    # Login page component
│   ├── login.component.ts
│   ├── login.component.html
│   └── login.component.scss
├── dashboard/                # Dashboard component
│   ├── dashboard.component.ts
│   ├── dashboard.component.html
│   └── dashboard.component.scss
├── services/
│   └── auth.service.ts      # Authentication service
├── guards/
│   └── auth.guard.ts        # Route guard
└── app.component.*          # Main app with navbar
```

## 🎯 Future Enhancements

Planned features for future releases:

- [ ] User registration
- [ ] Password reset functionality
- [ ] Two-factor authentication (2FA)
- [ ] User profile management
- [ ] Role-based access control (RBAC)
- [ ] Audit logging
- [ ] Real-time notifications
- [ ] Dark mode toggle
- [ ] Multi-language support
- [ ] Advanced search and filtering
- [ ] Export functionality
- [ ] Customizable dashboard widgets

## 📞 Support

For issues or questions:

1. Check this documentation
2. Review [README.md](README.md) for setup instructions
3. Check browser console for errors
4. Create an issue in the repository

## 🎓 Training Resources

- **Angular Material**: https://material.angular.io
- **Angular Routing**: https://angular.io/guide/router
- **Reactive Forms**: https://angular.io/guide/reactive-forms
- **Sawtooth REST API**: https://sawtooth.hyperledger.org/docs/

---

**Version**: 2.0.0  
**Last Updated**: August 17, 2026  
**Framework**: Angular 18 with Material Design
