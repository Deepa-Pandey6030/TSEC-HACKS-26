import React, { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { FileText, CheckCircle, AlertTriangle, Shield } from 'lucide-react';

const PdfAnalysisFeed = () => {
    const cardRef = useRef(null);

    // Sample feed data
    const feedItems = [
        {
            id: 1,
            title: "COVID-19 'Miracle Cure'",
            status: "Potential Misinformation Detected",
            confidence: 93,
            timestamp: "Analyzed 2 hours ago",
            type: "warning"
        },
        {
            id: 2,
            title: "Economic Forecast Report",
            status: "Verified Information",
            confidence: 99,
            timestamp: "Analyzed 4 hours ago",
            type: "verified"
        },
        {
            id: 3,
            title: "Leaked Political Document",
            status: "Sensitive Content Identified",
            confidence: 91,
            timestamp: "Analyzed 6 hours ago",
            type: "sensitive"
        }
    ];

    // 3D tilt effect on mouse move
    useEffect(() => {
        const card = cardRef.current;
        if (!card) return;

        const handleMouseMove = (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const centerX = rect.width / 2;
            const centerY = rect.height / 2;

            const rotateX = (y - centerY) / 20;
            const rotateY = (centerX - x) / 20;

            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(0px)`;
        };

        const handleMouseLeave = () => {
            card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0px)';
        };

        card.addEventListener('mousemove', handleMouseMove);
        card.addEventListener('mouseleave', handleMouseLeave);

        return () => {
            card.removeEventListener('mousemove', handleMouseMove);
            card.removeEventListener('mouseleave', handleMouseLeave);
        };
    }, []);

    const getStatusIcon = (type) => {
        switch (type) {
            case 'verified':
                return <CheckCircle className="text-green-400" size={16} />;
            case 'warning':
                return <AlertTriangle className="text-amber-400" size={16} />;
            case 'sensitive':
                return <Shield className="text-blue-400" size={16} />;
            default:
                return <FileText className="text-gray-400" size={16} />;
        }
    };

    const getConfidenceColor = (confidence) => {
        if (confidence >= 95) return 'from-green-500 to-emerald-500';
        if (confidence >= 85) return 'from-blue-500 to-cyan-500';
        return 'from-amber-500 to-orange-500';
    };

    return (
        <motion.div
            ref={cardRef}
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="relative w-full h-full"
            style={{ transformStyle: 'preserve-3d', transition: 'transform 0.1s ease-out' }}
        >
            {/* Animated background glow */}
            <div className="absolute inset-0 -z-10">
                <div className="absolute top-0 left-1/4 w-64 h-64 bg-blue-500/20 rounded-full blur-3xl animate-pulse"
                    style={{ animationDuration: '4s' }} />
                <div className="absolute bottom-0 right-1/4 w-64 h-64 bg-purple-500/20 rounded-full blur-3xl animate-pulse"
                    style={{ animationDuration: '5s', animationDelay: '1s' }} />
                <div className="absolute top-1/2 left-1/2 w-48 h-48 bg-cyan-500/10 rounded-full blur-3xl animate-pulse"
                    style={{ animationDuration: '6s', animationDelay: '2s' }} />
            </div>

            {/* Glassmorphism card */}
            <div className="relative h-full rounded-2xl overflow-hidden group">
                {/* Glass background */}
                <div className="absolute inset-0 bg-gradient-to-br from-white/10 via-white/5 to-transparent backdrop-blur-2xl" />

                {/* Gradient border */}
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-blue-500/30 via-purple-500/20 to-cyan-500/30 p-[1px]">
                    <div className="h-full w-full rounded-2xl bg-gradient-to-br from-gray-900/90 via-gray-900/80 to-gray-900/90 backdrop-blur-xl" />
                </div>

                {/* Hover glow effect */}
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-blue-500/0 via-purple-500/0 to-cyan-500/0 group-hover:from-blue-500/10 group-hover:via-purple-500/10 group-hover:to-cyan-500/10 transition-all duration-500" />

                {/* Content */}
                <div className="relative h-full p-6 flex flex-col">
                    {/* Header */}
                    <motion.div
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3, duration: 0.6 }}
                        className="flex items-center gap-3 mb-6"
                    >
                        <div className="p-2 rounded-lg bg-gradient-to-br from-blue-500/20 to-purple-500/20 backdrop-blur-sm">
                            <FileText className="text-blue-400" size={20} />
                        </div>
                        <h3 className="text-xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">
                            PDF Analysis Feed
                        </h3>
                    </motion.div>

                    {/* Feed items */}
                    <div className="flex-1 space-y-4 overflow-y-auto scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
                        {feedItems.map((item, index) => (
                            <motion.div
                                key={item.id}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.5 + index * 0.15, duration: 0.5 }}
                                whileHover={{ scale: 1.02, x: 4 }}
                                className="relative group/item"
                            >
                                {/* Item card */}
                                <div className="relative p-4 rounded-xl bg-gradient-to-br from-white/5 to-white/[0.02] border border-white/10 hover:border-white/20 transition-all duration-300">
                                    {/* Hover glow */}
                                    <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-blue-500/0 to-purple-500/0 group-hover/item:from-blue-500/5 group-hover/item:to-purple-500/5 transition-all duration-300" />

                                    <div className="relative space-y-3">
                                        {/* Title row */}
                                        <div className="flex items-start gap-3">
                                            <div className="mt-1 p-1.5 rounded-lg bg-white/5">
                                                <FileText className="text-gray-400" size={14} />
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <h4 className="text-sm font-semibold text-white/90 truncate">
                                                    {item.title}
                                                </h4>
                                            </div>
                                        </div>

                                        {/* Status row */}
                                        <div className="flex items-center gap-2 text-xs">
                                            {getStatusIcon(item.type)}
                                            <span className="text-gray-400">{item.status}</span>
                                        </div>

                                        {/* Confidence badge */}
                                        <div className="flex items-center justify-between">
                                            <motion.div
                                                initial={{ scale: 0.8 }}
                                                animate={{ scale: 1 }}
                                                transition={{ delay: 0.7 + index * 0.15, duration: 0.3 }}
                                                className="relative"
                                            >
                                                <div className={`px-3 py-1 rounded-full bg-gradient-to-r ${getConfidenceColor(item.confidence)} bg-opacity-20 backdrop-blur-sm`}>
                                                    <span className="text-xs font-bold text-white">
                                                        {item.confidence}% Confidence
                                                    </span>
                                                </div>
                                                {/* Pulse animation */}
                                                <motion.div
                                                    animate={{ scale: [1, 1.2, 1], opacity: [0.5, 0, 0.5] }}
                                                    transition={{ duration: 2, repeat: Infinity, delay: index * 0.5 }}
                                                    className={`absolute inset-0 rounded-full bg-gradient-to-r ${getConfidenceColor(item.confidence)}`}
                                                />
                                            </motion.div>

                                            <span className="text-xs text-gray-500">
                                                {item.timestamp}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </motion.div>
                        ))}
                    </div>

                    {/* Footer indicator */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 1.2, duration: 0.5 }}
                        className="mt-4 pt-4 border-t border-white/5 flex items-center justify-center gap-2"
                    >
                        <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                        <span className="text-xs text-gray-500">Live Analysis Active</span>
                    </motion.div>
                </div>

                {/* Light trails effect */}
                <div className="absolute inset-0 pointer-events-none overflow-hidden rounded-2xl">
                    <motion.div
                        animate={{
                            x: ['-100%', '200%'],
                            y: ['-100%', '100%']
                        }}
                        transition={{
                            duration: 8,
                            repeat: Infinity,
                            ease: "linear"
                        }}
                        className="absolute w-px h-32 bg-gradient-to-b from-transparent via-blue-400/50 to-transparent"
                        style={{ top: '20%', left: '10%' }}
                    />
                    <motion.div
                        animate={{
                            x: ['200%', '-100%'],
                            y: ['100%', '-100%']
                        }}
                        transition={{
                            duration: 10,
                            repeat: Infinity,
                            ease: "linear",
                            delay: 2
                        }}
                        className="absolute w-px h-32 bg-gradient-to-b from-transparent via-purple-400/50 to-transparent"
                        style={{ top: '60%', left: '80%' }}
                    />
                </div>
            </div>

            {/* Floating animation */}
            <motion.div
                animate={{
                    y: [0, -6, 0]
                }}
                transition={{
                    duration: 4,
                    repeat: Infinity,
                    ease: "easeInOut"
                }}
                className="absolute inset-0 -z-20"
            />
        </motion.div>
    );
};

export default PdfAnalysisFeed;
