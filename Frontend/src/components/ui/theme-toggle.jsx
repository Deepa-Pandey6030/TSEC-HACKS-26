import React from 'react';
import { motion } from 'framer-motion';
import { Sun, Moon, Monitor, Volume2, VolumeX } from 'lucide-react';
import { useTheme } from '../../lib/theme-provider';
import { Button } from './button';
import { Tooltip } from './tool-tip';

export function ThemeToggle() {
  const { theme, setTheme, motionPreference, setMotionPreference, isReducedMotion } = useTheme();

  const themeIcons = {
    light: Sun,
    dark: Moon,
    system: Monitor
  };

  const CurrentThemeIcon = themeIcons[theme];

  const nextTheme = () => {
    const themes = ['light', 'dark', 'system'];
    const currentIndex = themes.indexOf(theme);
    const nextIndex = (currentIndex + 1) % themes.length;
    setTheme(themes[nextIndex]);
  };

  const toggleMotion = () => {
    setMotionPreference(motionPreference === 'full' ? 'reduced' : 'full');
  };

  return (
    <div className="flex items-center space-x-2">
      <Tooltip content={`Current theme: ${theme}`}>
        <Button
          variant="ghost"
          size="sm"
          onClick={nextTheme}
          className="p-2"
        >
          <motion.div
            key={theme}
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{
              type: "spring",
              stiffness: 140,
              damping: 20
            }}
          >
            <CurrentThemeIcon size={18} />
          </motion.div>
        </Button>
      </Tooltip>

      <Tooltip content={`Motion: ${motionPreference}`}>
        <Button
          variant="ghost"
          size="sm"
          onClick={toggleMotion}
          className="p-2"
        >
          <motion.div
            animate={{ rotate: isReducedMotion ? 0 : [0, 10, -10, 0] }}
            transition={{ duration: 0.5 }}
          >
            {isReducedMotion ? <VolumeX size={18} /> : <Volume2 size={18} />}
          </motion.div>
        </Button>
      </Tooltip>
    </div>
  );
}