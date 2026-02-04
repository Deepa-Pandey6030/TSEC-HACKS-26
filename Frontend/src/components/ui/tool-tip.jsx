import React, { forwardRef, useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '../../utils/cn';
import { useTheme } from '../../lib/theme-provider';

export const Tooltip = forwardRef(
  ({ content, children, position = 'top', delay = 500 }, ref) => {
    const { isReducedMotion } = useTheme();
    const [isVisible, setIsVisible] = useState(false);
    const [computedPosition, setComputedPosition] = useState(position);
    const triggerRef = useRef(null);
    const timeoutRef = useRef();

    const showTooltip = () => {
      timeoutRef.current = setTimeout(() => {
        setIsVisible(true);
      }, delay);
    };

    const hideTooltip = () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      setIsVisible(false);
    };

    // Smart positioning
    useEffect(() => {
      if (!isVisible || !triggerRef.current) return;

      const rect = triggerRef.current.getBoundingClientRect();
      const viewport = {
        width: window.innerWidth,
        height: window.innerHeight
      };

      let newPosition = position;

      // Check if tooltip would go off-screen and adjust
      if (position === 'top' && rect.top < 60) {
        newPosition = 'bottom';
      } else if (position === 'bottom' && rect.bottom > viewport.height - 60) {
        newPosition = 'top';
      } else if (position === 'left' && rect.left < 120) {
        newPosition = 'right';
      } else if (position === 'right' && rect.right > viewport.width - 120) {
        newPosition = 'left';
      }

      setComputedPosition(newPosition);
    }, [isVisible, position]);

    const tooltipVariants = {
      hidden: { 
        opacity: 0,
        scale: isReducedMotion ? 1 : 0.9,
        y: isReducedMotion ? 0 : computedPosition === 'top' ? 10 : computedPosition === 'bottom' ? -10 : 0,
        x: isReducedMotion ? 0 : computedPosition === 'left' ? 10 : computedPosition === 'right' ? -10 : 0
      },
      visible: { 
        opacity: 1,
        scale: 1,
        y: 0,
        x: 0,
        transition: {
          type: "spring",
          stiffness: 140,
          damping: 20,
          duration: 0.15
        }
      }
    };

    const positionClasses = {
      top: 'bottom-full left-1/2 transform -translate-x-1/2 mb-2',
      bottom: 'top-full left-1/2 transform -translate-x-1/2 mt-2',
      left: 'right-full top-1/2 transform -translate-y-1/2 mr-2',
      right: 'left-full top-1/2 transform -translate-y-1/2 ml-2'
    };

    const arrowClasses = {
      top: 'top-full left-1/2 transform -translate-x-1/2 border-l-transparent border-r-transparent border-b-transparent border-t-neutral-800 dark:border-t-neutral-200',
      bottom: 'bottom-full left-1/2 transform -translate-x-1/2 border-l-transparent border-r-transparent border-t-transparent border-b-neutral-800 dark:border-b-neutral-200',
      left: 'left-full top-1/2 transform -translate-y-1/2 border-t-transparent border-b-transparent border-r-transparent border-l-neutral-800 dark:border-l-neutral-200',
      right: 'right-full top-1/2 transform -translate-y-1/2 border-t-transparent border-b-transparent border-l-transparent border-r-neutral-800 dark:border-r-neutral-200'
    };

    return (
      <div
        ref={triggerRef}
        className="relative inline-block"
        onMouseEnter={showTooltip}
        onMouseLeave={hideTooltip}
        onFocus={showTooltip}
        onBlur={hideTooltip}
      >
        {children}
        
        <AnimatePresence>
          {isVisible && (
            <motion.div
              className={cn(
                'absolute z-50 px-3 py-2 text-sm font-medium text-white bg-neutral-800 dark:bg-neutral-200 dark:text-neutral-900 rounded-lg shadow-lg pointer-events-none whitespace-nowrap',
                positionClasses[computedPosition]
              )}
              variants={tooltipVariants}
              initial="hidden"
              animate="visible"
              exit="hidden"
            >
              {content}
              
              {/* Arrow */}
              <div
                className={cn(
                  'absolute w-0 h-0 border-4',
                  arrowClasses[computedPosition]
                )}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    );
  }
);

Tooltip.displayName = 'Tooltip';