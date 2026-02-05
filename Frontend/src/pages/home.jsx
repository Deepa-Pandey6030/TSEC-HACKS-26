import React from 'react';
import { motion } from 'framer-motion';
import { Hero } from '../components/ui/hero';
import { Card } from '../components/ui/card';
import { useTheme } from '../lib/theme-provider';

const features = [
  {
    image: 'https://images.pexels.com/photos/7688336/pexels-photo-7688336.jpeg?auto=compress&cs=tinysrgb&w=800',
    title: 'AI Creative Assistant',
    meta: 'AI ASSISTANT',
    description: 'Senior Writer AI with 30+ years of experience provides intelligent creative guidance, analyzes narrative health, and suggests improvements for your story.',
    link: '/creative-assistant'
  },
  {
    image: 'https://images.pexels.com/photos/8728382/pexels-photo-8728382.jpeg?auto=compress&cs=tinysrgb&w=800',
    title: 'Dashboard & Analytics',
    meta: 'ANALYTICS',
    description: 'Real-time visualization of content analysis, credibility scores, and performance metrics across all your projects.',
    link: '/dashboard'
  },
  {
    image: 'https://images.pexels.com/photos/8728380/pexels-photo-8728380.jpeg?auto=compress&cs=tinysrgb&w=800',
    title: 'Products & Services',
    meta: 'MARKETPLACE',
    description: 'Browse our comprehensive suite of AI-powered tools for content verification, monitoring, and authentic engagement.',
    link: '/products'
  },
  {
    image: 'https://images.pexels.com/photos/8728381/pexels-photo-8728381.jpeg?auto=compress&cs=tinysrgb&w=800',
    title: 'Continuity Validator',
    meta: 'VERIFICATION',
    description: 'Check for narrative inconsistencies, continuity errors, and verify content coherence across multiple documents.',
    link: '/validator'
  },
  {
    image: 'https://images.pexels.com/photos/7688334/pexels-photo-7688334.jpeg?auto=compress&cs=tinysrgb&w=800',
    title: 'Graph Visualization',
    meta: 'NETWORK ANALYSIS',
    description: 'Visualize content relationships, narrative connections, and misinformation spread patterns in an interactive graph.',
    link: '/graph-view'
  },
  {
    image: 'https://images.pexels.com/photos/8728383/pexels-photo-8728383.jpeg?auto=compress&cs=tinysrgb&w=800',
    title: 'Critique & Review',
    meta: 'QUALITY ASSURANCE',
    description: 'Get comprehensive feedback on content quality, tone, and messaging with actionable recommendations.',
    link: '/critique-view'
  }
];

export function HomePage() {
  const { isReducedMotion } = useTheme();

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: isReducedMotion ? 0 : 0.1,
        delayChildren: 0.3
      }
    }
  };

  const cardVariants = {
    hidden: { y: 50, opacity: 0 },
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
    <div className="min-h-screen bg-gradient-to-br from-neutral-50 via-primary-50/30 to-secondary-50/30 dark:from-neutral-900 dark:via-neutral-800 dark:to-neutral-900">
      <Hero />

      <section className="py-24 px-6">
        <div className="container mx-auto">
          <motion.div
            className="text-center mb-16"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{
              type: "spring",
              stiffness: 140,
              damping: 20
            }}
          >
            <h2 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-neutral-900 via-primary-600 to-secondary-600 dark:from-neutral-100 dark:via-primary-400 dark:to-secondary-400 bg-clip-text text-transparent mb-6">
              Revolutionary Features
            </h2>
            <p className="text-xl text-neutral-600 dark:text-neutral-400 max-w-3xl mx-auto leading-relaxed">
              Discover how TruthShield's advanced AI agents work together to create an autonomous misinformation defense system.
            </p>
          </motion.div>

          <motion.div
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-200px" }}
          >
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                variants={cardVariants}
              >
                <Card
                  image={feature.image}
                  title={feature.title}
                  meta={feature.meta}
                  description={feature.description}
                  link={feature.link}
                />
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>
    </div>
  );
}