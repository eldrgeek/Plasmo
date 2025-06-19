// Test setup for Firebase services
import { initializeTestEnvironment, assertFails, assertSucceeds } from '@firebase/rules-unit-testing';
import fs from 'fs';
import path from 'path';

// Global test environment
let testEnv;

// Setup before all tests
beforeAll(async () => {
  console.log('🔥 Setting up Firebase emulators for testing...');
});

// Cleanup after all tests
afterAll(async () => {
  console.log('🧹 Cleaning up test environment...');
});

// Clear data before each test
beforeEach(async () => {
  if (testEnv) {
    await testEnv.clearFirestore();
    await testEnv.clearStorage();
  }
});

// Mock console methods to reduce noise in tests
global.console = {
  ...console,
  log: jest.fn(),
  debug: jest.fn(),
  info: jest.fn(),
  warn: jest.fn(),
  error: jest.fn()
};

// Mock environment variables
process.env.REACT_APP_FIREBASE_API_KEY = 'test-api-key';
process.env.REACT_APP_FIREBASE_AUTH_DOMAIN = 'roundtable-test.firebaseapp.com';
process.env.REACT_APP_FIREBASE_PROJECT_ID = 'roundtable-test';
process.env.REACT_APP_FIREBASE_STORAGE_BUCKET = 'roundtable-test.appspot.com';
process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID = '123456789';
process.env.REACT_APP_FIREBASE_APP_ID = 'test-app-id';

// Firebase emulator setup for testing
process.env.FIRESTORE_EMULATOR_HOST = 'localhost:8081';
process.env.FIREBASE_AUTH_EMULATOR_HOST = 'localhost:9099';
process.env.FIREBASE_STORAGE_EMULATOR_HOST = 'localhost:9199';

// Set test environment
process.env.NODE_ENV = 'test';

// Increase timeout for Firebase operations
jest.setTimeout(30000); 