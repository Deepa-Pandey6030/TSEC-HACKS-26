import React, { forwardRef } from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../utils/cn';
import { useTheme } from '../../lib/theme-provider';

export const Button = forwardRef(
  ({ className, variant = 'primary', size = 'md', children, disabled, ...props }, ref) => {
    const { isReducedMotion } = useTheme();
    
    const baseClasses = 'relative inline-flex items-center justify-center font-medium rounded-xl transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-primary-500/50 disabled:opacity-50 disabled:cursor-not-allowed overflow-hidden';
    
    const variants = {
      primary: 'bg-gradient-to-r from-primary-500 to-primary-600 text-white hover:from-primary-600 hover:to-primary-700 shadow-lg hover:shadow-xl',
      ghost: 'text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800/50',
      outline: 'border-2 border-primary-500/30 text-primary-600 dark:text-primary-400 hover:border-primary-500 hover:bg-primary-50 dark:hover:bg-primary-950/20'
    };
    
    const sizes = {
      sm: 'px-4 py-2 text-sm',
      md: 'px-6 py-3 text-base',
      lg: 'px-8 py-4 text-lg'
    };
    
    const buttonVariants = {
      initial: { scale: 1 },
      hover: { 
        scale: isReducedMotion ? 1 : 1.02,
        y: isReducedMotion ? 0 : -1
      },
      tap: { 
        scale: isReducedMotion ? 1 : 0.98,
        y: isReducedMotion ? 0 : 1
      }
    };
    
    const glowVariants = {
      initial: { opacity: 0, scale: 0.8 },
      hover: { 
        opacity: variant === 'primary' ? (isReducedMotion ? 0 : 0.6) : 0, 
        scale: isReducedMotion ? 0.8 : 1.2 
      }
    };
    
    return (
      <motion.button
        ref={ref}
        className={cn(
          baseClasses,
          variants[variant],
          sizes[size],
          className
        )}
        variants={buttonVariants}
        initial="initial"
        whileHover="hover"
        whileTap="tap"
        transition={{ type: "spring", stiffness: 140, damping: 20 }}
        disabled={disabled}
        {...props}
      >
        {/* Glow effect */}
        {variant === 'primary' && (
          <motion.div
            className="absolute inset-0 rounded-xl bg-gradient-to-r from-primary-400 to-primary-500 blur-md -z-10"
            variants={glowVariants}
            initial="initial"
            animate="initial"
            whileHover="hover"
            transition={{ duration: 0.2 }}
          />
        )}
        
        {/* Content */}
        <span className="relative z-10">
          {children}
        </span>
      </motion.button>
    );
  }
);

Button.displayName = 'Button';