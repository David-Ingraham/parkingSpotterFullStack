import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export const api = {
  /**
   * Fetch all cameras with current parking status
   */
  async getCameras() {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/cameras`);
      return response.data;
    } catch (error) {
      console.error('Error fetching cameras:', error);
      throw error;
    }
  },

  /**
   * Fetch specific camera by address
   */
  async getCamera(address) {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/camera/${address}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching camera ${address}:`, error);
      throw error;
    }
  },

  /**
   * Health check
   */
  async healthCheck() {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/health`);
      return response.data;
    } catch (error) {
      console.error('Error checking health:', error);
      throw error;
    }
  }
};

export default api;

