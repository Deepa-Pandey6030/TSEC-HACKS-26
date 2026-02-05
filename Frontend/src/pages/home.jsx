import React from 'react';
import { motion } from 'framer-motion';
import { Hero } from '../components/ui/hero';
import { Card } from '../components/ui/card';
import { useTheme } from '../lib/theme-provider';

const features = [
  {
    image: 'https://images.pexels.com/photos/3747463/pexels-photo-3747463.jpeg?auto=compress&cs=tinysrgb&w=800',
    title: 'Forensic Literary Audit',
    meta: 'CRITIQUE ENGINE',
    description: 'An autonomous "Senior Editor" that reads your Neo4j database to generate award-winning level critiques, identifying pacing issues and thematic inconsistencies.',
    link: '/critique-view'
  },
  {
    image: 'https://images.pexels.com/photos/1742370/pexels-photo-1742370.jpeg?auto=compress&cs=tinysrgb&w=800',
    title: 'Continuity Validator',
    meta: 'LOGIC CHECK',
    description: 'Stop "ghosts" and time-travel errors. Our deterministic engine flags logical paradoxes (e.g., dead characters acting) before you publish.',
    link: '/validator'
  },
  {
    image: 'https://images.pexels.com/photos/196644/pexels-photo-196644.jpeg?auto=compress&cs=tinysrgb&w=800',
    title: 'Narrative Knowledge Graph',
    meta: 'VISUALIZATION',
    description: 'See your story\'s architecture. Visualize complex character relationships, event timelines, and causal chains in an interactive 3D graph.',
    link: '/graph-view'
  },
  {
    image: 'https://images.pexels.com/photos/261763/pexels-photo-261763.jpeg?auto=compress&cs=tinysrgb&w=800',
    title: 'AI Creative Partner',
    meta: 'ASSISTANT',
    description: 'Brainstorm with an AI that actually knows your world rules. Generate scene ideas that respect the established facts in your database.',
    link: '/creative-assistant'
  },
  {
    image: 'https://images.pexels.com/photos/590022/pexels-photo-590022.jpeg?auto=compress&cs=tinysrgb&w=800',
    title: 'Story Health Analytics',
    meta: 'DASHBOARD',
    description: 'Real-time metrics on character dormancy, narrative density, and tension curves. Know exactly when your story is dragging.',
    link: '/dashboard'
  },
  {
    image: 'https://images.pexels.com/photos/11035471/pexels-photo-11035471.jpeg?auto=compress&cs=tinysrgb&w=800',
    title: 'World Management Suite',
    meta: 'DATABASE',
    description: 'Manage your lore, character sheets, and inventory. A centralized repository for every atom of your fictional universe.',
    link: '/products'
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
    <div className="min-h-screen bg-gradient-to-br from-stone-50 via-stone-100 to-stone-200 dark:from-stone-900 dark:via-neutral-900 dark:to-stone-950">
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
            <h2 className="text-4xl md:text-5xl font-serif font-bold text-stone-900 dark:text-stone-100 mb-6">
              The Engine for Modern Storytelling
            </h2>
            <p className="text-xl text-stone-600 dark:text-stone-400 max-w-3xl mx-auto leading-relaxed font-light">
              NOLAN isn't just a chatbot—it's a cognitive architecture. By combining 
              <span className="font-semibold text-stone-800 dark:text-stone-200"> Neo4j's logical memory</span> with 
              <span className="font-semibold text-stone-800 dark:text-stone-200"> Large Language Models</span>, 
              we ensure your story is not just creative, but structurally sound.
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