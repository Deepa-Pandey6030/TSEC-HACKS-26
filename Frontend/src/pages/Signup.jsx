import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { UserPlus, Mail, Lock, User as UserIcon, Loader, CheckCircle, Sparkles, Shield, Zap, ArrowRight } from 'lucide-react';
import { signup } from '../services/auth';
import { useAuth } from '../context/AuthContext';

const AnimatedBackground = () => (
  <div className="absolute inset-0 overflow-hidden pointer-events-none">
    <div className="absolute inset-0 bg-black" />

    {[...Array(18)].map((_, i) => (
      <motion.div
        key={i}
        className="absolute w-2 h-2 bg-purple-500 rounded-full opacity-20"
        initial={{
          x: Math.random() * (typeof window !== 'undefined' ? window.innerWidth : 1000),
          y: Math.random() * (typeof window !== 'undefined' ? window.innerHeight : 1000),
        }}
        animate={{
          x: Math.random() * (typeof window !== 'undefined' ? window.innerWidth : 1000),
          y: Math.random() * (typeof window !== 'undefined' ? window.innerHeight : 1000),
        }}
        transition={{
          duration: Math.random() * 20 + 10,
          repeat: Infinity,
          repeatType: "reverse",
          ease: "linear",
        }}
      />
    ))}

    <motion.div
      className="absolute top-24 left-10 w-40 h-40 bg-purple-600 rounded-full blur-3xl opacity-20"
      animate={{ y: [0, -30, 0] }}
      transition={{ duration: 8, repeat: Infinity }}
    />
    <motion.div
      className="absolute bottom-24 right-20 w-36 h-36 bg-blue-600 rounded-full blur-3xl opacity-20"
      animate={{ y: [0, 30, 0] }}
      transition={{ duration: 6, repeat: Infinity }}
    />
  </div>
);

const Signup = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const navigate = useNavigate();
  const { login: authLogin } = useAuth();

  const submit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters long');
      return;
    }

    setIsLoading(true);

    try {
      const result = await signup(name, email, password);

      if (result.success) {
        setSuccess('Account created! Opening your writing studio...');
        authLogin(result.user, result.token);
        setTimeout(() => navigate('/'), 1000);
      } else {
        setError(result.error);
        setIsLoading(false);
      }
    } catch {
      setError('Connection failed. Please try again.');
      setIsLoading(false);
    }
  };

  const benefits = [
    { icon: <Sparkles className="h-5 w-5" />, text: "Smart Script Insights" },
    { icon: <Shield className="h-5 w-5" />, text: "Private Writing Space" },
    { icon: <Zap className="h-5 w-5" />, text: "Instant Story Visualization" }
  ];

  return (
    <div className="relative min-h-screen flex items-center justify-center px-4 py-20 text-white">
      <AnimatedBackground />

      <div className="relative z-10 w-full max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-10 items-center">

        {/* FORM */}
        <motion.div
          initial={{ opacity: 0, x: -60 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl p-8 lg:p-10">

            <h2 className="text-3xl font-bold mb-2 bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
              Create Your Account
            </h2>
            <p className="text-neutral-400 mb-8">
              Start writing smarter stories today
            </p>

            <div className="space-y-5">

              {/* NAME */}
              <div>
                <label className="font-semibold text-neutral-300 mb-2 block">Full Name</label>
                <div className="relative">
                  <UserIcon className="absolute left-4 top-1/2 -translate-y-1/2 text-neutral-400" />
                  <input
                    className="w-full pl-12 py-3 rounded-xl bg-black border border-white/10 text-white focus:ring-2 focus:ring-purple-500"
                    value={name}
                    onChange={e => setName(e.target.value)}
                    required
                  />
                </div>
              </div>

              {/* EMAIL */}
              <div>
                <label className="font-semibold text-neutral-300 mb-2 block">Email</label>
                <div className="relative">
                  <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-neutral-400" />
                  <input
                    type="email"
                    className="w-full pl-12 py-3 rounded-xl bg-black border border-white/10 text-white focus:ring-2 focus:ring-purple-500"
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                    required
                  />
                </div>
              </div>

              {/* PASSWORD */}
              <div>
                <label className="font-semibold text-neutral-300 mb-2 block">Password</label>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-neutral-400" />
                  <input
                    type="password"
                    className="w-full pl-12 py-3 rounded-xl bg-black border border-white/10 text-white focus:ring-2 focus:ring-purple-500"
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                    required
                  />
                </div>
              </div>

              {/* CONFIRM */}
              <div>
                <label className="font-semibold text-neutral-300 mb-2 block">Confirm Password</label>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-neutral-400" />
                  <input
                    type="password"
                    className="w-full pl-12 py-3 rounded-xl bg-black border border-white/10 text-white focus:ring-2 focus:ring-purple-500"
                    value={confirmPassword}
                    onChange={e => setConfirmPassword(e.target.value)}
                    required
                  />
                </div>
              </div>

              {error && (
                <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-3 rounded-xl">
                  {error}
                </div>
              )}

              {success && (
                <div className="bg-green-500/10 border border-green-500/20 text-green-400 p-3 rounded-xl flex items-center gap-2">
                  <CheckCircle size={18} /> {success}
                </div>
              )}

              <motion.button
                onClick={submit}
                disabled={isLoading}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="w-full bg-gradient-to-r from-purple-500 to-blue-500 py-4 rounded-xl font-semibold flex justify-center gap-2"
              >
                {isLoading ? <Loader className="animate-spin" /> : "Create Studio"}
                {!isLoading && <ArrowRight />}
              </motion.button>
            </div>

            <p className="mt-8 text-center text-neutral-400 text-sm">
              Already have an account?{" "}
              <Link to="/" className="text-purple-400 font-semibold">
                Sign in →
              </Link>
            </p>
          </div>
        </motion.div>

        {/* RIGHT CONTENT */}
        <motion.div
          initial={{ opacity: 0, x: 60 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
          className="hidden lg:block space-y-6"
        >
          <div className="inline-block p-4 bg-gradient-to-r from-purple-500 to-blue-500 rounded-2xl">
            <UserPlus className="h-12 w-12 text-white" />
          </div>

          <h1 className="text-5xl font-bold leading-tight">
            Start Your  
            <br />
            <span className="bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
              Writing Journey
            </span>
          </h1>

          <p className="text-xl text-neutral-300">
            Organize stories, visualize characters, and track relationships effortlessly.
          </p>

          <div className="space-y-4 pt-4">
            {benefits.map((b, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 + i * 0.1 }}
                className="flex items-center gap-3 bg-white/5 backdrop-blur p-4 rounded-xl border border-white/10"
              >
                <div className="p-2 bg-gradient-to-r from-purple-500 to-blue-500 rounded-lg">
                  {b.icon}
                </div>
                <span className="text-neutral-200">{b.text}</span>
              </motion.div>
            ))}
          </div>
        </motion.div>

      </div>
    </div>
  );
};

export default Signup;
