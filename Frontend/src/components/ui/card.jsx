import React, { forwardRef, useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, ExternalLink, Heart } from 'lucide-react';
import { cn } from '../../utils/cn';
import { useTheme } from '../../lib/theme-provider';

export const Card = forwardRef(
  ({ className, image, title, meta, description, href, actions = true, children, ...props }, ref) => {
    const { isReducedMotion } = useTheme();
    const [isHovered, setIsHovered] = useState(false);
    const cardRef = useRef(null);
    const [rotateX, setRotateX] = useState(0);
    const [rotateY, setRotateY] = useState(0);

    const handleMouseMove = (e) => {
      if (isReducedMotion || !cardRef.current) return;
      
      const rect = cardRef.current.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;
      
      const maxTilt = 8;
      const tiltX = ((e.clientY - centerY) / (rect.height / 2)) * -maxTilt;
      const tiltY = ((e.clientX - centerX) / (rect.width / 2)) * maxTilt;
      
      setRotateX(tiltX);
      setRotateY(tiltY);
    };

    const handleMouseLeave = () => {
      setIsHovered(false);
      setRotateX(0);
      setRotateY(0);
    };

    const cardVariants = {
      initial: { 
        scale: 1, 
        y: 0,
        rotateX: 0,
        rotateY: 0
      },
      hover: { 
        scale: isReducedMotion ? 1 : 1.03,
        y: isReducedMotion ? 0 : -6,
        rotateX: isReducedMotion ? 0 : rotateX,
        rotateY: isReducedMotion ? 0 : rotateY,
        transition: {
          type: "spring",
          stiffness: 140,
          damping: 20
        }
      }
    };

    const glowVariants = {
      initial: { opacity: 0 },
      hover: { opacity: isReducedMotion ? 0 : 1 }
    };

    const actionVariants = {
      initial: { y: 20, opacity: 0 },
      hover: { 
        y: 0, 
        opacity: 1,
        transition: {
          type: "spring",
          stiffness: 140,
          damping: 20
        }
      }
    };

    const CardContent = (
      <motion.div
        ref={cardRef}
        className={cn(
          'relative group bg-white/80 dark:bg-neutral-900/80 backdrop-blur-xl rounded-2xl overflow-hidden border border-neutral-200/50 dark:border-neutral-700/50',
          'hover:border-primary-500/50 transition-all duration-300',
          className
        )}
        variants={cardVariants}
        initial="initial"
        animate="initial"
        whileHover="hover"
        onMouseMove={handleMouseMove}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={handleMouseLeave}
        style={{ 
          perspective: 1000,
          transformStyle: "preserve-3d"
        }}
        {...props}
      >
        {/* Animated border glow */}
        <motion.div
          className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"
          style={{
            background: 'linear-gradient(45deg, transparent, rgba(0, 217, 255, 0.1), transparent)',
            animation: isHovered && !isReducedMotion ? 'gradient-sweep 2s ease-in-out infinite' : 'none'
          }}
          variants={glowVariants}
          initial="initial"
          animate={isHovered ? "hover" : "initial"}
        />

        {/* Glow effect */}
        <motion.div
          className="absolute inset-0 rounded-2xl bg-gradient-to-r from-primary-500/10 to-secondary-500/10 blur-xl -z-10"
          variants={glowVariants}
          initial="initial"
          animate={isHovered ? "hover" : "initial"}
          transition={{ duration: 0.2 }}
        />

        {/* Image */}
        {image && (
          <div className="relative overflow-hidden">
            <img 
              src={image}
              alt={title || ''}
              className="w-full h-48 object-cover transition-transform duration-500 group-hover:scale-105"
            />
          </div>
        )}

        {/* Content */}
        <div className="p-6">
          {meta && (
            <p className="text-sm text-primary-600 dark:text-primary-400 font-medium mb-2">
              {meta}
            </p>
          )}
          
          {title && (
            <h3 className="text-xl font-bold text-neutral-900 dark:text-neutral-100 mb-3 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
              {title}
            </h3>
          )}
          
          {description && (
            <p className="text-neutral-600 dark:text-neutral-400 leading-relaxed mb-4">
              {description}
            </p>
          )}

          {children}

          {/* Animated actions */}
          {actions && (
            <motion.div
              className="flex items-center justify-between mt-6 pt-4 border-t border-neutral-200/50 dark:border-neutral-700/50"
              variants={actionVariants}
              initial="initial"
              animate={isHovered ? "hover" : "initial"}
              transition={{ delay: 0.1 }}
            >
              <div className="flex space-x-3">
                <motion.button
                  className="p-2 rounded-lg bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400 hover:bg-primary-100 dark:hover:bg-primary-900/20 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
                  whileHover={{ scale: isReducedMotion ? 1 : 1.1 }}
                  whileTap={{ scale: isReducedMotion ? 1 : 0.9 }}
                >
                  <Heart size={16} />
                </motion.button>
                <motion.button
                  className="p-2 rounded-lg bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400 hover:bg-primary-100 dark:hover:bg-primary-900/20 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
                  whileHover={{ scale: isReducedMotion ? 1 : 1.1 }}
                  whileTap={{ scale: isReducedMotion ? 1 : 0.9 }}
                >
                  <ExternalLink size={16} />
                </motion.button>
              </div>
              
              <motion.div
                className="flex items-center text-primary-600 dark:text-primary-400 font-medium cursor-pointer group/arrow"
                whileHover={{ x: isReducedMotion ? 0 : 4 }}
              >
                <span className="mr-2">View Details</span>
                <ArrowRight 
                  size={16} 
                  className="transition-transform group-hover/arrow:translate-x-1" 
                />
              </motion.div>
            </motion.div>
          )}
        </div>
      </motion.div>
    );

    return href ? (
      <a href={href} className="block">
        {CardContent}
      </a>
    ) : CardContent;
  }
);

Card.displayName = 'Card';