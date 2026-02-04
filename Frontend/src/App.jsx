import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
// Added FileCheck for the validator icon
import { Home, LayoutDashboard, Package, LogIn, UserPlus, LogOut, User, FileCheck } from 'lucide-react';
import { ThemeProvider, useTheme } from './lib/theme-provider';
import { AuthProvider, useAuth } from './context/AuthContext';
import { HomePage } from './pages/home';
import { ProductListPage } from './pages/product-list';
import { CreativeAssistantPage } from './pages/creative-assistant';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Signup from './pages/Signup';
import AIChat from './components/AIChat';
import { Button } from './components/ui/button';
import { ThemeToggle } from './components/ui/theme-toggle';
import ContinuityValidator from './pages/ContinuityValidator';

function Navigation() {
  const navigate = useNavigate();
  const location = useLocation();
  const { isReducedMotion } = useTheme();
  const { isAuthenticated, user, logout: authLogout, loading } = useAuth();

  // Don't show navigation on login/signup pages
  if (['/login', '/signup'].includes(location.pathname)) {
    return null;
  }

  const navigation = [
    { path: '/', label: 'Home', icon: Home },
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/products', label: 'Products', icon: Package },
    // FIXED: Added icon and completed the object
    { path: '/validator', label: 'Validate', icon: FileCheck } 
  ];

  const handleLogout = () => {
    authLogout();
    navigate('/');
  };

  return (
    <>
      {/* Desktop Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-40 bg-white/80 dark:bg-neutral-900/80 backdrop-blur-xl border-b border-neutral-200/50 dark:border-neutral-700/50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <motion.div
              className="flex items-center space-x-2 cursor-pointer"
              onClick={() => navigate('/')}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{
                type: "spring",
                stiffness: 140,
                damping: 20
              }}
            >
              <div className="w-10 h-10 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-xl flex items-center justify-center">
                <span className="text-white font-bold text-lg">T</span>
              </div>
              <span className="text-xl font-bold text-neutral-900 dark:text-neutral-100">
                TruthShield
              </span>
            </motion.div>

            {/* Navigation Links */}
            <div className="hidden md:flex items-center space-x-1">
              {navigation.map((item, index) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;

                return (
                  <motion.div
                    key={item.path}
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <Button
                      variant={isActive ? 'primary' : 'ghost'}
                      size="sm"
                      onClick={() => navigate(item.path)}
                      className="flex items-center space-x-2"
                    >
                      <Icon size={16} />
                      <span>{item.label}</span>
                    </Button>
                  </motion.div>
                );
              })}
            </div>

            {/* Theme Toggle and Auth Buttons */}
            <div className="flex items-center space-x-2">
              {!loading && (
                <>
                  {isAuthenticated ? (
                    <>
                      {/* User Display */}
                      <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{
                          type: "spring",
                          stiffness: 140,
                          damping: 20,
                          delay: 0.1
                        }}
                        className="flex items-center space-x-2 px-3 py-2 bg-neutral-100 dark:bg-neutral-800 rounded-lg"
                      >
                        <User size={16} className="text-neutral-700 dark:text-neutral-300" />
                        <span className="hidden sm:inline text-sm font-medium text-neutral-900 dark:text-neutral-100">
                          {user?.username || 'User'}
                        </span>
                      </motion.div>

                      {/* Logout Button */}
                      <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{
                          type: "spring",
                          stiffness: 140,
                          damping: 20,
                          delay: 0.2
                        }}
                      >
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={handleLogout}
                          className="flex items-center space-x-2 text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-500"
                        >
                          <LogOut className='' size={16} />
                          <span className="hidden sm:inline">Logout</span>
                        </Button>
                      </motion.div>
                    </>
                  ) : (
                    <>
                      {/* Login Button */}
                      <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{
                          type: "spring",
                          stiffness: 140,
                          damping: 20,
                          delay: 0.1
                        }}
                      >
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => navigate('/login')}
                          className="flex items-center space-x-2"
                        >
                          <LogIn size={16} />
                          <span className="hidden sm:inline">Login</span>
                        </Button>
                      </motion.div>

                      {/* Signup Button */}
                      <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{
                          type: "spring",
                          stiffness: 140,
                          damping: 20,
                          delay: 0.2
                        }}
                      >
                        <Button
                          variant="primary"
                          size="sm"
                          onClick={() => navigate('/signup')}
                          className="flex items-center space-x-2"
                        >
                          <UserPlus size={16} />
                          <span className="hidden sm:inline">Sign Up</span>
                        </Button>
                      </motion.div>
                    </>
                  )}
                </>
              )}

              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{
                  type: "spring",
                  stiffness: 140,
                  damping: 20,
                  delay: 0.3
                }}
              >
                <ThemeToggle />
              </motion.div>
            </div>
          </div>
        </div>
      </nav>

      {/* Mobile Navigation */}
      <nav className="fixed bottom-0 left-0 right-0 z-40 md:hidden bg-white/80 dark:bg-neutral-900/80 backdrop-blur-xl border-t border-neutral-200/50 dark:border-neutral-700/50">
        <div className="flex items-center justify-around py-3">
          {navigation.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;

            return (
              <Button
                key={item.path}
                variant={isActive ? 'primary' : 'ghost'}
                size="sm"
                onClick={() => navigate(item.path)}
                className="flex flex-col items-center space-y-1 min-w-[60px]"
              >
                <Icon size={16} />
                <span className="text-xs">{item.label}</span>
              </Button>
            );
          })}
        </div>
      </nav>
    </>
  );
}

function AppContent() {
  const location = useLocation();
  const { isReducedMotion } = useTheme();
  const [showChat, setShowChat] = useState(false);
  const [notifications, setNotifications] = useState([]);

  const addNotification = (message, type = 'info') => {
    const id = Math.random().toString(36).substr(2, 9);
    setNotifications(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id));
    }, 4000);
  };

  const pageVariants = {
    initial: { opacity: 0, x: isReducedMotion ? 0 : 20 },
    animate: {
      opacity: 1,
      x: 0,
      transition: {
        type: "spring",
        stiffness: 140,
        damping: 20
      }
    },
    exit: { opacity: 0, x: isReducedMotion ? 0 : -20 }
  };

  // Add padding for pages with navigation
  const hasNavigation = !['/login', '/signup'].includes(location.pathname);

  return (
    <div className="relative min-h-screen">
      <Navigation />

      <motion.main
        className={hasNavigation ? "pt-20 pb-20 md:pb-0" : ""}
        variants={pageVariants}
        initial="initial"
        animate="animate"
        exit="exit"
        key={location.pathname}
      >
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/" element={<HomePage />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/products" element={<ProductListPage />} />
          <Route path="/validator" element={<ContinuityValidator />} />

        </Routes>
      </motion.main>

      {/* AI Chat Integration - Always Available */}
      <AnimatePresence>
        {showChat && (
          <AIChat
            showChat={showChat}
            setShowChat={setShowChat}
            addNotification={addNotification}
          />
        )}
      </AnimatePresence>

      {/* Floating Chat Toggle */}
      <motion.button
        onClick={() => setShowChat(!showChat)}
        className="fixed bottom-6 right-6 w-16 h-16 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full shadow-2xl z-50 flex items-center justify-center group"
        whileHover={{
          scale: 1.1,
          boxShadow: "0 0 30px rgba(6, 182, 212, 0.8)"
        }}
        whileTap={{ scale: 0.95 }}
        animate={{
          boxShadow: showChat
            ? "0 0 20px rgba(6, 182, 212, 0.6)"
            : ["0 0 10px rgba(6, 182, 212, 0.4)", "0 0 20px rgba(6, 182, 212, 0.8)", "0 0 10px rgba(6, 182, 212, 0.4)"]
        }}
        transition={{
          boxShadow: {
            duration: 2,
            repeat: showChat ? 0 : Infinity,
            ease: "easeInOut"
          }
        }}
      >
        <motion.div
          animate={{ rotate: showChat ? 45 : 0 }}
          className="text-2xl"
        >
          {showChat ? '✕' : '💬'}
        </motion.div>
      </motion.button>

      {/* Notification System */}
      <div className="fixed top-20 right-4 z-50 space-y-2">
        <AnimatePresence>
          {notifications.map(notification => (
            <motion.div
              key={notification.id}
              initial={{ opacity: 0, x: 300 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 300 }}
              className={`px-4 py-3 rounded-lg shadow-lg ${notification.type === 'success' ? 'bg-green-500' :
                notification.type === 'error' ? 'bg-red-500' :
                  'bg-blue-500'
                } text-white`}
            >
              {notification.message}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <AppContent />
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;