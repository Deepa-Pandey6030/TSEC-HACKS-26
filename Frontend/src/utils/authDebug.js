/**
 * Frontend Auth Connection Test
 * Run this in browser console to test backend connection
 */

const API_URL = 'http://localhost:8000/api/v1/auth';

async function testBackendConnection() {
  console.log('🔍 Testing Backend Connection...');
  
  try {
    const response = await fetch(`${API_URL}/check-session`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_token: 'test' })
    });
    
    const data = await response.json();
    console.log('✅ Backend is responding');
    console.log('Response:', data);
    return true;
  } catch (error) {
    console.error('❌ Backend connection failed:', error);
    return false;
  }
}

async function testSignup(name, email, password) {
  console.log(`📝 Testing Signup with email: ${email}`);
  
  try {
    const response = await fetch(`${API_URL}/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password })
    });
    
    const data = await response.json();
    console.log('Response:', data);
    
    if (data.success) {
      console.log('✅ Signup successful');
      console.log('User:', data.user);
      console.log('Token:', data.token);
      localStorage.setItem('sessionToken', data.token);
      return data;
    } else {
      console.error('❌ Signup failed:', data.message);
      return null;
    }
  } catch (error) {
    console.error('❌ Signup error:', error);
    return null;
  }
}

async function testLogin(email, password) {
  console.log(`🔑 Testing Login with email: ${email}`);
  
  try {
    const response = await fetch(`${API_URL}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    
    const data = await response.json();
    console.log('Response:', data);
    
    if (data.success) {
      console.log('✅ Login successful');
      console.log('User:', data.user);
      console.log('Token:', data.token);
      localStorage.setItem('sessionToken', data.token);
      return data;
    } else {
      console.error('❌ Login failed:', data.message);
      return null;
    }
  } catch (error) {
    console.error('❌ Login error:', error);
    return null;
  }
}

async function testCheckSession() {
  const token = localStorage.getItem('sessionToken');
  console.log(`🔐 Checking Session with token: ${token}`);
  
  if (!token) {
    console.warn('⚠️ No session token in localStorage');
    return null;
  }
  
  try {
    const response = await fetch(`${API_URL}/check-session`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_token: token })
    });
    
    const data = await response.json();
    console.log('Response:', data);
    
    if (data.valid) {
      console.log('✅ Session is valid');
      console.log('User:', data.user);
      return data;
    } else {
      console.error('❌ Session invalid:', data.message);
      return null;
    }
  } catch (error) {
    console.error('❌ Session check error:', error);
    return null;
  }
}

async function testLogout() {
  const token = localStorage.getItem('sessionToken');
  console.log(`🚪 Testing Logout`);
  
  if (!token) {
    console.warn('⚠️ No session token to logout');
    return null;
  }
  
  try {
    const response = await fetch(`${API_URL}/logout`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_token: token })
    });
    
    const data = await response.json();
    console.log('Response:', data);
    
    if (data.success) {
      console.log('✅ Logout successful');
      localStorage.removeItem('sessionToken');
      return true;
    } else {
      console.error('❌ Logout failed:', data.message);
      return false;
    }
  } catch (error) {
    console.error('❌ Logout error:', error);
    return false;
  }
}

// Quick test flow
async function runQuickTest() {
  console.log('\n========== QUICK AUTH TEST ==========\n');
  
  // Test 1: Backend connection
  await testBackendConnection();
  
  // Test 2: Signup with unique email
  const testEmail = `test${Date.now()}@example.com`;
  const result = await testSignup('Test User', testEmail, 'password123');
  
  if (result) {
    // Test 3: Check session
    await testCheckSession();
    
    // Test 4: Logout
    await testLogout();
    
    // Test 5: Check session after logout
    await testCheckSession();
  }
  
  console.log('\n========== TEST COMPLETE ==========\n');
}

// Export for use
window.authTest = {
  testBackendConnection,
  testSignup,
  testLogin,
  testCheckSession,
  testLogout,
  runQuickTest
};

console.log('✅ Auth Test functions loaded');
console.log('Run: authTest.runQuickTest() to test full flow');
console.log('Or use individual functions:');
console.log('  authTest.testBackendConnection()');
console.log('  authTest.testSignup(name, email, password)');
console.log('  authTest.testLogin(email, password)');
console.log('  authTest.testCheckSession()');
console.log('  authTest.testLogout()');
