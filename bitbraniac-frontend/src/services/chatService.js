const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001/api';

class ChatService {
  async makeRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    // Add auth token if available
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      // Handle unauthorized responses
      if (response.status === 401 && token) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        // Don't redirect here, let the auth context handle it
        return { success: false, message: 'Session expired' };
      }

      return data;
    } catch (error) {
      console.error('API request failed:', error);
      return { success: false, message: 'Network error. Please try again.' };
    }
  }

  async sendMessage(message, sessionId = null) {
    const endpoint = localStorage.getItem('access_token') 
      ? '/chat/message' 
      : '/chat/message/anonymous';
    
    const body = { message };
    if (sessionId) {
      body.session_id = sessionId;
    }

    return await this.makeRequest(endpoint, {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  async getWelcomeMessage() {
    return await this.makeRequest('/chat/welcome');
  }

  async getChatHistory() {
    return await this.makeRequest('/chat/history');
  }

  async clearChat() {
    return await this.makeRequest('/chat/clear', {
      method: 'POST',
    });
  }

  async checkHealth() {
    return await this.makeRequest('/chat/health');
  }
}

export const chatService = new ChatService();

