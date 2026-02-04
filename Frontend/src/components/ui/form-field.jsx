import React, { forwardRef, useState, useId } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Check, AlertCircle } from 'lucide-react';
import { cn } from '../../utils/cn';
import { useTheme } from '../../lib/theme-provider';

export const FormField = forwardRef(
  ({ className, label, error, success, helperText, type = 'text', ...props }, ref) => {
    const { isReducedMotion } = useTheme();
    const [isFocused, setIsFocused] = useState(false);
    const [hasValue, setHasValue] = useState(false);
    const id = useId();

    const handleFocus = () => setIsFocused(true);
    const handleBlur = (e) => {
      setIsFocused(false);
      setHasValue(e.target.value.length > 0);
      props.onBlur?.(e);
    };

    const handleChange = (e) => {
      setHasValue(e.target.value.length > 0);
      props.onChange?.(e);
    };

    const labelVariants = {
      default: {
        y: 0,
        scale: 1,
        color: "rgb(100, 116, 139)" // neutral-500
      },
      focused: {
        y: -24,
        scale: 0.85,
        color: "rgb(0, 217, 255)", // primary-500
        transition: {
          type: "spring",
          stiffness: 140,
          damping: 20
        }
      }
    };

    const inputVariants = {
      default: {
        boxShadow: "0 0 0 0 rgba(0, 217, 255, 0)"
      },
      focused: {
        boxShadow: isReducedMotion 
          ? "0 0 0 0 rgba(0, 217, 255, 0)"
          : "0 0 0 2px rgba(0, 217, 255, 0.2), 0 0 20px rgba(0, 217, 255, 0.1)"
      }
    };

    const errorShake = {
      x: [0, -10, 10, -10, 10, 0],
      transition: { duration: 0.5 }
    };

    const successCheckmark = {
      scale: [0, 1.2, 1],
      opacity: [0, 1, 1],
      transition: {
        type: "spring",
        stiffness: 200,
        damping: 10
      }
    };

    return (
      <div className={cn('relative', className)}>
        {/* Input container */}
        <div className="relative">
          <motion.input
            ref={ref}
            id={id}
            type={type}
            className={cn(
              'w-full px-4 py-4 bg-white/80 dark:bg-neutral-900/80 backdrop-blur-xl rounded-xl border-2 transition-all duration-200',
              'focus:outline-none focus:ring-0',
              error 
                ? 'border-red-500 text-red-900 dark:text-red-400' 
                : success
                ? 'border-green-500 text-green-900 dark:text-green-400'
                : 'border-neutral-300 dark:border-neutral-600 text-neutral-900 dark:text-neutral-100',
              'placeholder:text-transparent'
            )}
            variants={inputVariants}
            animate={isFocused ? "focused" : "default"}
            onFocus={handleFocus}
            onBlur={handleBlur}
            onChange={handleChange}
            {...props}
          />

          {/* Floating label */}
          <motion.label
            htmlFor={id}
            className="absolute left-4 top-4 pointer-events-none origin-left transition-colors duration-200"
            variants={labelVariants}
            animate={isFocused || hasValue ? "focused" : "default"}
          >
            {label}
          </motion.label>

          {/* Success/Error icons */}
          <AnimatePresence>
            {success && (
              <motion.div
                className="absolute right-4 top-1/2 transform -translate-y-1/2"
                variants={successCheckmark}
                initial={{ scale: 0, opacity: 0 }}
                animate="scale"
                exit={{ scale: 0, opacity: 0 }}
              >
                <Check className="w-5 h-5 text-green-500" />
              </motion.div>
            )}
            {error && (
              <motion.div
                className="absolute right-4 top-1/2 transform -translate-y-1/2"
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0, opacity: 0 }}
              >
                <AlertCircle className="w-5 h-5 text-red-500" />
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Error message with shake animation */}
        <AnimatePresence>
          {error && (
            <motion.p
              className="mt-2 text-sm text-red-600 dark:text-red-400"
              initial={{ opacity: 0, y: -10 }}
              animate={isReducedMotion ? { opacity: 1, y: 0 } : { opacity: 1, y: 0, ...errorShake }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ type: "spring", stiffness: 140, damping: 20 }}
            >
              {error}
            </motion.p>
          )}
        </AnimatePresence>

        {/* Helper text */}
        {helperText && !error && (
          <motion.p
            className="mt-2 text-sm text-neutral-500 dark:text-neutral-400"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ type: "spring", stiffness: 140, damping: 20 }}
          >
            {helperText}
          </motion.p>
        )}
      </div>
    );
  }
);

FormField.displayName = 'FormField';