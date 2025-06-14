import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';
import { getStorage } from 'firebase/storage';

// Firebase configuration using environment variables
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || process.env.REACT_APP_FIREBASE_API_KEY || "YOUR_API_KEY_HERE",
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || process.env.REACT_APP_FIREBASE_AUTH_DOMAIN || "monad-roundtable.firebaseapp.com",
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || process.env.REACT_APP_FIREBASE_PROJECT_ID || "monad-roundtable",
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || process.env.REACT_APP_FIREBASE_STORAGE_BUCKET || "monad-roundtable.appspot.com",
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID || "YOUR_MESSAGING_SENDER_ID_HERE",
  appId: import.meta.env.VITE_FIREBASE_APP_ID || process.env.REACT_APP_FIREBASE_APP_ID || "YOUR_APP_ID_HERE"
};

// Validate configuration
const requiredFields = ['apiKey', 'authDomain', 'projectId', 'storageBucket', 'messagingSenderId', 'appId'];
const missingFields = requiredFields.filter(field => 
  !firebaseConfig[field] || firebaseConfig[field].startsWith('YOUR_')
);

if (missingFields.length > 0) {
  console.error('❌ Firebase configuration incomplete!');
  console.error('Missing or placeholder values for:', missingFields.join(', '));
  console.error('\n🔧 To fix this:');
  console.error('1. Create a .env file in your project root');
  console.error('2. Add your Firebase config values (see .env.example)');
  console.error('3. Get values from Firebase Console > Project Settings > Your apps');
  console.error('4. Restart your development server');
  
  // Don't throw error in development to allow for gradual setup
  if (process.env.NODE_ENV === 'production') {
    throw new Error('Firebase configuration is incomplete');
  }
}

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase services
export const auth = getAuth(app);
export const db = getFirestore(app);
export const storage = getStorage(app);

// Export the app instance
export default app;

// Helper function to check if Firebase is properly configured
export const isFirebaseConfigured = () => {
  return missingFields.length === 0;
};

// Log configuration status (only in development)
if (process.env.NODE_ENV === 'development') {
  if (isFirebaseConfigured()) {
    console.log('✅ Firebase configured successfully');
  } else {
    console.warn('⚠️ Firebase configuration incomplete - some features may not work');
  }
} 