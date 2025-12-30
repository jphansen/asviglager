import api from './api';
import type { Photo, PhotoUpload } from '../types';

export const photoService = {
  async uploadPhoto(photo: PhotoUpload): Promise<Photo> {
    const response = await api.post<Photo>('/photos/', photo);
    return response.data;
  },

  async getPhotos(): Promise<Photo[]> {
    const response = await api.get<Photo[]>('/photos/');
    return response.data;
  },

  async getPhoto(id: string): Promise<Photo> {
    const response = await api.get<Photo>(`/photos/${id}`);
    return response.data;
  },

  async deletePhoto(id: string): Promise<void> {
    await api.delete(`/photos/${id}`);
  },

  // Helper to convert File to base64
  fileToBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        const result = reader.result as string;
        // Remove data URL prefix (e.g., "data:image/png;base64,")
        const base64 = result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = (error) => reject(error);
    });
  },
};
