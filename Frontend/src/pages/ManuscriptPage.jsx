import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { BookOpen, Sparkles } from 'lucide-react';
import { ManuscriptEditor } from '../components/Manuscripteditor';
import { SummaryCard } from '../components/SummaryCard';
import { EntitySidebar } from '../components/Entitysidebar';

export default function ManuscriptPage() {
    const [manuscriptId] = useState('my_story_' + Date.now());

    const handleEntityClick = (entity) => {
        console.log('Entity clicked:', entity);
        // Future: Could show entity details in a modal or highlight in text
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-neutral-50 via-white to-neutral-100 dark:from-neutral-900 dark:via-neutral-800 dark:to-neutral-900">
            <div className="container mx-auto px-6 py-8">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-8"
                >
                    <div className="flex items-center space-x-3 mb-2">
                        <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg">
                            <BookOpen className="w-6 h-6 text-white" />
                        </div>
                        <h1 className="text-4xl font-bold text-neutral-900 dark:text-neutral-100">
                            Story Manuscript
                        </h1>
                    </div>
                    <p className="text-neutral-600 dark:text-neutral-400 flex items-center gap-2">
                        <Sparkles className="w-4 h-4" />
                        Write your story and watch AI extract characters, locations, and events in real-time
                    </p>
                </motion.div>

                {/* Main Content: Two-Column Layout */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-200px)]"
                >
                    {/* Editor - Takes 2/3 of space on large screens */}
                    <div className="lg:col-span-2 bg-white dark:bg-neutral-800 rounded-2xl shadow-lg overflow-hidden">
                        <ManuscriptEditor manuscriptId={manuscriptId} />
                    </div>

                    {/* Entity Sidebar - Takes 1/3 of space on large screens */}
                    <div className="lg:col-span-1 bg-white dark:bg-neutral-800 rounded-2xl shadow-lg overflow-hidden">
                        <EntitySidebar onEntityClick={handleEntityClick} />
                    </div>
                </motion.div>

                {/* Summary Card Section */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="mt-6"
                >
                    <SummaryCard />
                </motion.div>

                {/* Info Card */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.3 }}
                    className="mt-6 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-4"
                >
                    <div className="flex items-start gap-3">
                        <Sparkles className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
                        <div className="text-sm text-blue-800 dark:text-blue-200">
                            <p className="font-semibold mb-1">AI-Powered Entity Extraction</p>
                            <p className="text-blue-700 dark:text-blue-300">
                                As you write, our AI automatically identifies characters, locations, and events.
                                Entities are saved to the Knowledge Graph and appear in the sidebar.
                                Auto-save triggers 2 seconds after you stop typing.
                            </p>
                        </div>
                    </div>
                </motion.div>
            </div>
        </div>
    );
}
