import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  TrendingUp,
  Shield,
  AlertTriangle,
  CheckCircle,
  Activity,
  Globe,
  Users,
  Clock
} from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';

// Utility function for conditional classes
const cn = (...classes) => {
  return classes.filter(Boolean).join(' ');
};

// Card Component
const Card = ({ children, className = '' }) => {
  return (
    <div className={cn(
      'bg-white/80 backdrop-blur-xl rounded-2xl border border-gray-200/50 shadow-sm hover:shadow-lg transition-all duration-300',
      className
    )}>
      {children}
    </div>
  );
};

// Button Component
const Button = ({
  children,
  variant = 'primary',
  size = 'md',
  className = '',
  onClick,
  ...props
}) => {
  const baseStyles = 'font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2';

  const variants = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500',
    outline: 'border border-gray-300 text-gray-700 hover:bg-gray-50 focus:ring-gray-500'
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base'
  };

  return (
    <button
      className={cn(baseStyles, variants[variant], sizes[size], className)}
      onClick={onClick}
      {...props}
    >
      {children}
    </button>
  );
};

// Modal Component
const Modal = ({ isOpen, onClose, title, children }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="bg-white rounded-2xl shadow-2xl max-w-lg w-full max-h-[90vh] overflow-auto"
      >
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        <div className="p-6">
          {children}
        </div>
      </motion.div>
    </div>
  );
};

// Stats data - would be replaced with real backend data
const stats = [
  {
    title: 'Total Users',
    value: '1,234',
    change: '+12%',
    trend: 'up',
    icon: Activity,
    color: 'primary'
  },
  {
    title: 'Revenue',
    value: '$12,450',
    change: '+15%',
    trend: 'up',
    icon: Shield,
    color: 'success'
  },
  {
    title: 'Active Now',
    value: '45',
    change: '+2%',
    trend: 'up',
    icon: AlertTriangle,
    color: 'warning'
  },
  {
    title: 'Project Data',
    value: '127',
    change: '+8%',
    trend: 'up',
    icon: CheckCircle,
    color: 'secondary'
  }
];

const recentActivity = [
  {
    id: 1,
    type: 'detection',
    title: 'New user registration spike detected',
    time: '2 minutes ago',
    severity: 'high',
    status: 'verified'
  },
  {
    id: 2,
    type: 'verification',
    title: 'Revenue milestone reached: $10k',
    time: '5 minutes ago',
    severity: 'low',
    status: 'completed'
  },
  {
    id: 3,
    type: 'alert',
    title: 'Unusual traffic pattern detected',
    time: '12 minutes ago',
    severity: 'medium',
    status: 'investigating'
  }
];

const Dashboard = () => {
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedActivity, setSelectedActivity] = useState(null);
  const isReducedMotion = false; // Can be tied to user preferences

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: isReducedMotion ? 0 : 0.1,
        delayChildren: 0.2
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: "spring",
        stiffness: 140,
        damping: 20
      }
    }
  };

  const StatCard = ({ stat, index }) => {
    const Icon = stat.icon;
    const isPositive = stat.trend === 'up';

    return (
      <motion.div
        variants={itemVariants}
        whileHover={isReducedMotion ? {} : { y: -4 }}
        className="group"
      >
        <div className="bg-white/80 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 hover:border-blue-500/30 transition-all duration-300 hover:shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <div className={cn(
              'p-3 rounded-xl',
              stat.color === 'primary' && 'bg-blue-100 text-blue-600',
              stat.color === 'success' && 'bg-green-100 text-green-600',
              stat.color === 'warning' && 'bg-yellow-100 text-yellow-600',
              stat.color === 'secondary' && 'bg-purple-100 text-purple-600'
            )}>
              <Icon size={24} />
            </div>
            <div className={cn(
              'flex items-center text-sm font-medium',
              isPositive ? 'text-green-600' : 'text-red-600'
            )}>
              <TrendingUp
                size={16}
                className={cn(
                  'mr-1',
                  !isPositive && 'transform rotate-180'
                )}
              />
              {stat.change}
            </div>
          </div>

          <div>
            <div className="text-3xl font-bold text-gray-900 mb-2">
              {stat.value}
            </div>
            <div className="text-sm text-gray-600">
              {stat.title}
            </div>
          </div>
        </div>
      </motion.div>
    );
  };

  return (
    <DashboardLayout>
      <div className="bg-gradient-to-br from-gray-50 via-blue-50/20 to-purple-50/20 p-6">
        <div className="container mx-auto">
          {/* Header */}
          <motion.div
            className="mb-8"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{
              type: "spring",
              stiffness: 140,
              damping: 20
            }}
          >
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              Dashboard Overview
            </h1>
            <p className="text-gray-600">
              Real-time monitoring and analytics
            </p>
          </motion.div>

          {/* Stats Grid */}
          <motion.div
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12"
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            {stats.map((stat, index) => (
              <StatCard key={stat.title} stat={stat} index={index} />
            ))}
          </motion.div>

          {/* Main Content Grid */}
          <motion.div
            className="grid grid-cols-1 lg:grid-cols-3 gap-8"
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            {/* Activity Feed */}
            <motion.div variants={itemVariants} className="lg:col-span-2">
              <Card>
                <div className="p-6">
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-2xl font-bold text-gray-900">
                      Recent Activity
                    </h2>
                    <Button variant="outline" size="sm">
                      View All
                    </Button>
                  </div>

                  <div className="space-y-4">
                    {recentActivity.map((activity, index) => (
                      <motion.div
                        key={activity.id}
                        className="flex items-start space-x-4 p-4 rounded-xl bg-gray-50 hover:bg-gray-100 transition-colors cursor-pointer"
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                        onClick={() => {
                          setSelectedActivity(activity);
                          setModalOpen(true);
                        }}
                        whileHover={isReducedMotion ? {} : { x: 4 }}
                      >
                        <div className={cn(
                          'w-3 h-3 rounded-full mt-2',
                          activity.severity === 'high' && 'bg-red-500',
                          activity.severity === 'medium' && 'bg-yellow-500',
                          activity.severity === 'low' && 'bg-green-500'
                        )} />

                        <div className="flex-1">
                          <h3 className="font-medium text-gray-900 mb-1">
                            {activity.title}
                          </h3>
                          <div className="flex items-center space-x-4 text-sm text-gray-500">
                            <span className="flex items-center">
                              <Clock size={14} className="mr-1" />
                              {activity.time}
                            </span>
                            <span className={cn(
                              'px-2 py-1 rounded-full text-xs font-medium',
                              activity.status === 'completed' && 'bg-green-100 text-green-700',
                              activity.status === 'investigating' && 'bg-yellow-100 text-yellow-700',
                              activity.status === 'verified' && 'bg-blue-100 text-blue-700'
                            )}>
                              {activity.status}
                            </span>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>
              </Card>
            </motion.div>

            {/* Sidebar */}
            <motion.div variants={itemVariants} className="space-y-6">
              {/* Global Status */}
              <Card>
                <div className="p-6">
                  <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                    <Globe className="mr-2" size={20} />
                    Global Status
                  </h3>

                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">Sources Monitored</span>
                      <span className="font-bold text-gray-900">2,847</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">Active Regions</span>
                      <span className="font-bold text-gray-900">147</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">System Health</span>
                      <span className="font-bold text-green-600">99.8%</span>
                    </div>
                  </div>
                </div>
              </Card>

              {/* Quick Actions */}
              <Card>
                <div className="p-6">
                  <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                    <Users className="mr-2" size={20} />
                    Quick Actions
                  </h3>

                  <div className="space-y-3">
                    <Button variant="outline" className="w-full justify-start">
                      Submit Report
                    </Button>
                    <Button variant="outline" className="w-full justify-start">
                      Expert Verification
                    </Button>
                    <Button variant="outline" className="w-full justify-start">
                      Crisis Protocol
                    </Button>
                  </div>
                </div>
              </Card>
            </motion.div>
          </motion.div>
        </div>
      </div>

      {/* Activity Detail Modal */}
      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title="Activity Details"
      >
        {selectedActivity && (
          <div className="space-y-4">
            <div>
              <h3 className="font-bold text-gray-900 mb-2">
                {selectedActivity.title}
              </h3>
              <p className="text-gray-600">
                Detected at {selectedActivity.time} with {selectedActivity.severity} severity level.
                Current status: {selectedActivity.status}.
              </p>
            </div>

            <div className="flex space-x-3 pt-4">
              <Button size="sm">Take Action</Button>
              <Button variant="outline" size="sm">Mark Reviewed</Button>
            </div>
          </div>
        )}
      </Modal>
    </DashboardLayout>
  );
};

export default Dashboard;