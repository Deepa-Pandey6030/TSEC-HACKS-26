import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import { BookOpen, AlertTriangle, CheckCircle, RefreshCw, Sparkles } from 'lucide-react';
import { useTheme } from '../lib/theme-provider';

const Critique = () => {
  const { isReducedMotion } = useTheme();
  const [review, setReview] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchCritique = async () => {
    setLoading(true);
    setError("");
    setReview("");
    
    try {
      const response = await fetch("http://localhost:8000/critique");
      if (!response.ok) throw new Error("Server error");
      const data = await response.json();
      setReview(data.review);
    } catch (err) {
      setError("Could not connect to the Literary Engine. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

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

  return (
    <div className="min-h-screen bg-gradient-to-br from-neutral-50 via-primary-50/30 to-secondary-50/30 dark:from-neutral-900 dark:via-neutral-800 dark:to-neutral-900 px-4 md:px-6 py-8">
      <div className="container mx-auto max-w-4xl">
        {/* Header */}
        <motion.div
          className="mb-12 text-center"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{
            type: "spring",
            stiffness: 140,
            damping: 20
          }}
        >
          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-neutral-900 via-primary-600 to-secondary-600 dark:from-neutral-100 dark:via-primary-400 dark:to-secondary-400 bg-clip-text text-transparent mb-3">
            AI Critique & Review
          </h1>
          <p className="text-lg text-neutral-600 dark:text-neutral-400">
            Get professional editorial feedback on your content
          </p>
        </motion.div>

        <AnimatePresence mode="wait">
          {/* State: IDLE */}
          {!review && !loading && !error && (
            <motion.div
              key="idle"
              variants={itemVariants}
              initial="hidden"
              animate="visible"
              exit="hidden"
              className="relative group"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl blur-xl opacity-25 group-hover:opacity-40 transition-opacity duration-300" />
              <div className="relative bg-white/40 dark:bg-neutral-800/40 backdrop-blur-xl rounded-2xl border border-neutral-200/50 dark:border-neutral-700/50 p-12 text-center">
                <div className="w-16 h-16 rounded-xl bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center mx-auto mb-6">
                  <BookOpen size={32} className="text-white" />
                </div>
                <h2 className="text-2xl font-bold text-neutral-900 dark:text-neutral-100 mb-3">
                  Ready for Professional Critique
                </h2>
                <p className="text-neutral-600 dark:text-neutral-400 max-w-md mx-auto mb-8 text-lg">
                  Get comprehensive editorial feedback analyzing narrative structure, pacing, character consistency, and writing quality.
                </p>
                <motion.button 
                  onClick={fetchCritique}
                  className="px-8 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600 text-white rounded-lg font-semibold transition-all shadow-lg"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  Generate Critique
                </motion.button>
              </div>
            </motion.div>
          )}

          {/* State: LOADING */}
          {loading && (
            <motion.div
              key="loading"
              variants={itemVariants}
              initial="hidden"
              animate="visible"
              exit="hidden"
              className="relative group"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-2xl blur-xl opacity-25 group-hover:opacity-40 transition-opacity duration-300" />
              <div className="relative bg-white/40 dark:bg-neutral-800/40 backdrop-blur-xl rounded-2xl border border-neutral-200/50 dark:border-neutral-700/50 p-12 text-center">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                  className="w-12 h-12 rounded-full bg-gradient-to-r from-blue-500 to-cyan-500 flex items-center justify-center mx-auto mb-6"
                >
                  <RefreshCw size={24} className="text-white" />
                </motion.div>
                <h3 className="text-xl font-bold text-neutral-900 dark:text-neutral-100 mb-4">
                  Analyzing Your Content...
                </h3>
                <div className="space-y-3 max-w-md mx-auto">
                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 }}
                    className="text-neutral-600 dark:text-neutral-400 flex items-center gap-2"
                  >
                    <div className="w-2 h-2 rounded-full bg-primary-500" />
                    Extracting narrative elements...
                  </motion.div>
                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.2 }}
                    className="text-neutral-600 dark:text-neutral-400 flex items-center gap-2"
                  >
                    <div className="w-2 h-2 rounded-full bg-primary-500" />
                    Evaluating structure and pacing...
                  </motion.div>
                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.3 }}
                    className="text-neutral-600 dark:text-neutral-400 flex items-center gap-2"
                  >
                    <div className="w-2 h-2 rounded-full bg-primary-500" />
                    Generating editorial insights...
                  </motion.div>
                </div>
              </div>
            </motion.div>
          )}

          {/* State: ERROR */}
          {error && (
            <motion.div
              key="error"
              variants={itemVariants}
              initial="hidden"
              animate="visible"
              exit="hidden"
              className="relative group"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-red-500 to-orange-500 rounded-2xl blur-xl opacity-25 group-hover:opacity-40 transition-opacity duration-300" />
              <div className="relative bg-white/40 dark:bg-neutral-800/40 backdrop-blur-xl rounded-2xl border border-neutral-200/50 dark:border-neutral-700/50 p-8">
                <div className="flex gap-4">
                  <div className="flex-shrink-0">
                    <AlertTriangle size={24} className="text-red-500" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-neutral-900 dark:text-neutral-100 mb-1">
                      Connection Error
                    </h3>
                    <p className="text-neutral-600 dark:text-neutral-400 mb-4">{error}</p>
                    <motion.button 
                      onClick={fetchCritique}
                      className="text-primary-600 dark:text-primary-400 font-semibold hover:underline"
                      whileHover={{ x: 4 }}
                    >
                      Try Again →
                    </motion.button>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* State: SUCCESS */}
          {review && (
            <motion.div
              key="success"
              variants={itemVariants}
              initial="hidden"
              animate="visible"
              exit="hidden"
              className="relative group"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-green-500 to-emerald-500 rounded-2xl blur-xl opacity-25 group-hover:opacity-40 transition-opacity duration-300" />
              <div className="relative bg-white/40 dark:bg-neutral-800/40 backdrop-blur-xl rounded-2xl border border-neutral-200/50 dark:border-neutral-700/50 overflow-hidden">
                {/* Header */}
                <div className="bg-gradient-to-r from-primary-500 to-secondary-500 px-8 py-6 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <CheckCircle size={24} className="text-white" />
                    <span className="text-white font-semibold text-lg">Editorial Critique</span>
                  </div>
                  <Sparkles size={20} className="text-white" />
                </div>

                {/* Content */}
                <div className="p-8 prose dark:prose-invert max-w-none">
                  <ReactMarkdown
                    components={{
                      h1: ({node, ...props}) => <h1 className="text-3xl font-bold text-neutral-900 dark:text-neutral-100 mt-8 mb-4 border-b-2 border-primary-500/20 pb-2" {...props} />,
                      h2: ({node, ...props}) => <h2 className="text-2xl font-bold text-neutral-900 dark:text-neutral-100 mt-6 mb-3" {...props} />,
                      h3: ({node, ...props}) => <h3 className="text-xl font-bold text-neutral-800 dark:text-neutral-200 mt-5 mb-2 uppercase tracking-wide" {...props} />,
                      p: ({node, ...props}) => <p className="mb-4 text-neutral-700 dark:text-neutral-300 leading-relaxed" {...props} />,
                      strong: ({node, ...props}) => <strong className="font-bold text-neutral-900 dark:text-neutral-100" {...props} />,
                      ul: ({node, ...props}) => <ul className="list-disc list-inside mb-4 space-y-2 text-neutral-700 dark:text-neutral-300" {...props} />,
                      li: ({node, ...props}) => <li className="ml-2" {...props} />,
                      blockquote: ({node, ...props}) => <blockquote className="border-l-4 border-primary-500 pl-4 italic my-4 text-neutral-600 dark:text-neutral-400" {...props} />,
                    }}
                  >
                    {review}
                  </ReactMarkdown>
                </div>

                {/* Footer */}
                <div className="bg-neutral-100/50 dark:bg-neutral-700/30 px-8 py-4 border-t border-neutral-200/50 dark:border-neutral-700/50 flex justify-between items-center">
                  <p className="text-sm text-neutral-500 dark:text-neutral-400">
                    Analysis complete • Powered by AI
                  </p>
                  <motion.button 
                    onClick={fetchCritique}
                    className="flex items-center gap-2 text-primary-600 dark:text-primary-400 font-semibold hover:text-primary-700 dark:hover:text-primary-300 transition-colors"
                    whileHover={{ x: 4 }}
                  >
                    <RefreshCw size={16} />
                    New Analysis
                  </motion.button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default Critique;