import React, { createContext, useContext, useState, useEffect } from 'react';
import { getCurrentUser } from '../services/auth';

const AuthContext = createContext(null);

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

// Export useTheme for backward compatibility with AIChat
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
            const token = localStorage.getItem('token');
            const storedUsername = localStorage.getItem('username');

            if (token) {
                try {
                    const result = await getCurrentUser();
                    if (result.success) {
                        setUser(result.user);
                        setIsAuthenticated(true);
                    } else {
                        localStorage.removeItem('token');
                        localStorage.removeItem('username');
                        setUser(null);
                        setIsAuthenticated(false);
                    }
                } catch (error) {
                    if (storedUsername) {
                        setUser({ username: storedUsername });
                        setIsAuthenticated(true);
                    } else {
                        localStorage.removeItem('token');
                        setUser(null);
                        setIsAuthenticated(false);
                    }
                }
            }
            setLoading(false);
        };

        checkAuth();
    }, []);

    const login = (userData, token) => {
        setUser(userData);
        setIsAuthenticated(true);
        localStorage.setItem('token', token);
        localStorage.setItem('username', userData.username);
    };

    const logout = () => {
        setUser(null);
        setIsAuthenticated(false);
        localStorage.removeItem('token');
        localStorage.removeItem('username');
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