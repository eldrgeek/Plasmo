const FirebaseAutomator = require('./firebase-console-automation');

/**
 * Example usage of Firebase Console Automation
 * 
 * This example shows how to automate various Firebase Console tasks
 * for an existing Firebase project with multiple web apps.
 */

async function automateFirebaseSetup() {
  // Configuration for your Firebase project
  const config = {
    projectId: 'your-existing-project-id', // Replace with your project ID
    email: 'your-email@gmail.com',        // Replace with your Google account
    password: 'your-password',            // Replace with your password (or use auth state)
    
    // Browser settings
    headless: false,                      // Set to true for headless mode
    slowMo: 1000,                        // Slow down actions (ms)
    authStatePath: './firebase-auth-state.json' // Save login state
  };

  const automator = new FirebaseAutomator(config.projectId, {
    headless: config.headless,
    slowMo: config.slowMo,
    authStatePath: config.authStatePath
  });

  try {
    console.log('🚀 Starting Firebase Console automation...');
    await automator.init();
    
    // Login (only needed first time if saving auth state)
    if (!config.authStatePath || !require('fs').existsSync(config.authStatePath)) {
      await automator.login(config.email, config.password);
    }
    
    // Example 1: Create a new web app
    console.log('\n📱 Creating new web app...');
    await automator.createWebApp('Admin Dashboard', {
      setupHosting: true,
      hostingSite: 'admin-dashboard-site'
    });
    
    // Example 2: Create another web app
    console.log('\n📱 Creating another web app...');
    await automator.createWebApp('Customer Portal', {
      setupHosting: true,
      hostingSite: 'customer-portal-site'
    });
    
    // Example 3: Configure Authentication providers
    console.log('\n🔑 Configuring Authentication...');
    await automator.enableAuthentication([
      { 
        name: 'Email/Password', 
        type: 'email',
        passwordless: false // Set to true for email link sign-in
      },
      { 
        name: 'Google', 
        type: 'google'
        // For Google, you might need to configure OAuth in Google Cloud Console
      },
      { 
        name: 'GitHub', 
        type: 'github',
        clientId: 'your-github-oauth-client-id',
        clientSecret: 'your-github-oauth-client-secret'
        // You'll need to create a GitHub OAuth app first
      }
    ]);
    
    // Example 4: Configure Firebase services
    console.log('\n🗄️ Configuring Firestore...');
    await automator.configureFirestore();
    
    console.log('\n📦 Configuring Storage...');
    await automator.configureStorage();
    
    console.log('\n⚡ Configuring Functions...');
    await automator.configureFunctions();
    
    console.log('\n🌍 Configuring Hosting...');
    await automator.configureHosting('your-custom-domain.com');
    
    console.log('\n✅ Firebase automation completed successfully!');
    
  } catch (error) {
    console.error('❌ Automation failed:', error);
    console.error('Stack trace:', error.stack);
  } finally {
    await automator.close();
  }
}

// Configuration for batch operations
async function batchCreateWebApps() {
  const webApps = [
    { name: 'Marketing Site', hosting: 'marketing-site' },
    { name: 'API Dashboard', hosting: 'api-dashboard' },
    { name: 'Mobile App Admin', hosting: 'mobile-admin' },
    { name: 'Analytics Portal', hosting: 'analytics' }
  ];

  const automator = new FirebaseAutomator('your-project-id');
  
  try {
    await automator.init();
    
    for (const app of webApps) {
      console.log(`\n📱 Creating: ${app.name}`);
      await automator.createWebApp(app.name, {
        setupHosting: true,
        hostingSite: app.hosting
      });
      
      // Wait between requests to avoid rate limiting
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
    
  } catch (error) {
    console.error('❌ Batch creation failed:', error);
  } finally {
    await automator.close();
  }
}

// Configuration for OAuth providers setup
async function setupOAuthProviders() {
  const providers = [
    {
      name: 'Google',
      type: 'google'
    },
    {
      name: 'GitHub',
      type: 'github',
      clientId: process.env.GITHUB_CLIENT_ID,
      clientSecret: process.env.GITHUB_CLIENT_SECRET
    },
    {
      name: 'Facebook',
      type: 'custom',
      configFields: {
        'App ID': process.env.FACEBOOK_APP_ID,
        'App Secret': process.env.FACEBOOK_APP_SECRET
      }
    }
  ];

  const automator = new FirebaseAutomator('your-project-id');
  
  try {
    await automator.init();
    await automator.enableAuthentication(providers);
    
  } catch (error) {
    console.error('❌ OAuth setup failed:', error);
  } finally {
    await automator.close();
  }
}

// Choose which function to run
if (require.main === module) {
  // Run the main automation
  automateFirebaseSetup();
  
  // Or run batch operations
  // batchCreateWebApps();
  
  // Or setup OAuth providers
  // setupOAuthProviders();
}

module.exports = {
  automateFirebaseSetup,
  batchCreateWebApps,
  setupOAuthProviders
};