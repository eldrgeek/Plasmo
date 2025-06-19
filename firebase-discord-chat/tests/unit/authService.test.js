const { initializeApp } = require('firebase/app');
const { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword, signOut, updateProfile } = require('firebase/auth');
const { getFirestore, doc, setDoc, getDoc, updateDoc } = require('firebase/firestore');
const { authService } = require('../../src/services/authService');
const { 
  TEST_USERS, 
  getAuthenticatedContext, 
  getUnauthenticatedContext,
  assertFirebaseSuccess,
  assertFirebaseError
} = require('../utils/testHelpers');

// Firebase config for testing
const firebaseConfig = {
  apiKey: "test-api-key",
  authDomain: "roundtable-test.firebaseapp.com",
  projectId: "roundtable-test",
  storageBucket: "roundtable-test.appspot.com",
  messagingSenderId: "123456789",
  appId: "test-app-id"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

describe('Authentication Service', () => {
  beforeEach(async () => {
    // Clear any existing auth state
    if (auth.currentUser) {
      await signOut(auth);
    }
  });

  afterEach(async () => {
    // Clean up auth state
    if (auth.currentUser) {
      await signOut(auth);
    }
  });

  describe('User Registration', () => {
    test('should register new user successfully', async () => {
      const userData = TEST_USERS.alice;
      
      const userCredential = await createUserWithEmailAndPassword(
        auth, 
        userData.email, 
        userData.password
      );
      
      expect(userCredential.user).toBeDefined();
      expect(userCredential.user.email).toBe(userData.email);
      
      // Update profile
      await updateProfile(userCredential.user, {
        displayName: userData.displayName
      });
      
      // Create user document in Firestore
      await setDoc(doc(db, 'users', userCredential.user.uid), {
        email: userData.email,
        displayName: userData.displayName,
        createdAt: new Date(),
        status: 'online'
      });
      
      // Verify user document was created
      const userDoc = await getDoc(doc(db, 'users', userCredential.user.uid));
      expect(userDoc.exists()).toBe(true);
      expect(userDoc.data().email).toBe(userData.email);
    });

    test('should reject duplicate email registration', async () => {
      const userData = TEST_USERS.alice;
      
      // Register user first time
      await createUserWithEmailAndPassword(auth, userData.email, userData.password);
      
      // Sign out
      await signOut(auth);
      
      // Try to register same email again
      await expect(
        createUserWithEmailAndPassword(auth, userData.email, userData.password)
      ).rejects.toThrow();
    });

    test('should reject invalid email format', async () => {
      await expect(
        createUserWithEmailAndPassword(auth, 'invalid-email', 'password123')
      ).rejects.toThrow();
    });

    test('should reject weak password', async () => {
      await expect(
        createUserWithEmailAndPassword(auth, 'test@example.com', '123')
      ).rejects.toThrow();
    });
  });

  describe('User Login', () => {
    beforeEach(async () => {
      // Create test user for login tests
      const userData = TEST_USERS.bob;
      await createUserWithEmailAndPassword(auth, userData.email, userData.password);
      await signOut(auth);
    });

    test('should login existing user successfully', async () => {
      const userData = TEST_USERS.bob;
      
      const userCredential = await signInWithEmailAndPassword(
        auth, 
        userData.email, 
        userData.password
      );
      
      expect(userCredential.user).toBeDefined();
      expect(userCredential.user.email).toBe(userData.email);
    });

    test('should reject invalid credentials', async () => {
      await expect(
        signInWithEmailAndPassword(auth, 'nonexistent@test.com', 'wrongpassword')
      ).rejects.toThrow();
    });

    test('should reject wrong password', async () => {
      const userData = TEST_USERS.bob;
      
      await expect(
        signInWithEmailAndPassword(auth, userData.email, 'wrongpassword')
      ).rejects.toThrow();
    });
  });

  describe('User Logout', () => {
    test('should logout user successfully', async () => {
      const userData = TEST_USERS.alice;
      
      // Login first
      await createUserWithEmailAndPassword(auth, userData.email, userData.password);
      expect(auth.currentUser).toBeDefined();
      
      // Logout
      await signOut(auth);
      expect(auth.currentUser).toBeNull();
    });
  });

  describe('Profile Management', () => {
    test('should update user profile', async () => {
      const userData = TEST_USERS.alice;
      
      // Register user
      const userCredential = await createUserWithEmailAndPassword(
        auth, 
        userData.email, 
        userData.password
      );
      
      // Update profile
      await updateProfile(userCredential.user, {
        displayName: 'Updated Name'
      });
      
      // Update Firestore document
      await setDoc(doc(db, 'users', userCredential.user.uid), {
        email: userData.email,
        displayName: 'Updated Name',
        updatedAt: new Date()
      });
      
      // Verify update
      const userDoc = await getDoc(doc(db, 'users', userCredential.user.uid));
      expect(userDoc.data().displayName).toBe('Updated Name');
    });

    test('should update user status', async () => {
      const userData = TEST_USERS.alice;
      
      // Register user
      const userCredential = await createUserWithEmailAndPassword(
        auth, 
        userData.email, 
        userData.password
      );
      
      // Create user document
      await setDoc(doc(db, 'users', userCredential.user.uid), {
        email: userData.email,
        displayName: userData.displayName,
        status: 'online'
      });
      
      // Update status
      await updateDoc(doc(db, 'users', userCredential.user.uid), {
        status: 'away',
        lastSeen: new Date()
      });
      
      // Verify status update
      const userDoc = await getDoc(doc(db, 'users', userCredential.user.uid));
      expect(userDoc.data().status).toBe('away');
      expect(userDoc.data().lastSeen).toBeDefined();
    });
  });
}); 