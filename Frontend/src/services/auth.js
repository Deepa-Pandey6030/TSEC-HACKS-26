const API_URL = 'http://localhost:8000/api/v1/auth';

export const signup = async (name, email, password) => {
  try {
    const response = await fetch(`${API_URL}/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password })
    });

    const data = await response.json();

    if (response.ok && data.success) {
      return {
        success: true,
        user: data.user,
        token: data.token
      };
    } else {
      return { success: false, error: data.message || 'Signup failed' };
    }
  } catch (error) {
    return { success: false, error: error.message };
  }
};

export const login = async (email, password) => {
  try {
    const response = await fetch(`${API_URL}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    const data = await response.json();

    if (response.ok && data.success) {
      return {
        success: true,
        user: data.user,
        token: data.token
      };
    } else {
      return { success: false, error: data.message || 'Login failed' };
    }
  } catch (error) {
    return { success: false, error: error.message };
  }
};

export const logout = async () => {
  try {
    const sessionToken = localStorage.getItem('sessionToken');
    
    if (sessionToken) {
      await fetch(`${API_URL}/logout`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_token: sessionToken })
      });
    }
    
    localStorage.removeItem('sessionToken');
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
};

export const checkSession = async (sessionToken) => {
  try {
    const response = await fetch(`${API_URL}/check-session`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_token: sessionToken })
    });

    const data = await response.json();
    return data;
  } catch (error) {
    return { valid: false, error: error.message };
  }
};

