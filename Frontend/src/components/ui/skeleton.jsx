import React, { forwardRef } from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../utils/cn';
import { useTheme } from '../../lib/theme-provider';

export const Skeleton = forwardRef(
  ({ className, variant = 'rectangular', width, height, lines = 1, style, ...props }, ref) => {
    const { isReducedMotion } = useTheme();

    const shimmerVariants = {
      initial: { x: '-100%' },
      animate: {
        x: '100%',
        transition: {
          duration: 1.5,
          repeat: Infinity,
          ease: "easeInOut"
        }
      }
    };

    const pulseVariants = {
      initial: { opacity: 0.6 },
      animate: {
        opacity: [0.6, 0.8, 0.6],
        transition: {
          duration: 1.5,
          repeat: Infinity,
          ease: "easeInOut"
        }
      }
    };

    const baseClasses = 'relative overflow-hidden bg-neutral-200 dark:bg-neutral-700';
    
    const variantClasses = {
      text: 'h-4 rounded',
      circular: 'rounded-full',
      rectangular: 'rounded-xl'
    };

    const skeletonStyle = {
      width: width || (variant === 'circular' ? '40px' : '100%'),
      height: height || (variant === 'text' ? '16px' : variant === 'circular' ? '40px' : '200px'),
      ...style
    };

    if (variant === 'text' && lines > 1) {
      return (
        <div className="space-y-2">
          {Array.from({ length: lines }).map((_, index) => (
            <motion.div
              key={index}
              ref={index === 0 ? ref : undefined}
              className={cn(baseClasses, variantClasses.text, className)}
              style={{
                ...skeletonStyle,
                width: index === lines - 1 ? '75%' : '100%'
              }}
              variants={isReducedMotion ? pulseVariants : undefined}
              initial="initial"
              animate="animate"
              {...props}
            >
              {!isReducedMotion && (
                <motion.div
                  className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 dark:via-neutral-600/20 to-transparent"
                  variants={shimmerVariants}
                  initial="initial"
                  animate="animate"
                />
              )}
            </motion.div>
          ))}
        </div>
      );
    }

    return (
      <motion.div
        ref={ref}
        className={cn(baseClasses, variantClasses[variant], className)}
        style={skeletonStyle}
        variants={isReducedMotion ? pulseVariants : undefined}
        initial="initial"
        animate="animate"
        {...props}
      >
        {!isReducedMotion && (
          <motion.div
            className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 dark:via-neutral-600/20 to-transparent"
            variants={shimmerVariants}
            initial="initial"
            animate="animate"
          />
        )}
      </motion.div>
    );
  }
);

Skeleton.displayName = 'Skeleton';