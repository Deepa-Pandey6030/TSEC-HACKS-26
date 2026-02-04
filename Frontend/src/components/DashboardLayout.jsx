import React, { useEffect } from 'react';
import { LayoutDashboard, Users, LogOut } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const DashboardLayout = ({ children }) => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/');
  };

  // Lock body scroll when dashboard is mounted
  useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = '';
    };
  }, []);

  return (
    <div className="flex h-screen bg-gray-100 overflow-hidden">
      <aside className="w-64 bg-white shadow-md hidden md:block fixed left-0 top-20 h-[calc(100vh-5rem)]">
        <div className="p-6 text-xl font-bold text-blue-600">HackathonApp</div>
        <nav className="mt-6">
          <a href="/dashboard" className="flex items-center px-6 py-3 bg-blue-50 text-blue-600 border-r-4 border-blue-600">
            <LayoutDashboard className="w-5 h-5 mr-3" />
            Dashboard
          </a>
          <a href="#" className="flex items-center px-6 py-3 text-gray-600 hover:bg-gray-50 hover:text-blue-600 transition">
            <Users className="w-5 h-5 mr-3" />
            Profile
          </a>
        </nav>
      </aside>
      <div className="flex-1 flex flex-col md:ml-64 h-[calc(100vh-5rem)]">
        <main className="flex-1 overflow-y-auto min-h-0 p-6">
          {children}
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;