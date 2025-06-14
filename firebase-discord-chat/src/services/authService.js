import { 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  updateProfile
} from 'firebase/auth';
import { doc, setDoc, updateDoc, getDoc } from 'firebase/firestore';
import { auth, db } from '../firebase/config';

export const authService = {
  // Register new user
  async register(email, password, username) {
    try {
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      const user = userCredential.user;
      
      // Update the user's display name
      await updateProfile(user, { displayName: username });
      
      // Create user document in Firestore
      await setDoc(doc(db, 'users', user.uid), {
        uid: user.uid,
        username,
        email,
        avatar: '',
        status: 'online',
        createdAt: new Date(),
        lastSeen: new Date(),
        preferences: {
          theme: 'dark',
          notifications: true
        }
      });
      
      return user;
    } catch (error) {
      console.error('Error registering user:', error);
      throw error;
    }
  },

  // Login user
  async login(email, password) {
    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      
      // Update online status
      await updateDoc(doc(db, 'users', userCredential.user.uid), {
        status: 'online',
        lastSeen: new Date()
      });
      
      return userCredential.user;
    } catch (error) {
      console.error('Error logging in:', error);
      throw error;
    }
  },

  // Logout user
  async logout() {
    try {
      if (auth.currentUser) {
        await updateDoc(doc(db, 'users', auth.currentUser.uid), {
          status: 'offline',
          lastSeen: new Date()
        });
      }
      await signOut(auth);
    } catch (error) {
      console.error('Error logging out:', error);
      throw error;
    }
  },

  // Get current user data from Firestore
  async getCurrentUserData() {
    if (!auth.currentUser) return null;
    
    try {
      const userDoc = await getDoc(doc(db, 'users', auth.currentUser.uid));
      return userDoc.exists() ? userDoc.data() : null;
    } catch (error) {
      console.error('Error getting user data:', error);
      return null;
    }
  },

  // Listen to auth state changes
  onAuthStateChanged(callback) {
    return onAuthStateChanged(auth, callback);
  },

  // Update user status
  async updateUserStatus(status) {
    if (!auth.currentUser) return;
    
    try {
      await updateDoc(doc(db, 'users', auth.currentUser.uid), {
        status,
        lastSeen: new Date()
      });
    } catch (error) {
      console.error('Error updating user status:', error);
    }
  }
}; 