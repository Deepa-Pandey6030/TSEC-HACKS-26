import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { LogIn, Mail, Lock, Loader, Shield, Sparkles, Zap, ArrowRight, CheckCircle } from 'lucide-react';
import { login } from '../services/auth';
import { useAuth } from '../context/AuthContext';

const AnimatedBackground = () => (
  <div className="fixed inset-0 -z-10 overflow-hidden">
    <div className="absolute inset-0 bg-black" />

    <motion.div
      className="absolute top-1/4 -left-20 w-96 h-96 bg-purple-600 rounded-full blur-3xl opacity-20"
      animate={{ x: [0, 120, 0], y: [0, 60, 0] }}
      transition={{ duration: 20, repeat: Infinity }}
    />
    <motion.div
      className="absolute top-1/3 -right-20 w-96 h-96 bg-blue-600 rounded-full blur-3xl opacity-20"
      animate={{ x: [0, -120, 0], y: [0, 100, 0] }}
      transition={{ duration: 25, repeat: Infinity }}
    />
    <motion.div
      className="absolute -bottom-32 left-1/3 w-96 h-96 bg-indigo-600 rounded-full blur-3xl opacity-20"
      animate={{ x: [0, 60, 0], y: [0, -60, 0] }}
      transition={{ duration: 22, repeat: Infinity }}
    />
  </div>
);

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const navigate = useNavigate();
  const { login: authLogin } = useAuth();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const result = await login(email, password);
      if (result.success) {
        authLogin(result.user, result.token);
        navigate('/');
      } else {
        setError(result.error || 'Login failed');
      }
    } catch {
      setError("Connection failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const benefits = [
    { icon: <Shield className="h-5 w-5" />, text: "Secure Writing Sessions" },
    { icon: <Sparkles className="h-5 w-5" />, text: "Intelligent Story Analysis" },
    { icon: <Zap className="h-5 w-5" />, text: "Instant Script Insights" }
  ];

  return (
    <div className="relative min-h-screen flex items-center justify-center px-4 py-20 text-white">
      <AnimatedBackground />

      <div className="relative z-10 w-full max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-10 items-center">

        {/* LEFT */}
        <motion.div
          initial={{ opacity: 0, x: -60 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
          className="hidden lg:block space-y-6"
        >
          <div className="inline-block p-4 bg-gradient-to-r from-purple-500 to-blue-500 rounded-2xl">
            <LogIn className="h-12 w-12 text-white" />
          </div>

          <h1 className="text-5xl font-bold leading-tight">
            Welcome Back  
            <br />
            <span className="bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
              To Your Script Studio
            </span>
          </h1>

          <p className="text-xl text-neutral-300">
            Write smarter stories, visualize characters, and track relationships effortlessly.
          </p>

          <div className="space-y-4 pt-4">
            {benefits.map((b, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 + i * 0.1 }}
                className="flex items-center space-x-3 bg-white/5 backdrop-blur p-4 rounded-xl border border-white/10"
              >
                <div className="p-2 bg-gradient-to-r from-purple-500 to-blue-500 rounded-lg">
                  {b.icon}
                </div>
                <span className="text-neutral-200 font-medium">{b.text}</span>
              </motion.div>
            ))}
          </div>

          <div className="pt-6 bg-white/5 backdrop-blur p-6 rounded-xl border border-white/10">
            <div className="flex space-x-3">
              <CheckCircle className="h-6 w-6 text-purple-400 mt-1" />
              <div>
                <p className="font-semibold">Your stories stay private</p>
                <p className="text-sm text-neutral-400">
                  All scripts and graphs are securely stored and protected.
                </p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* FORM */}
        <motion.div
          initial={{ opacity: 0, x: 60 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl p-8 lg:p-10">

            <h2 className="text-3xl font-bold mb-2 bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
              Sign In
            </h2>
            <p className="text-neutral-400 mb-8">
              Access your smart writing workspace
            </p>

            <form onSubmit={handleLogin} className="space-y-5">

              <div>
                <label className="font-semibold text-neutral-300 mb-2 block">Email</label>
                <div className="relative">
                  <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-neutral-400" />
                  <input
                    type="email"
                    className="w-full pl-12 py-3 rounded-xl bg-black border border-white/10 focus:ring-2 focus:ring-purple-500 text-white"
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                    required
                  />
                </div>
              </div>

              <div>
                <label className="font-semibold text-neutral-300 mb-2 block">Password</label>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-neutral-400" />
                  <input
                    type="password"
                    className="w-full pl-12 py-3 rounded-xl bg-black border border-white/10 focus:ring-2 focus:ring-purple-500 text-white"
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                    required
                  />
                </div>
              </div>

              {error && (
                <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-3 rounded-xl">
                  {error}
                </div>
              )}

              <motion.button
                type="submit"
                disabled={isLoading}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="w-full bg-gradient-to-r from-purple-500 to-blue-500 py-4 rounded-xl font-semibold flex justify-center gap-2"
              >
                {isLoading ? <Loader className="animate-spin" /> : "Enter Studio"}
                {!isLoading && <ArrowRight />}
              </motion.button>
            </form>

            <p className="mt-8 text-center text-neutral-400 text-sm">
              New here?{" "}
              <Link to="/signup" className="text-purple-400 font-semibold">
                Create account →
              </Link>
            </p>

            <div className="mt-8 text-center text-xs text-neutral-500">
              Private & Secure Workspace
            </div>

          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Login;
