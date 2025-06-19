const { chromium } = require('playwright');
const fs = require('fs').promises;
const path = require('path');

/**
 * Firebase Console Automation Script
 * Automates manual Firebase Console tasks using Playwright
 */

class FirebaseAutomator {
  constructor(projectId, config = {}) {
    this.projectId = projectId;
    this.config = {
      headless: false, // Show browser for debugging
      slowMo: 500, // Slow down actions for visibility
      ...config
    };
    this.browser = null;
    this.page = null;
  }

  async init() {
    this.browser = await chromium.launch({
      headless: this.config.headless,
      slowMo: this.config.slowMo
    });
    
    const context = await this.browser.newContext({
      viewport: { width: 1280, height: 720 }
    });
    
    this.page = await context.newPage();
    
    // Handle Google login persistence
    if (this.config.authStatePath) {
      await context.storageState({ path: this.config.authStatePath });
    }
  }

  async login(email, password) {
    console.log('🔐 Logging into Google...');
    await this.page.goto('https://console.firebase.google.com');
    
    // Check if already logged in
    try {
      await this.page.waitForSelector(`[data-projectid="${this.projectId}"]`, { timeout: 5000 });
      console.log('✅ Already logged in');
      return;
    } catch (e) {
      // Not logged in, proceed with login
    }

    // Google login flow
    await this.page.fill('input[type="email"]', email);
    await this.page.click('#identifierNext');
    
    await this.page.waitForSelector('input[type="password"]', { visible: true });
    await this.page.fill('input[type="password"]', password);
    await this.page.click('#passwordNext');
    
    // Wait for Firebase console to load
    await this.page.waitForSelector('.c5e-project-card', { timeout: 30000 });
    
    // Save auth state for future runs
    if (this.config.authStatePath) {
      await this.page.context().storageState({ path: this.config.authStatePath });
    }
  }

  async navigateToProject() {
    console.log(`📂 Navigating to project: ${this.projectId}`);
    await this.page.goto(`https://console.firebase.google.com/project/${this.projectId}/overview`);
    await this.page.waitForLoadState('networkidle');
  }

  async createWebApp(appName, appConfig = {}) {
    console.log(`🌐 Creating web app: ${appName}`);
    
    await this.navigateToProject();
    
    // Go to project settings
    await this.page.click('[aria-label="Project settings"]');
    await this.page.waitForSelector('text="Your apps"');
    
    // Click add app button
    await this.page.click('button:has-text("Add app")');
    
    // Select Web platform
    await this.page.click('[aria-label="Web"]');
    
    // Fill app nickname
    await this.page.fill('input[placeholder="App nickname"]', appName);
    
    // Configure hosting if requested
    if (appConfig.setupHosting) {
      await this.page.check('text="Also set up Firebase Hosting"');
      if (appConfig.hostingSite) {
        await this.page.fill('input[placeholder="hosting-site-name"]', appConfig.hostingSite);
      }
    }
    
    // Register app
    await this.page.click('button:has-text("Register app")');
    
    // Wait for config to be generated
    await this.page.waitForSelector('text="Firebase SDK snippet"', { timeout: 30000 });
    
    // Extract the config
    const configElement = await this.page.waitForSelector('pre:has-text("const firebaseConfig")');
    const configText = await configElement.textContent();
    
    // Save config to file
    const configPath = path.join(process.cwd(), `firebase-config-${appName}.js`);
    await fs.writeFile(configPath, configText);
    console.log(`✅ Config saved to: ${configPath}`);
    
    // Continue to next step
    await this.page.click('button:has-text("Continue to console")');
    
    return configText;
  }

  async enableAuthentication(providers = []) {
    console.log('🔑 Configuring Authentication...');
    
    await this.navigateToProject();
    
    // Go to Authentication
    await this.page.click('text="Authentication"');
    await this.page.waitForSelector('text="Sign-in method"');
    await this.page.click('text="Sign-in method"');
    
    for (const provider of providers) {
      await this.enableAuthProvider(provider);
    }
  }

  async enableAuthProvider(provider) {
    console.log(`  Enabling ${provider.name}...`);
    
    // Click on the provider
    await this.page.click(`text="${provider.name}"`);
    
    switch (provider.type) {
      case 'email':
        await this.page.check('text="Enable"');
        if (provider.passwordless) {
          await this.page.check('text="Email link (passwordless sign-in)"');
        }
        break;
        
      case 'google':
        await this.page.check('text="Enable"');
        if (provider.clientId && provider.clientSecret) {
          await this.page.click('text="Web SDK configuration"');
          await this.page.fill('input[placeholder="Web client ID"]', provider.clientId);
          await this.page.fill('input[placeholder="Web client secret"]', provider.clientSecret);
        }
        break;
        
      case 'github':
        await this.page.check('text="Enable"');
        await this.page.fill('input[placeholder="Client ID"]', provider.clientId);
        await this.page.fill('input[placeholder="Client secret"]', provider.clientSecret);
        
        // Copy callback URL for GitHub OAuth app
        const callbackUrl = await this.page.inputValue('input[readonly][value*="firebaseapp.com"]');
        console.log(`    ⚠️  Add this callback URL to GitHub OAuth app: ${callbackUrl}`);
        break;
        
      case 'custom':
        // Handle custom OAuth providers
        await this.page.check('text="Enable"');
        if (provider.configFields) {
          for (const [field, value] of Object.entries(provider.configFields)) {
            await this.page.fill(`input[placeholder*="${field}"]`, value);
          }
        }
        break;
    }
    
    // Save the provider settings
    await this.page.click('button:has-text("Save")');
    await this.page.waitForSelector(`text="${provider.name}"`, { state: 'visible' });
  }

  async configureFirestore() {
    console.log('🗄️ Configuring Firestore...');
    
    await this.navigateToProject();
    
    // Go to Firestore
    await this.page.click('text="Firestore Database"');
    
    // Check if Firestore needs to be created
    try {
      await this.page.waitForSelector('text="Create database"', { timeout: 5000 });
      await this.page.click('button:has-text("Create database")');
      
      // Select mode
      await this.page.click('text="Start in production mode"');
      await this.page.click('button:has-text("Next")');
      
      // Select location
      await this.page.click('button:has-text("nam5 (us-central)")'); // or your preferred location
      await this.page.click('button:has-text("Enable")');
      
      console.log('✅ Firestore database created');
    } catch (e) {
      console.log('ℹ️ Firestore already exists');
    }
  }

  async configureStorage() {
    console.log('📦 Configuring Storage...');
    
    await this.navigateToProject();
    
    // Go to Storage
    await this.page.click('text="Storage"');
    
    // Check if Storage needs to be set up
    try {
      await this.page.waitForSelector('text="Get started"', { timeout: 5000 });
      await this.page.click('button:has-text("Get started")');
      
      // Start in production mode
      await this.page.click('text="Start in production mode"');
      await this.page.click('button:has-text("Next")');
      
      // Select location
      await this.page.click('button:has-text("nam5 (us-central)")'); // or your preferred location
      await this.page.click('button:has-text("Done")');
      
      console.log('✅ Storage configured');
    } catch (e) {
      console.log('ℹ️ Storage already configured');
    }
  }

  async configureFunctions() {
    console.log('⚡ Configuring Functions...');
    
    await this.navigateToProject();
    
    // Go to Functions
    await this.page.click('text="Functions"');
    
    // Check if Functions needs to be set up
    try {
      await this.page.waitForSelector('text="Get started"', { timeout: 5000 });
      await this.page.click('button:has-text("Get started")');
      
      // This usually redirects to upgrade billing
      console.log('⚠️  Functions requires billing to be enabled');
    } catch (e) {
      console.log('ℹ️ Functions already configured');
    }
  }

  async configureHosting(customDomain = null) {
    console.log('🌍 Configuring Hosting...');
    
    await this.navigateToProject();
    
    // Go to Hosting
    await this.page.click('text="Hosting"');
    
    if (customDomain) {
      await this.page.click('text="Add custom domain"');
      await this.page.fill('input[placeholder="example.com"]', customDomain);
      await this.page.click('button:has-text("Continue")');
      
      // Get DNS records
      const dnsRecords = await this.page.$$eval('.dns-record', records => 
        records.map(r => r.textContent)
      );
      
      console.log('📝 Add these DNS records to your domain:');
      dnsRecords.forEach(record => console.log(`   ${record}`));
    }
  }

  async close() {
    if (this.browser) {
      await this.browser.close();
    }
  }
}

// Example usage
async function main() {
  const automator = new FirebaseAutomator('your-project-id', {
    headless: false,
    authStatePath: './firebase-auth-state.json' // Save login state
  });

  try {
    await automator.init();
    
    // Login (only needed first time if saving auth state)
    // await automator.login('your-email@gmail.com', 'your-password');
    
    // Create a new web app
    await automator.createWebApp('My Web App', {
      setupHosting: true,
      hostingSite: 'my-web-app'
    });
    
    // Enable authentication providers
    await automator.enableAuthentication([
      { name: 'Email/Password', type: 'email' },
      { name: 'Google', type: 'google' },
      { 
        name: 'GitHub', 
        type: 'github',
        clientId: 'your-github-client-id',
        clientSecret: 'your-github-client-secret'
      }
    ]);
    
    // Configure services
    await automator.configureFirestore();
    await automator.configureStorage();
    await automator.configureFunctions();
    await automator.configureHosting('mydomain.com');
    
  } catch (error) {
    console.error('❌ Error:', error);
  } finally {
    await automator.close();
  }
}

// Export for use as module
module.exports = FirebaseAutomator;

// Run if called directly
if (require.main === module) {
  main();
}