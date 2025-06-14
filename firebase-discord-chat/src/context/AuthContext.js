import React, { createContext, useContext, useEffect, useState } from 'react';
import { authService } from '../services/authService';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(true);

  const login = async (email, password) => {
    try {
      const user = await authService.login(email, password);
      const userDataDoc = await authService.getCurrentUserData();
      setCurrentUser(user);
      setUserData(userDataDoc);
      return user;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const register = async (email, password, username) => {
    try {
      const user = await authService.register(email, password, username);
      const userDataDoc = await authService.getCurrentUserData();
      setCurrentUser(user);
      setUserData(userDataDoc);
      return user;
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  };

  const logout = async () => {
    try {
      await authService.logout();
      setCurrentUser(null);
      setUserData(null);
    } catch (error) {
      console.error('Logout error:', error);
      throw error;
    }
  };

  const updateUserStatus = async (status) => {
    try {
      await authService.updateUserStatus(status);
      setUserData(prev => ({ ...prev, status }));
    } catch (error) {
      console.error('Update status error:', error);
    }
  };

  useEffect(() => {
    const unsubscribe = authService.onAuthStateChanged(async (user) => {
      setCurrentUser(user);
      if (user) {
        const userDataDoc = await authService.getCurrentUserData();
        setUserData(userDataDoc);
      } else {
        setUserData(null);
      }
      setLoading(false);
    });

    return unsubscribe;
  }, []);

  // Update user status on app focus/blur
  useEffect(() => {
    const handleFocus = () => {
      if (currentUser) {
        updateUserStatus('online');
      }
    };

    const handleBlur = () => {
      if (currentUser) {
        updateUserStatus('away');
      }
    };

    window.addEventListener('focus', handleFocus);
    window.addEventListener('blur', handleBlur);

    return () => {
      window.removeEventListener('focus', handleFocus);
      window.removeEventListener('blur', handleBlur);
    };
  }, [currentUser]);

  const value = {
    currentUser,
    userData,
    login,
    register,
    logout,
    updateUserStatus,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
}; 