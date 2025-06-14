// Simple test script to verify database setup
// Run with: node test-database.js

import { databaseService } from './src/services/databaseService.js';

async function testDatabase() {
  console.log('🔥 Testing Roundtable Database Setup...\n');

  try {
    // Test 1: Health Check
    console.log('1. Testing database connection...');
    const health = await databaseService.healthCheck();
    console.log(`   Status: ${health.status}`);
    console.log(`   Message: ${health.message}\n`);

    if (health.status !== 'healthy') {
      console.error('❌ Database connection failed!');
      console.error('Make sure you have:');
      console.error('1. Updated src/firebase/config.js with your Firebase config');
      console.error('2. Enabled Firestore in your Firebase project');
      console.error('3. Set up authentication in Firebase Console');
      return;
    }

    // Test 2: Initialize Database
    console.log('2. Initializing database with default data...');
    await databaseService.initializeDatabase();
    console.log('   ✅ Database initialized successfully\n');

    // Test 3: Get Database Stats
    console.log('3. Getting database statistics...');
    const stats = await databaseService.getDatabaseStats();
    console.log(`   Total Channels: ${stats.totalChannels}`);
    console.log(`   Public Channels: ${stats.publicChannels}`);
    console.log(`   Private Channels: ${stats.privateChannels}`);
    console.log(`   Total Users: ${stats.totalUsers}`);
    console.log(`   Online Users: ${stats.onlineUsers}\n`);

    console.log('🎉 Database setup completed successfully!');
    console.log('\nNext steps:');
    console.log('1. Update src/firebase/config.js with your actual Firebase config');
    console.log('2. Deploy Firestore security rules: firebase deploy --only firestore:rules');
    console.log('3. Deploy storage rules: firebase deploy --only storage');
    console.log('4. Start building your UI with Bolt.new or other tools');
    console.log('\nDatabase API documentation: DATABASE_API.md');

  } catch (error) {
    console.error('❌ Database test failed:', error.message);
    
    if (error.message.includes('Firebase config')) {
      console.error('\n🔧 Fix: Update src/firebase/config.js with your Firebase project config');
    } else if (error.message.includes('permission-denied')) {
      console.error('\n🔧 Fix: Check your Firestore security rules');
    } else if (error.message.includes('not-found')) {
      console.error('\n🔧 Fix: Make sure Firestore is enabled in your Firebase project');
    }
  }
}

// Run the test
testDatabase().catch(console.error); 