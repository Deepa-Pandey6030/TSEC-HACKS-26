import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

export const useTheme = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useTheme must be used within an AuthProvider');
    }
    return { theme: context.theme, toggleTheme: context.toggleTheme };
};

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [loading, setLoading] = useState(true);
    
    // Theme state management
    const [theme, setTheme] = useState(() => {
        const storedTheme = localStorage.getItem('theme');
        return (storedTheme === 'light' || storedTheme === 'dark') ? storedTheme : 'dark';
    });

    // Theme effect
    useEffect(() => {
        document.documentElement.classList.remove('light', 'dark');
        document.documentElement.classList.add(theme);
        localStorage.setItem('theme', theme);
    }, [theme]);

    const toggleTheme = () => {
        setTheme((prevTheme) => (prevTheme === 'light' ? 'dark' : 'light'));
    };

    // Check if user is authenticated on mount
    useEffect(() => {
        const checkAuth = async () => {
            const sessionToken = localStorage.getItem('sessionToken');
            
            if (sessionToken) {
                try {
                    const response = await fetch('http://localhost:8000/api/v1/auth/check-session', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ session_token: sessionToken })
                    });
                    
                    const data = await response.json();
                    
                    if (data.valid && data.user) {
                        setUser(data.user);
                        setIsAuthenticated(true);
                    } else {
                        // Session invalid, clear storage
                        localStorage.removeItem('sessionToken');
                        setUser(null);
                        setIsAuthenticated(false);
                    }
                } catch (error) {
                    console.error('Auth check failed:', error);
                    setUser(null);
                    setIsAuthenticated(false);
                }
            }
            setLoading(false);
        };

        checkAuth();
    }, []);


    const login = (userData, sessionToken) => {
        setUser(userData);
        setIsAuthenticated(true);
        localStorage.setItem('sessionToken', sessionToken);
    };

    const logout = async () => {
        const sessionToken = localStorage.getItem('sessionToken');
        
        if (sessionToken) {
            try {
                await fetch('http://localhost:8000/api/v1/auth/logout', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ session_token: sessionToken })
                });
            } catch (error) {
                console.error('Logout failed:', error);
            }
        }
        
        setUser(null);
        setIsAuthenticated(false);
        localStorage.removeItem('sessionToken');
    };

    const refreshUser = async () => {
        try {
            const result = await getCurrentUser();
            if (result.success) {
                setUser(result.user);
                setIsAuthenticated(true);
            }
        } catch (error) {
            console.error('Failed to refresh user:', error);
        }
    };

    return (
        <AuthContext.Provider value={{ 
            user, 
            isAuthenticated, 
            loading, 
            login, 
            logout, 
            refreshUser,
            theme,
            toggleTheme
        }}>
            {children}
        </AuthContext.Provider>
    );
};