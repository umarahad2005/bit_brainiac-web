const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001/api';

class SessionService {
  async makeRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    // Add auth token
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      // Handle unauthorized responses
      if (response.status === 401) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return { success: false, message: 'Session expired' };
      }

      return data;
    } catch (error) {
      console.error('API request failed:', error);
      return { success: false, message: 'Network error. Please try again.' };
    }
  }

  async getUserSessions(limit = 50) {
    return await this.makeRequest(`/sessions?limit=${limit}`);
  }

  async createSession(title = 'New Chat') {
    return await this.makeRequest('/sessions', {
      method: 'POST',
      body: JSON.stringify({ title }),
    });
  }

  async getSession(sessionId) {
    return await this.makeRequest(`/sessions/${sessionId}`);
  }

  async deleteSession(sessionId) {
    return await this.makeRequest(`/sessions/${sessionId}`, {
      method: 'DELETE',
    });
  }

  async clearAllSessions() {
    return await this.makeRequest('/sessions/clear', {
      method: 'POST',
    });
  }
}

export const sessionService = new SessionService();

