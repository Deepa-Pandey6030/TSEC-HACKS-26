import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Filter, Plus, Grid, List } from 'lucide-react';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { FormField } from '../components/ui/form-field';
import { Skeleton } from '../components/ui/skeleton';
import { useTheme } from '../lib/theme-provider';
import { cn } from '../utils/cn';

const products = [
  {
    id: 1,
    image: 'https://images.pexels.com/photos/7688336/pexels-photo-7688336.jpeg?auto=compress&cs=tinysrgb&w=800',
    title: 'Sentinel Agent Pro',
    meta: 'MONITORING',
    description: 'Advanced content monitoring with real-time pattern recognition and viral prediction capabilities.',
    price: '$299/month'
  },
  {
    id: 2,
    image: 'https://images.pexels.com/photos/8728382/pexels-photo-8728382.jpeg?auto=compress&cs=tinysrgb&w=800',
    title: 'Detective Suite Enterprise',
    meta: 'VERIFICATION',
    description: 'Comprehensive fact-checking platform with API integrations to trusted news sources and expert networks.',
    price: '$599/month'
  },
  {
    id: 3,
    image: 'https://images.pexels.com/photos/8728380/pexels-photo-8728380.jpeg?auto=compress&cs=tinysrgb&w=800',
    title: 'Crisis Response Command',
    meta: 'EMERGENCY',
    description: 'Emergency response system with geo-targeted alerts, severity scoring, and real-time communication tools.',
    price: '$899/month'
  },
  {
    id: 4,
    image: 'https://images.pexels.com/photos/7688334/pexels-photo-7688334.jpeg?auto=compress&cs=tinysrgb&w=800',
    title: 'Blockchain Authenticator',
    meta: 'SECURITY',
    description: 'Immutable content verification system with blockchain provenance tracking and authenticity certificates.',
    price: '$399/month'
  },
  {
    id: 5,
    image: 'https://images.pexels.com/photos/8728381/pexels-photo-8728381.jpeg?auto=compress&cs=tinysrgb&w=800',
    title: 'AR Truth Overlay',
    meta: 'INNOVATION',
    description: 'Augmented reality mobile application that overlays credibility scores on social media content.',
    price: '$199/month'
  },
  {
    id: 6,
    image: 'https://images.pexels.com/photos/8728383/pexels-photo-8728383.jpeg?auto=compress&cs=tinysrgb&w=800',
    title: 'Trust Analytics Dashboard',
    meta: 'ANALYTICS',
    description: 'Comprehensive analytics platform for tracking information credibility across topics and sources.',
    price: '$499/month'
  }
];

export function ProductListPage() {
  const { isReducedMotion } = useTheme();
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState('grid');
  const [isLoading, setIsLoading] = useState(false);
  const [filteredProducts, setFilteredProducts] = useState(products);

  const handleSearch = (e) => {
    const term = e.target.value.toLowerCase();
    setSearchTerm(term);
    
    const filtered = products.filter(product => 
      product.title.toLowerCase().includes(term) ||
      product.meta.toLowerCase().includes(term) ||
      product.description.toLowerCase().includes(term)
    );
    setFilteredProducts(filtered);
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: isReducedMotion ? 0 : 0.08,
        delayChildren: 0.2
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

  const EmptyState = () => (
    <motion.div
      className="text-center py-16"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <div className="max-w-md mx-auto">
        <div className="w-24 h-24 mx-auto mb-6 bg-neutral-200 dark:bg-neutral-700 rounded-2xl flex items-center justify-center">
          <Search className="w-12 h-12 text-neutral-400" />
        </div>
        <h3 className="text-xl font-bold text-neutral-900 dark:text-neutral-100 mb-2">
          Nothing here yet — try adding a new item.
        </h3>
        <p className="text-neutral-600 dark:text-neutral-400 mb-6">
          No products match your search criteria. Try adjusting your search terms or browse all products.
        </p>
        <Button onClick={() => setSearchTerm('')}>
          Clear Search
        </Button>
      </div>
    </motion.div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-neutral-50 via-primary-50/20 to-secondary-50/20 dark:from-neutral-900 dark:via-neutral-800 dark:to-neutral-900">
      <div className="container mx-auto px-6 py-8">
        {/* Header */}
        <motion.div
          className="mb-8"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{
            type: "spring",
            stiffness: 140,
            damping: 20
          }}
        >
          <h1 className="text-4xl font-bold text-neutral-900 dark:text-neutral-100 mb-2">
            TruthShield Products
          </h1>
          <p className="text-neutral-600 dark:text-neutral-400">
            Discover our comprehensive suite of AI-powered misinformation detection tools
          </p>
        </motion.div>

        {/* Controls */}
        <motion.div
          className="flex flex-col md:flex-row items-center justify-between gap-6 mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <div className="flex-1 max-w-md">
            <FormField
              label="Search products..."
              value={searchTerm}
              onChange={handleSearch}
              className="w-full"
            />
          </div>

          <div className="flex items-center space-x-4">
            <Button variant="outline" size="sm">
              <Filter size={16} className="mr-2" />
              Filter
            </Button>

            <div className="flex items-center bg-white dark:bg-neutral-800 rounded-lg p-1 border border-neutral-200 dark:border-neutral-700">
              <Button
                variant={viewMode === 'grid' ? 'primary' : 'ghost'}
                size="sm"
                onClick={() => setViewMode('grid')}
                className="p-2"
              >
                <Grid size={16} />
              </Button>
              <Button
                variant={viewMode === 'list' ? 'primary' : 'ghost'}
                size="sm"
                onClick={() => setViewMode('list')}
                className="p-2"
              >
                <List size={16} />
              </Button>
            </div>

            <Button>
              <Plus size={16} className="mr-2" />
              Add Product
            </Button>
          </div>
        </motion.div>

        {/* Products Grid/List */}
        <AnimatePresence mode="wait">
          {isLoading ? (
            <motion.div
              className={cn(
                'grid gap-6',
                viewMode === 'grid' 
                  ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
                  : 'grid-cols-1'
              )}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              {Array.from({ length: 6 }).map((_, index) => (
                <Skeleton key={index} height="300px" className="rounded-2xl" />
              ))}
            </motion.div>
          ) : filteredProducts.length === 0 ? (
            <EmptyState />
          ) : (
            <motion.div
              className={cn(
                'grid gap-6',
                viewMode === 'grid' 
                  ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
                  : 'grid-cols-1'
              )}
              variants={containerVariants}
              initial="hidden"
              animate="visible"
              key={viewMode}
            >
              {filteredProducts.map((product, index) => (
                <motion.div
                  key={product.id}
                  variants={itemVariants}
                  layout
                >
                  <Card
                    image={product.image}
                    title={product.title}
                    meta={product.meta}
                    description={product.description}
                    className={viewMode === 'list' ? 'flex-row overflow-hidden' : ''}
                  >
                    <div className="flex items-center justify-between mt-4 pt-4 border-t border-neutral-200/50 dark:border-neutral-700/50">
                      <span className="text-2xl font-bold text-primary-600 dark:text-primary-400">
                        {product.price}
                      </span>
                      <Button size="sm">
                        Get Started
                      </Button>
                    </div>
                  </Card>
                </motion.div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}