import { 
  ref, 
  uploadBytes, 
  uploadBytesResumable,
  getDownloadURL, 
  deleteObject,
  listAll,
  getMetadata
} from 'firebase/storage';
import { storage, auth } from '../firebase/config';

export const storageService = {
  // Upload file with progress tracking
  async uploadFile(file, path, onProgress = null) {
    if (!auth.currentUser) throw new Error('User not authenticated');
    
    try {
      const fileRef = ref(storage, `${path}/${file.name}`);
      
      if (onProgress) {
        // Use resumable upload for progress tracking
        const uploadTask = uploadBytesResumable(fileRef, file);
        
        return new Promise((resolve, reject) => {
          uploadTask.on('state_changed',
            (snapshot) => {
              const progress = (snapshot.bytesTransferred / snapshot.totalBytes) * 100;
              onProgress(progress);
            },
            (error) => {
              console.error('Upload error:', error);
              reject(error);
            },
            async () => {
              try {
                const downloadURL = await getDownloadURL(uploadTask.snapshot.ref);
                const metadata = await getMetadata(uploadTask.snapshot.ref);
                resolve({
                  url: downloadURL,
                  name: file.name,
                  size: metadata.size,
                  type: metadata.contentType,
                  path: uploadTask.snapshot.ref.fullPath
                });
              } catch (error) {
                reject(error);
              }
            }
          );
        });
      } else {
        // Simple upload without progress
        const snapshot = await uploadBytes(fileRef, file);
        const downloadURL = await getDownloadURL(snapshot.ref);
        const metadata = await getMetadata(snapshot.ref);
        
        return {
          url: downloadURL,
          name: file.name,
          size: metadata.size,
          type: metadata.contentType,
          path: snapshot.ref.fullPath
        };
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      throw error;
    }
  },
  
  // Upload image for chat
  async uploadChatImage(file, channelId, onProgress = null) {
    const path = `uploads/${auth.currentUser.uid}/chat/${channelId}`;
    return await this.uploadFile(file, path, onProgress);
  },
  
  // Upload file for chat
  async uploadChatFile(file, channelId, onProgress = null) {
    const path = `uploads/${auth.currentUser.uid}/files/${channelId}`;
    return await this.uploadFile(file, path, onProgress);
  },
  
  // Upload avatar image
  async uploadAvatar(file, onProgress = null) {
    if (!auth.currentUser) throw new Error('User not authenticated');
    
    try {
      // Delete old avatar if exists
      await this.deleteAvatar();
      
      const path = `avatars/${auth.currentUser.uid}`;
      const fileRef = ref(storage, path);
      
      if (onProgress) {
        const uploadTask = uploadBytesResumable(fileRef, file);
        
        return new Promise((resolve, reject) => {
          uploadTask.on('state_changed',
            (snapshot) => {
              const progress = (snapshot.bytesTransferred / snapshot.totalBytes) * 100;
              onProgress(progress);
            },
            (error) => {
              console.error('Avatar upload error:', error);
              reject(error);
            },
            async () => {
              try {
                const downloadURL = await getDownloadURL(uploadTask.snapshot.ref);
                resolve(downloadURL);
              } catch (error) {
                reject(error);
              }
            }
          );
        });
      } else {
        const snapshot = await uploadBytes(fileRef, file);
        return await getDownloadURL(snapshot.ref);
      }
    } catch (error) {
      console.error('Error uploading avatar:', error);
      throw error;
    }
  },
  
  // Delete avatar
  async deleteAvatar() {
    if (!auth.currentUser) return;
    
    try {
      const avatarRef = ref(storage, `avatars/${auth.currentUser.uid}`);
      await deleteObject(avatarRef);
    } catch (error) {
      // Ignore error if avatar doesn't exist
      if (error.code !== 'storage/object-not-found') {
        console.error('Error deleting avatar:', error);
      }
    }
  },
  
  // Delete file
  async deleteFile(filePath) {
    if (!auth.currentUser) throw new Error('User not authenticated');
    
    try {
      const fileRef = ref(storage, filePath);
      await deleteObject(fileRef);
    } catch (error) {
      console.error('Error deleting file:', error);
      throw error;
    }
  },
  
  // Get user's uploaded files
  async getUserFiles(userId = null) {
    const targetUserId = userId || auth.currentUser?.uid;
    if (!targetUserId) throw new Error('User not authenticated');
    
    try {
      const userUploadsRef = ref(storage, `uploads/${targetUserId}`);
      const result = await listAll(userUploadsRef);
      
      const files = await Promise.all(
        result.items.map(async (itemRef) => {
          try {
            const [url, metadata] = await Promise.all([
              getDownloadURL(itemRef),
              getMetadata(itemRef)
            ]);
            
            return {
              name: itemRef.name,
              url,
              size: metadata.size,
              type: metadata.contentType,
              path: itemRef.fullPath,
              uploadTime: metadata.timeCreated,
              updatedTime: metadata.updated
            };
          } catch (error) {
            console.error(`Error getting file info for ${itemRef.name}:`, error);
            return null;
          }
        })
      );
      
      return files.filter(file => file !== null);
    } catch (error) {
      console.error('Error getting user files:', error);
      throw error;
    }
  },
  
  // Validate file type and size
  validateFile(file, options = {}) {
    const {
      maxSize = 10 * 1024 * 1024, // 10MB default
      allowedTypes = ['image/*', 'text/*', 'application/pdf'],
      allowedExtensions = []
    } = options;
    
    const errors = [];
    
    // Check file size
    if (file.size > maxSize) {
      errors.push(`File size must be less than ${Math.round(maxSize / 1024 / 1024)}MB`);
    }
    
    // Check file type
    const isTypeAllowed = allowedTypes.some(type => {
      if (type.endsWith('/*')) {
        return file.type.startsWith(type.slice(0, -1));
      }
      return file.type === type;
    });
    
    // Check file extension
    const fileExtension = file.name.split('.').pop()?.toLowerCase();
    const isExtensionAllowed = allowedExtensions.length === 0 || 
      allowedExtensions.includes(fileExtension);
    
    if (!isTypeAllowed && !isExtensionAllowed) {
      errors.push(`File type not allowed. Allowed types: ${allowedTypes.join(', ')}`);
    }
    
    return {
      isValid: errors.length === 0,
      errors
    };
  },
  
  // Validate image file
  validateImage(file, options = {}) {
    const {
      maxSize = 5 * 1024 * 1024, // 5MB for images
      allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    } = options;
    
    return this.validateFile(file, { maxSize, allowedTypes });
  },
  
  // Get file info without downloading
  async getFileInfo(filePath) {
    try {
      const fileRef = ref(storage, filePath);
      const [url, metadata] = await Promise.all([
        getDownloadURL(fileRef),
        getMetadata(fileRef)
      ]);
      
      return {
        name: fileRef.name,
        url,
        size: metadata.size,
        type: metadata.contentType,
        path: filePath,
        uploadTime: metadata.timeCreated,
        updatedTime: metadata.updated
      };
    } catch (error) {
      console.error('Error getting file info:', error);
      throw error;
    }
  },
  
  // Generate thumbnail for images (would require Cloud Functions in production)
  async generateThumbnail(imageFile) {
    // This is a client-side implementation
    // In production, you'd use Cloud Functions to generate thumbnails
    return new Promise((resolve, reject) => {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      const img = new Image();
      
      img.onload = () => {
        const maxSize = 200;
        let { width, height } = img;
        
        if (width > height) {
          if (width > maxSize) {
            height = (height * maxSize) / width;
            width = maxSize;
          }
        } else {
          if (height > maxSize) {
            width = (width * maxSize) / height;
            height = maxSize;
          }
        }
        
        canvas.width = width;
        canvas.height = height;
        
        ctx.drawImage(img, 0, 0, width, height);
        
        canvas.toBlob((blob) => {
          resolve(blob);
        }, 'image/jpeg', 0.8);
      };
      
      img.onerror = reject;
      img.src = URL.createObjectURL(imageFile);
    });
  },
  
  // Format file size for display
  formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
}; 