import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';
import { getStorage } from 'firebase/storage';

// Firebase configuration - You'll get this from Firebase Console
const firebaseConfig = {
  // Replace with your papa-chat project config
  apiKey: "your-api-key",
  authDomain: "papa-chat.firebaseapp.com",
  projectId: "papa-chat",
  storageBucket: "papa-chat.appspot.com",
  messagingSenderId: "627759580484",
  appId: "your-app-id"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase services
export const auth = getAuth(app);
export const db = getFirestore(app);
export const storage = getStorage(app);

export default app; 