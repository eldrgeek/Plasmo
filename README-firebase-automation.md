# Firebase Console Automation

Automate Firebase Console tasks using Playwright web automation.

## Setup

1. Install dependencies:
```bash
npm install
npm run install-browser
```

2. Configure your project settings in `firebase-automation-example.js`

## What Can Be Automated

✅ **Fully Automated:**
- Create new web apps
- Configure Firebase Hosting
- Enable Authentication providers (Email/Password, Google, GitHub, etc.)
- Set up Firestore Database
- Configure Firebase Storage
- Set up Cloud Functions (billing permitting)
- Add custom domains (DNS records provided)
- Extract and save Firebase config files

⚠️ **Partially Automated:**
- OAuth provider setup (requires external app creation)
- Custom domain verification (requires DNS changes)
- Analytics integration (requires Google Analytics setup)

❌ **Cannot Automate:**
- Creating Firebase project (use GCP CLI instead)
- Billing account setup (requires payment method)
- App Store/Play Store integration
- Apple Sign-In certificates

## Usage Examples

### Basic Setup
```javascript
const FirebaseAutomator = require('./firebase-console-automation');

const automator = new FirebaseAutomator('your-project-id');
await automator.init();
await automator.createWebApp('My App');
await automator.enableAuthentication([
  { name: 'Email/Password', type: 'email' },
  { name: 'Google', type: 'google' }
]);
```

### Batch Web App Creation
```bash
npm run firebase-example
```

### Custom Configuration
```javascript
// Create web app with hosting
await automator.createWebApp('Marketing Site', {
  setupHosting: true,
  hostingSite: 'marketing-site'
});

// Enable GitHub OAuth
await automator.enableAuthentication([{
  name: 'GitHub',
  type: 'github',
  clientId: 'your-github-client-id',
  clientSecret: 'your-github-client-secret'
}]);
```

## Authentication State

The script can save your Google login state to avoid re-authentication:

```javascript
const automator = new FirebaseAutomator('project-id', {
  authStatePath: './firebase-auth-state.json'
});
```

First run will require login, subsequent runs will use saved state.

## Configuration Files

The automation will automatically:
- Extract Firebase config for each web app
- Save configs as `firebase-config-{app-name}.js`
- Create basic security rules
- Set up project structure

## OAuth Provider Setup

For OAuth providers, you'll need to create apps externally:

### GitHub OAuth App
1. Go to GitHub Settings > Developer settings > OAuth Apps
2. Create new OAuth app
3. Use callback URL provided by the script
4. Get Client ID and Secret

### Google OAuth
1. Go to Google Cloud Console
2. Enable Google+ API
3. Create OAuth 2.0 credentials
4. Configure consent screen

### Facebook OAuth
1. Go to Facebook Developers
2. Create new app
3. Set up Facebook Login
4. Get App ID and Secret

## Running the Automation

```bash
# Install and run
npm install
npm run install-browser
npm run firebase-example

# Or run directly
node firebase-console-automation.js
```

## Troubleshooting

- **Login Issues**: Make sure 2FA is configured properly
- **Rate Limiting**: Add delays between operations
- **Selector Changes**: Firebase Console UI may change, update selectors
- **Authentication Errors**: Clear auth state file and re-login

## Security Notes

- Never commit auth credentials to version control
- Use environment variables for sensitive data
- Auth state files contain session tokens - keep secure
- Consider using service accounts for production automation