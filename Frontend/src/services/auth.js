import axios from 'axios';

const API_URL = 'http://localhost:3001'; // Adjust to match your backend URL

export const signup = async (name, email, password) => {
  try {
    const response = await axios.post(`${API_URL}/register`, {
      username: name,
      email,
      password
    });

    if (response.data.status === 'ok') {
      return { success: true };
    } else {
      return { success: false, error: response.data.error || 'Signup failed' };
    }
  } catch (error) {
    throw error;
  }
};

export const login = async (email, password) => {
  try {
    const response = await axios.post(`${API_URL}/login`, {
      email,
      password
    });

    if (response.data.status === 'ok') {
      // Store the token and username in localStorage
      if (response.data.token) {
        localStorage.setItem('token', response.data.token);
      }
      if (response.data.username) {
        localStorage.setItem('username', response.data.username);
      }
      return {
        success: true,
        token: response.data.token,
        username: response.data.username
      };
    } else {
      return { success: false, error: response.data.error || 'Login failed' };
    }
  } catch (error) {
    throw error;
  }
};

// Get current authenticated user
export const getCurrentUser = async () => {
  try {
    const token = localStorage.getItem('token');
    if (!token) {
      return { success: false, error: 'No token found' };
    }

    const response = await axios.get(`${API_URL}/me`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (response.data.status === 'ok') {
      return { success: true, user: response.data.user };
    } else {
      return { success: false, error: response.data.error || 'Failed to get user' };
    }
  } catch (error) {
    return { success: false, error: error.message };
  }
};

// Logout user
export const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('username');
};
