import React, { forwardRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';
import { cn } from '../../utils/cn';
import { useTheme } from '../../lib/theme-provider';

export const Modal = forwardRef(
  ({ className, isOpen, onClose, title, children, ...props }, ref) => {
    const { isReducedMotion } = useTheme();

    // Focus trap and escape key handling
    useEffect(() => {
      if (!isOpen) return;

      const handleEscape = (e) => {
        if (e.key === 'Escape') onClose();
      };

      const focusableElements = document.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      const firstElement = focusableElements[0];
      const lastElement = focusableElements[focusableElements.length - 1];

      const handleTabKey = (e) => {
        if (e.key === 'Tab') {
          if (e.shiftKey && document.activeElement === firstElement) {
            e.preventDefault();
            lastElement.focus();
          } else if (!e.shiftKey && document.activeElement === lastElement) {
            e.preventDefault();
            firstElement.focus();
          }
        }
      };

      document.addEventListener('keydown', handleEscape);
      document.addEventListener('keydown', handleTabKey);

      // Focus first element when modal opens
      setTimeout(() => firstElement?.focus(), 100);

      return () => {
        document.removeEventListener('keydown', handleEscape);
        document.removeEventListener('keydown', handleTabKey);
      };
    }, [isOpen, onClose]);

    const overlayVariants = {
      hidden: { opacity: 0 },
      visible: { 
        opacity: 1,
        transition: { duration: 0.2 }
      },
      exit: { 
        opacity: 0,
        transition: { duration: 0.15 }
      }
    };

    const modalVariants = {
      hidden: { 
        scale: isReducedMotion ? 1 : 0.95, 
        opacity: 0,
        y: isReducedMotion ? 0 : 20
      },
      visible: { 
        scale: 1, 
        opacity: 1,
        y: 0,
        transition: {
          type: "spring",
          stiffness: 140,
          damping: 20,
          delay: 0.1
        }
      },
      exit: { 
        scale: isReducedMotion ? 1 : 0.95, 
        opacity: 0,
        y: isReducedMotion ? 0 : 20,
        transition: { duration: 0.15 }
      }
    };

    return (
      <AnimatePresence>
        {isOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            {/* Backdrop */}
            <motion.div
              className="absolute inset-0 bg-black/50 backdrop-blur-sm"
              variants={overlayVariants}
              initial="hidden"
              animate="visible"
              exit="exit"
              onClick={onClose}
            />

            {/* Modal */}
            <motion.div
              ref={ref}
              className={cn(
                'relative w-full max-w-lg bg-white/90 dark:bg-neutral-900/90 backdrop-blur-xl rounded-2xl shadow-xl',
                'border border-neutral-200/50 dark:border-neutral-700/50 overflow-hidden',
                className
              )}
              variants={modalVariants}
              initial="hidden"
              animate="visible"
              exit="exit"
              onClick={(e) => e.stopPropagation()}
              {...props}
            >
              {/* Header */}
              {title && (
                <div className="flex items-center justify-between p-6 border-b border-neutral-200/50 dark:border-neutral-700/50">
                  <h2 className="text-xl font-bold text-neutral-900 dark:text-neutral-100">
                    {title}
                  </h2>
                  <motion.button
                    className="p-2 rounded-lg text-neutral-500 hover:text-neutral-700 dark:hover:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors"
                    whileHover={{ scale: isReducedMotion ? 1 : 1.05 }}
                    whileTap={{ scale: isReducedMotion ? 1 : 0.95 }}
                    onClick={onClose}
                  >
                    <X size={20} />
                  </motion.button>
                </div>
              )}

              {/* Content */}
              <div className="p-6">
                {children}
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    );
  }
);

Modal.displayName = 'Modal';