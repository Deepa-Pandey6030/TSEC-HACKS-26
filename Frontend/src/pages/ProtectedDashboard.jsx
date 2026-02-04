import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { motion } from 'framer-motion';
import { LogOut, User, Mail } from 'lucide-react';

const ProtectedDashboard = () => {
  const { user, isAuthenticated, logout, loading } = useAuth();
  const navigate = useNavigate();

  // Redirect to login if not authenticated
  React.useEffect(() => {
    if (!loading && !isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, loading, navigate]);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      {/* Header */}
      <motion.nav
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white shadow-md"
      >
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Dashboard
          </h1>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleLogout}
            className="flex items-center gap-2 px-6 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition"
          >
            <LogOut size={20} />
            Logout
          </motion.button>
        </div>
      </motion.nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-xl shadow-lg p-8 mb-8"
        >
          <h2 className="text-3xl font-bold mb-8 text-gray-800">
            Welcome, {user?.name || 'User'}! 👋
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* User Info Card */}
            <motion.div
              whileHover={{ translateY: -5 }}
              className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg p-6 text-white"
            >
              <div className="flex items-center gap-4 mb-4">
                <User size={32} />
                <h3 className="text-xl font-semibold">Name</h3>
              </div>
              <p className="text-blue-100 text-lg">{user?.name || 'N/A'}</p>
            </motion.div>

            {/* Email Card */}
            <motion.div
              whileHover={{ translateY: -5 }}
              className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg p-6 text-white"
            >
              <div className="flex items-center gap-4 mb-4">
                <Mail size={32} />
                <h3 className="text-xl font-semibold">Email</h3>
              </div>
              <p className="text-purple-100 text-lg">{user?.email || 'N/A'}</p>
            </motion.div>
          </div>

          {/* Status Card */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.4 }}
            className="mt-8 bg-green-50 border-l-4 border-green-500 p-6 rounded-lg"
          >
            <h3 className="text-lg font-semibold text-green-800 mb-2">✅ Session Active</h3>
            <p className="text-green-700">
              Your session is stored and persisted. You can navigate freely and your login status will be maintained even if you refresh the page.
            </p>
          </motion.div>
        </motion.div>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6"
        >
          {[
            { title: 'Profile Settings', desc: 'Manage your profile' },
            { title: 'Data Privacy', desc: 'Control your data' },
            { title: 'Help & Support', desc: 'Get assistance' },
          ].map((item, idx) => (
            <motion.div
              key={idx}
              whileHover={{ translateY: -8 }}
              className="bg-white rounded-lg shadow-md p-6 cursor-pointer hover:shadow-lg transition"
            >
              <h3 className="text-lg font-semibold text-gray-800 mb-2">{item.title}</h3>
              <p className="text-gray-600">{item.desc}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </div>
  );
};

export default ProtectedDashboard;
