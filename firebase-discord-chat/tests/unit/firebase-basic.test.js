const { initializeApp } = require('firebase/app');
const { getFirestore, doc, setDoc, getDoc, collection, addDoc } = require('firebase/firestore');

// Firebase config for testing
const firebaseConfig = {
  apiKey: "test-api-key",
  authDomain: "roundtable-test.firebaseapp.com",
  projectId: "roundtable-test",
  storageBucket: "roundtable-test.appspot.com",
  messagingSenderId: "123456789",
  appId: "test-app-id"
};

describe('Firebase Database Basic Tests', () => {
  let app;
  let db;

  beforeAll(() => {
    // Initialize Firebase
    app = initializeApp(firebaseConfig);
    db = getFirestore(app);
  });

  test('should connect to Firestore emulator', async () => {
    // Simple test to verify connection
    const testDoc = doc(db, 'test', 'connection');
    await setDoc(testDoc, { message: 'Hello Firebase!' });
    
    const docSnap = await getDoc(testDoc);
    expect(docSnap.exists()).toBe(true);
    expect(docSnap.data().message).toBe('Hello Firebase!');
  });

  test('should create and read document', async () => {
    const testData = {
      name: 'Test User',
      email: 'test@example.com',
      createdAt: new Date()
    };

    // Create document
    const docRef = await addDoc(collection(db, 'users'), testData);
    expect(docRef.id).toBeDefined();

    // Read document
    const docSnap = await getDoc(docRef);
    expect(docSnap.exists()).toBe(true);
    expect(docSnap.data().name).toBe(testData.name);
    expect(docSnap.data().email).toBe(testData.email);
  });

  test('should handle non-existent document', async () => {
    const nonExistentDoc = doc(db, 'users', 'non-existent-id');
    const docSnap = await getDoc(nonExistentDoc);
    expect(docSnap.exists()).toBe(false);
  });
}); 