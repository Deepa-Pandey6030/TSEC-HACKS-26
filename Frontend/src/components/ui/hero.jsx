import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Shield, Zap, Eye, AlertTriangle } from 'lucide-react';
import { cn } from '../../utils/cn';
import { useTheme } from '../../lib/theme-provider';
import { Button } from './button';

export function Hero({ 
  className,
  headline = "Explore stories as living knowledge — not static text.",
  subheading = "Transform manuscripts into intelligent knowledge graphs where characters, locations, and relationships evolve in real time through autonomous AI agents.",
  ctaPrimary = "Visualize My Graph",
  ctaSecondary = "How It Works"
}) 
 {
  const { isReducedMotion } = useTheme();
  const [displayedText, setDisplayedText] = useState('');
  const [isTypingComplete, setIsTypingComplete] = useState(false);

  // Typewriter effect for headline
  useEffect(() => {
    if (isReducedMotion) {
      setDisplayedText(headline);
      setIsTypingComplete(true);
      return;
    }

    let currentIndex = 0;
    const timer = setInterval(() => {
      if (currentIndex <= headline.length) {
        setDisplayedText(headline.slice(0, currentIndex));
        currentIndex++;
      } else {
        setIsTypingComplete(true);
        clearInterval(timer);
      }
    }, 50);

    return () => clearInterval(timer);
  }, [headline, isReducedMotion]);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
        delayChildren: 0.3
      }
    }
  };

  const itemVariants = {
    hidden: { y: 30, opacity: 0 },
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

  const floatingIconVariants = {
    floating: {
      y: [0, -10, 0],
      transition: {
        duration: 3,
        repeat: Infinity,
        ease: "easeInOut"
      }
    }
  };

  return (
    <section className={cn('relative min-h-screen flex items-center justify-center overflow-hidden', className)}>
      {/* Animated background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary-50 via-secondary-50 to-neutral-50 dark:from-neutral-900 dark:via-neutral-800 dark:to-neutral-900" />
      
      {/* Floating background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          className="absolute top-20 left-20 w-72 h-72 bg-primary-500/10 rounded-full blur-3xl"
          animate={isReducedMotion ? {} : {
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.6, 0.3]
          }}
          transition={{
            duration: 4,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
        <motion.div
          className="absolute bottom-20 right-20 w-96 h-96 bg-secondary-500/10 rounded-full blur-3xl"
          animate={isReducedMotion ? {} : {
            scale: [1.2, 1, 1.2],
            opacity: [0.4, 0.2, 0.4]
          }}
          transition={{
            duration: 5,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
      </div>

      <div className="container mx-auto px-6 relative z-10">
        <motion.div
          className="max-w-6xl mx-auto text-center"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {/* Headline with typewriter effect */}
          <motion.div
            variants={itemVariants}
            className="mb-8"
          >
            <h1 className="text-5xl md:text-7xl font-bold bg-gradient-to-r from-neutral-900 via-primary-600 to-secondary-600 dark:from-neutral-100 dark:via-primary-400 dark:to-secondary-400 bg-clip-text text-transparent leading-tight">
              {displayedText}
              {!isTypingComplete && (
                <motion.span
                  className="inline-block w-1 h-16 md:h-20 bg-primary-500 ml-2"
                  animate={{ opacity: [1, 0] }}
                  transition={{ duration: 0.8, repeat: Infinity }}
                />
              )}
            </h1>
          </motion.div>

          {/* Subheading with micro-parallax */}
          <motion.div
            variants={itemVariants}
            className="mb-12"
            animate={isReducedMotion ? {} : { y: [0, -2, 0] }}
            transition={{
              duration: 4,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          >
            <p className="text-xl md:text-2xl text-neutral-600 dark:text-neutral-400 leading-relaxed max-w-4xl mx-auto">
              {subheading}
            </p>
          </motion.div>

          {/* CTA Buttons */}
          <motion.div
            variants={itemVariants}
            className="flex flex-col sm:flex-row items-center justify-center gap-6 mb-16"
          >
            <Button size="lg" className="min-w-[200px]">
              {ctaPrimary}
            </Button>
            <Button variant="outline" size="lg" className="min-w-[200px]">
              {ctaSecondary}
            </Button>
          </motion.div>

          {/* Floating illustration */}
          <motion.div
            variants={itemVariants}
            className="relative"
          >
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto">
              {[
                { icon: Shield, label: 'Sentinel Agents', color: 'primary' },
                { icon: Eye, label: 'Detective Agents', color: 'secondary' },
                { icon: Zap, label: 'Crisis Response', color: 'accent' },
                { icon: AlertTriangle, label: 'Early Warning', color: 'warning' }
              ].map((item, index) => (
                <motion.div
                  key={item.label}
                  className="relative group"
                  variants={floatingIconVariants}
                  animate={isReducedMotion ? {} : "floating"}
                  transition={{ delay: index * 0.2 }}
                  whileHover={isReducedMotion ? {} : { scale: 1.05, y: -5 }}
                >
                  <div className="bg-white/90 dark:bg-neutral-800/90 backdrop-blur-xl rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-neutral-200/50 dark:border-neutral-700/50 group-hover:border-primary-500/30">
                    <div className={cn(
                      'w-12 h-12 rounded-xl flex items-center justify-center mb-4 mx-auto',
                      item.color === 'primary' && 'bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400',
                      item.color === 'secondary' && 'bg-secondary-100 dark:bg-secondary-900/30 text-secondary-600 dark:text-secondary-400',
                      item.color === 'accent' && 'bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400',
                      item.color === 'warning' && 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-600 dark:text-yellow-400'
                    )}>
                      <item.icon size={24} />
                    </div>
                    <h3 className="font-semibold text-neutral-900 dark:text-neutral-100 text-sm">
                      {item.label}
                    </h3>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </motion.div>
      </div>

      {/* Scroll indicator */}
      <motion.div
        className="absolute bottom-8 left-1/2 transform -translate-x-1/2"
        animate={isReducedMotion ? {} : { y: [0, 10, 0] }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      >
        <div className="w-6 h-10 border-2 border-neutral-400 dark:border-neutral-600 rounded-full flex justify-center">
          <motion.div
            className="w-1 h-2 bg-neutral-600 dark:bg-neutral-400 rounded-full mt-2"
            animate={isReducedMotion ? {} : { y: [0, 12, 0] }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />
        </div>
      </motion.div>
    </section>
  );
}