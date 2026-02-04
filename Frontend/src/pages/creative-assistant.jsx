import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Sparkles, Upload, FileText, ChevronLeft, ChevronRight,
    Wand2, MessageSquare, TrendingUp, Target, Lightbulb,
    CheckCircle2, AlertCircle, Activity, Zap, Eye
} from 'lucide-react';
import { useTheme } from '../lib/theme-provider';
import { useGrammarCheck } from '../hooks/useGrammarCheck';
import { useAutocomplete } from '../hooks/useAutocomplete';
import GrammarOverlay from '../components/Editor/GrammarOverlay';
import GhostOverlay from '../components/Editor/GhostOverlay';
import LineGutter from '../components/Editor/LineGutter';

const API_BASE_URL = 'http://localhost:8000';

// Writing Mode Options
const WRITING_MODES = [
    { id: 'veteran', icon: '🎖️', label: 'Veteran Editor', description: '30+ years editorial experience' },
    { id: 'creative', icon: '✨', label: 'Creative Writer', description: 'Imaginative storytelling' },
    { id: 'consultant', icon: '🎭', label: 'Story Consultant', description: 'Narrative structure expert' },
    { id: 'academic', icon: '📚', label: 'Academic Reviewer', description: 'Scholarly precision' }
];

export function CreativeAssistantPage({ isAutocompleteEnabled = true }) {
    const { isReducedMotion } = useTheme();
    const [contextPanelOpen, setContextPanelOpen] = useState(true);
    const [insightPanelOpen, setInsightPanelOpen] = useState(true);
    const [selectedMode, setSelectedMode] = useState('veteran');
    const [prompt, setPrompt] = useState('');
    const [content, setContent] = useState('');
    const [analyzing, setAnalyzing] = useState(false);
    const [insights, setInsights] = useState(null);
    const [selectedText, setSelectedText] = useState('');
    const [selectionPosition, setSelectionPosition] = useState(null);
    const [rewriting, setRewriting] = useState(false);
    const [improving, setImproving] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [uploadedFile, setUploadedFile] = useState(null);
    const [rewriteStyle, setRewriteStyle] = useState('professional');
    const [flowTone, setFlowTone] = useState('default');
    const [originalContent, setOriginalContent] = useState('');
    const [showKeepUndoControls, setShowKeepUndoControls] = useState(false);
    const [predictiveRisks, setPredictiveRisks] = useState(null);
    const editorRef = useRef(null);
    const fileInputRef = useRef(null);

    // Grammar Checking Integration
    const { matches, isChecking: isGrammarChecking, setMatches } = useGrammarCheck(content);

    // Autocomplete Integration
    const { suggestion, acceptSuggestion, clearSuggestion } = useAutocomplete(content, isAutocompleteEnabled);

    const handleApplyGrammarFix = (match, replacement) => {
        const prefix = content.slice(0, match.offset);
        const suffix = content.slice(match.offset + match.length);
        const newContent = prefix + replacement + suffix;
        setContent(newContent);

        // Remove the fixed match locally to update UI instantly
        setMatches(prev => prev.filter(m => m.offset !== match.offset));
    };

    // Handle text selection for floating toolbar
    const handleTextSelection = () => {
        const selection = window.getSelection();
        const text = selection.toString().trim();

        if (text && editorRef.current?.contains(selection.anchorNode)) {
            setSelectedText(text);
            const range = selection.getRangeAt(0);
            const rect = range.getBoundingClientRect();
            setSelectionPosition({
                top: rect.top - 60,
                left: rect.left + rect.width / 2
            });
        } else {
            setSelectedText('');
            setSelectionPosition(null);
        }
    };

    // Handle Tab to accept suggestion
    const handleKeyDown = (e) => {
        if (e.key === 'Tab' && suggestion) {
            e.preventDefault();
            const addedText = acceptSuggestion();
            if (addedText) {
                setContent(prev => prev + addedText);
            }
        }
    };

    useEffect(() => {
        document.addEventListener('selectionchange', handleTextSelection);
        return () => document.removeEventListener('selectionchange', handleTextSelection);
    }, []);

    // Handle analyze with predictive risk analysis
    const handleAnalyze = async () => {
        if (!content.trim()) return;

        setAnalyzing(true);
        try {
            const response = await fetch(`${API_BASE_URL}/api/v1/creative-assistant/quick-analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    story_title: 'Untitled Story',
                    genre: 'General',
                    completion_percentage: 50,
                    recent_scene_summary: content
                })
            });

            if (response.ok) {
                const data = await response.json();
                setInsights(data);

                // Store predictive risk analysis
                if (data.predictive_risks) {
                    setPredictiveRisks(data.predictive_risks);
                    console.log('📊 Predictive Risk Analysis:', data.predictive_risks);
                }
            }
        } catch (error) {
            console.error('Analysis error:', error);
        } finally {
            setAnalyzing(false);
        }
    };

    // Rewrite content
    const handleRewrite = async () => {
        if (!content.trim()) return;

        setRewriting(true);
        try {
            const response = await fetch(`${API_BASE_URL}/api/v1/creative-assistant/rewrite`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    content: content,
                    style: rewriteStyle
                })
            });

            if (response.ok) {
                const data = await response.json();
                setContent(data.rewritten);
            }
        } catch (error) {
            console.error('Rewrite error:', error);
        } finally {
            setRewriting(false);
        }
    };

    // Improve flow with production-grade Flow Engine
    const handleImproveFlow = async () => {
        if (!content.trim()) return;

        setImproving(true);
        try {
            const response = await fetch(`${API_BASE_URL}/api/v1/creative-assistant/improve-flow`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    content: content,
                    tone: flowTone,
                    preserve_formatting: true,
                    focus: 'pacing'  // Legacy parameter
                })
            });

            if (response.ok) {
                const data = await response.json();

                // Store original content for undo
                setOriginalContent(content);

                // Update with improved content
                setContent(data.improved);

                // Show Keep/Undo controls
                setShowKeepUndoControls(true);

                // Log metadata for debugging
                if (data.metadata) {
                    console.log('Flow Engine:', {
                        chunks: data.metadata.chunks_processed,
                        tokens: data.metadata.tokens_used,
                        provider: data.metadata.provider
                    });
                }
            }
        } catch (error) {
            console.error('Improve flow error:', error);
        } finally {
            setImproving(false);
        }
    };

    // Keep the improved changes
    const handleKeepChanges = () => {
        setShowKeepUndoControls(false);
        setOriginalContent('');
        // Could add backend API call here to save the accepted changes
    };

    // Undo and revert to original
    const handleUndoChanges = () => {
        setContent(originalContent);
        setShowKeepUndoControls(false);
        setOriginalContent('');
    };

    // Handle file upload
    const handleFileUpload = async (file) => {
        if (!file) return;

        setUploading(true);
        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch(`${API_BASE_URL}/api/v1/creative-assistant/upload-file`, {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                setContent(data.text);
                setUploadedFile(data.filename);
            }
        } catch (error) {
            console.error('Upload error:', error);
        } finally {
            setUploading(false);
        }
    };

    // Handle file drop
    const handleFileDrop = (e) => {
        e.preventDefault();
        const file = e.dataTransfer.files[0];
        if (file) handleFileUpload(file);
    };

    // Handle file select
    const handleFileSelect = (e) => {
        const file = e.target.files[0];
        if (file) handleFileUpload(file);
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50 dark:from-neutral-900 dark:via-neutral-800 dark:to-neutral-900">
            {/* Hero Workspace Header */}
            <motion.div
                className="relative bg-gradient-to-r from-blue-100 via-white to-cyan-100 dark:from-neutral-800 dark:via-neutral-900 dark:to-neutral-800 border-b border-neutral-200/50 dark:border-neutral-700/50 backdrop-blur-xl"
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
            >
                <div className="container mx-auto px-6 py-8">
                    <div className="flex items-center justify-between">
                        {/* Left: Title & Subtitle */}
                        <div>
                            <h1 className="text-3xl font-bold text-neutral-900 dark:text-neutral-100 mb-2">
                                AI Creative Assistant
                            </h1>
                            <p className="text-neutral-600 dark:text-neutral-400">
                                Senior Writer AI with 30+ years of editorial experience
                            </p>
                        </div>

                        {/* Right: Status */}
                        <motion.div
                            className="flex items-center gap-2 px-4 py-2 bg-green-100 dark:bg-green-900/20 rounded-full border border-green-200 dark:border-green-800"
                            animate={{ scale: analyzing ? [1, 1.05, 1] : 1 }}
                            transition={{ repeat: analyzing ? Infinity : 0, duration: 2 }}
                        >
                            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                            <span className="text-sm font-medium text-green-700 dark:text-green-400">
                                {analyzing ? 'AI Predicting Future Impact...' : improving ? `Improving Flow (${flowTone})...` : 'Ready to Analyze'}
                            </span>
                        </motion.div>
                    </div>
                </div>

                {/* Subtle glow effect */}
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 to-cyan-500/5 pointer-events-none" />
            </motion.div>

            {/* Main Workspace Layout */}
            <div className="container mx-auto px-6 py-6">
                <div className="flex gap-6 relative">
                    {/* Context Panel (LEFT) */}
                    <AnimatePresence>
                        {contextPanelOpen && (
                            <motion.div
                                className="w-80 flex-shrink-0"
                                initial={{ x: -300, opacity: 0 }}
                                animate={{ x: 0, opacity: 1 }}
                                exit={{ x: -300, opacity: 0 }}
                                transition={{ type: "spring", stiffness: 140, damping: 20 }}
                            >
                                <div className="sticky top-6 space-y-4">
                                    {/* Prompt Input */}
                                    <div className="bg-white/80 dark:bg-neutral-900/80 backdrop-blur-xl rounded-2xl p-6 border border-neutral-200/50 dark:border-neutral-700/50 shadow-lg">
                                        <div className="flex items-center gap-2 mb-4">
                                            <MessageSquare className="text-primary-600 dark:text-primary-400" size={20} />
                                            <h3 className="font-semibold text-neutral-900 dark:text-neutral-100">
                                                Writing Intent
                                            </h3>
                                        </div>
                                        <input
                                            type="text"
                                            value={prompt}
                                            onChange={(e) => setPrompt(e.target.value)}
                                            placeholder="What are you working on?"
                                            className="w-full px-4 py-3 bg-neutral-50 dark:bg-neutral-800 rounded-lg border border-neutral-200 dark:border-neutral-700 text-neutral-900 dark:text-neutral-100 placeholder-neutral-400 focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                                        />
                                    </div>

                                    {/* Writing Mode Selector */}
                                    <div className="bg-white/80 dark:bg-neutral-900/80 backdrop-blur-xl rounded-2xl p-6 border border-neutral-200/50 dark:border-neutral-700/50 shadow-lg">
                                        <div className="flex items-center gap-2 mb-4">
                                            <Wand2 className="text-primary-600 dark:text-primary-400" size={20} />
                                            <h3 className="font-semibold text-neutral-900 dark:text-neutral-100">
                                                Writing Mode
                                            </h3>
                                        </div>
                                        <div className="space-y-2">
                                            {WRITING_MODES.map((mode) => (
                                                <motion.button
                                                    key={mode.id}
                                                    onClick={() => setSelectedMode(mode.id)}
                                                    className={`w-full text-left px-4 py-3 rounded-lg transition-all ${selectedMode === mode.id
                                                        ? 'bg-primary-100 dark:bg-primary-900/20 border-2 border-primary-500'
                                                        : 'bg-neutral-50 dark:bg-neutral-800 border-2 border-transparent hover:border-neutral-300 dark:hover:border-neutral-600'
                                                        }`}
                                                    whileHover={{ scale: isReducedMotion ? 1 : 1.02 }}
                                                    whileTap={{ scale: isReducedMotion ? 1 : 0.98 }}
                                                >
                                                    <div className="flex items-center gap-3">
                                                        <span className="text-2xl">{mode.icon}</span>
                                                        <div className="flex-1">
                                                            <div className="font-medium text-neutral-900 dark:text-neutral-100 text-sm">
                                                                {mode.label}
                                                            </div>
                                                            <div className="text-xs text-neutral-500 dark:text-neutral-400">
                                                                {mode.description}
                                                            </div>
                                                        </div>
                                                    </div>
                                                </motion.button>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Flow Tone Selector */}
                                    <div className="bg-white/80 dark:bg-neutral-900/80 backdrop-blur-xl rounded-2xl p-6 border border-neutral-200/50 dark:border-neutral-700/50 shadow-lg">
                                        <div className="flex items-center gap-2 mb-4">
                                            <TrendingUp className="text-primary-600 dark:text-primary-400" size={20} />
                                            <h3 className="font-semibold text-neutral-900 dark:text-neutral-100">
                                                Flow Tone
                                            </h3>
                                        </div>
                                        <select
                                            value={flowTone}
                                            onChange={(e) => setFlowTone(e.target.value)}
                                            className="w-full px-4 py-3 bg-neutral-50 dark:bg-neutral-800 rounded-lg border border-neutral-200 dark:border-neutral-700 text-neutral-900 dark:text-neutral-100 focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                                        >
                                            <option value="default">Default - Professional & Clear</option>
                                            <option value="academic">Academic - Scholarly Precision</option>
                                            <option value="business">Business - Executive Friendly</option>
                                            <option value="simple">Simple - Easy to Understand</option>
                                            <option value="creative">Creative - Light Flair</option>
                                        </select>
                                    </div>

                                    {/* File Upload */}
                                    <div className="bg-white/80 dark:bg-neutral-900/80 backdrop-blur-xl rounded-2xl p-6 border border-neutral-200/50 dark:border-neutral-700/50 shadow-lg">
                                        <div className="flex items-center gap-2 mb-4">
                                            <Upload className="text-primary-600 dark:text-primary-400" size={20} />
                                            <h3 className="font-semibold text-neutral-900 dark:text-neutral-100">
                                                Attach Files
                                            </h3>
                                        </div>
                                        <div
                                            onClick={() => fileInputRef.current?.click()}
                                            onDrop={handleFileDrop}
                                            onDragOver={(e) => e.preventDefault()}
                                            className="border-2 border-dashed border-neutral-300 dark:border-neutral-600 rounded-lg p-6 text-center hover:border-primary-500 transition-colors cursor-pointer"
                                        >
                                            {uploading ? (
                                                <div className="flex flex-col items-center">
                                                    <motion.div
                                                        animate={{ rotate: 360 }}
                                                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                                                    >
                                                        <Upload className="mx-auto mb-2 text-primary-500" size={32} />
                                                    </motion.div>
                                                    <p className="text-sm text-neutral-600 dark:text-neutral-400">
                                                        Uploading...
                                                    </p>
                                                </div>
                                            ) : uploadedFile ? (
                                                <div className="flex flex-col items-center">
                                                    <CheckCircle2 className="mx-auto mb-2 text-green-500" size={32} />
                                                    <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-1">
                                                        {uploadedFile}
                                                    </p>
                                                    <p className="text-xs text-neutral-400">
                                                        Click to upload another
                                                    </p>
                                                </div>
                                            ) : (
                                                <div className="flex flex-col items-center">
                                                    <FileText className="mx-auto mb-2 text-neutral-400" size={32} />
                                                    <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-1">
                                                        Drop files here or click to browse
                                                    </p>
                                                    <p className="text-xs text-neutral-400">
                                                        PDF, DOCX, TXT supported
                                                    </p>
                                                </div>
                                            )}
                                        </div>
                                        <input
                                            ref={fileInputRef}
                                            type="file"
                                            accept=".pdf,.docx,.txt"
                                            onChange={handleFileSelect}
                                            className="hidden"
                                        />
                                    </div>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {/* Toggle Context Panel */}
                    <motion.button
                        onClick={() => setContextPanelOpen(!contextPanelOpen)}
                        className="absolute left-0 top-1/2 -translate-y-1/2 z-10 bg-white dark:bg-neutral-800 p-2 rounded-r-lg border border-l-0 border-neutral-200 dark:border-neutral-700 shadow-lg hover:bg-neutral-50 dark:hover:bg-neutral-700 transition-colors"
                        whileHover={{ x: contextPanelOpen ? 0 : 4 }}
                    >
                        {contextPanelOpen ? <ChevronLeft size={20} /> : <ChevronRight size={20} />}
                    </motion.button>

                    {/* Creative Canvas (CENTER) */}
                    <div className="flex-1 min-w-0">
                        <div className="bg-white/80 dark:bg-neutral-900/80 backdrop-blur-xl rounded-2xl border border-neutral-200/50 dark:border-neutral-700/50 shadow-xl min-h-[600px] relative overflow-hidden">
                            {/* Canvas Header */}
                            <div className="border-b border-neutral-200/50 dark:border-neutral-700/50 px-6 py-4">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-2">
                                        <Sparkles className="text-primary-600 dark:text-primary-400" size={20} />
                                        <span className="font-medium text-neutral-900 dark:text-neutral-100">
                                            Creative Canvas
                                        </span>
                                    </div>
                                    <div className="flex items-center gap-4">
                                        <div className="text-sm text-neutral-500 dark:text-neutral-400">
                                            {content.length} characters
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Editor */}
                            <div className="relative pl-12 flex">
                                <LineGutter content={content} />
                                <div className="relative flex-1 p-8">
                                    <GrammarOverlay
                                        text={content}
                                        matches={matches}
                                        onApplyFix={handleApplyGrammarFix}
                                    />
                                    <GhostOverlay text={content} suggestion={suggestion} />
                                    <textarea
                                        ref={editorRef}
                                        value={content}
                                        onChange={(e) => setContent(e.target.value)}
                                        onKeyDown={handleKeyDown}
                                        placeholder="Start writing… Nolan is reviewing your work."
                                        className="w-full min-h-[500px] bg-transparent border-none outline-none text-neutral-900 dark:text-neutral-100 text-lg leading-relaxed resize-none placeholder-neutral-400 focus:placeholder-neutral-300 relative z-10"
                                        style={{ fontFamily: 'Georgia, serif' }}
                                    />
                                </div>
                            </div>

                            {/* Keep/Undo Controls */}
                            <AnimatePresence>
                                {showKeepUndoControls && (
                                    <motion.div
                                        initial={{ opacity: 0, y: 20 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        exit={{ opacity: 0, y: 20 }}
                                        className="pb-8 flex items-center justify-center gap-4"
                                    >
                                        <motion.button
                                            onClick={handleKeepChanges}
                                            className="px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-medium rounded-lg shadow-lg flex items-center gap-2 transition-all"
                                            whileHover={{ scale: 1.05 }}
                                            whileTap={{ scale: 0.95 }}
                                        >
                                            <CheckCircle2 size={20} />
                                            Keep Changes
                                        </motion.button>

                                        <motion.button
                                            onClick={handleUndoChanges}
                                            className="px-6 py-3 bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-700 hover:to-rose-700 text-white font-medium rounded-lg shadow-lg flex items-center gap-2 transition-all"
                                            whileHover={{ scale: 1.05 }}
                                            whileTap={{ scale: 0.95 }}
                                        >
                                            <AlertCircle size={20} />
                                            Undo Changes
                                        </motion.button>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>

                        {/* Floating Selection Toolbar */}
                        <AnimatePresence>
                            {selectedText && selectionPosition && (
                                <motion.div
                                    initial={{ opacity: 0, y: 10, scale: 0.9 }}
                                    animate={{ opacity: 1, y: 0, scale: 1 }}
                                    exit={{ opacity: 0, y: 10, scale: 0.9 }}
                                    className="fixed z-50 bg-neutral-900 dark:bg-neutral-800 rounded-lg shadow-2xl border border-neutral-700 px-2 py-2 flex items-center gap-1"
                                    style={{
                                        top: selectionPosition.top,
                                        left: selectionPosition.left,
                                        transform: 'translateX(-50%)'
                                    }}
                                >
                                    <button className="px-3 py-2 hover:bg-neutral-800 dark:hover:bg-neutral-700 rounded text-white text-sm flex items-center gap-1 transition-colors">
                                        <Sparkles size={14} /> Improve
                                    </button>
                                    <button className="px-3 py-2 hover:bg-neutral-800 dark:hover:bg-neutral-700 rounded text-white text-sm flex items-center gap-1 transition-colors">
                                        <Wand2 size={14} /> Tone
                                    </button>
                                    <button className="px-3 py-2 hover:bg-neutral-800 dark:hover:bg-neutral-700 rounded text-white text-sm flex items-center gap-1 transition-colors">
                                        <Eye size={14} /> Explain
                                    </button>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>

                    {/* Insight Panel (RIGHT) */}
                    <AnimatePresence>
                        {insightPanelOpen && insights && (
                            <motion.div
                                className="w-80 flex-shrink-0"
                                initial={{ x: 300, opacity: 0 }}
                                animate={{ x: 0, opacity: 1 }}
                                exit={{ x: 300, opacity: 0 }}
                                transition={{ type: "spring", stiffness: 140, damping: 20 }}
                            >
                                <div className="sticky top-6 space-y-4">
                                    {/* Narrative Health */}
                                    <div className="bg-white/80 dark:bg-neutral-900/80 backdrop-blur-xl rounded-2xl p-6 border border-neutral-200/50 dark:border-neutral-700/50 shadow-lg">
                                        <div className="flex items-center gap-2 mb-4">
                                            <Activity className="text-green-600 dark:text-green-400" size={20} />
                                            <h3 className="font-semibold text-neutral-900 dark:text-neutral-100">
                                                Narrative Health
                                            </h3>
                                        </div>
                                        <div className="space-y-3">
                                            <div>
                                                <div className="flex justify-between mb-1">
                                                    <span className="text-sm text-neutral-600 dark:text-neutral-400">Overall</span>
                                                    <span className="text-sm font-medium text-neutral-900 dark:text-neutral-100 capitalize">
                                                        {insights.overall_story_health}
                                                    </span>
                                                </div>
                                                <div className="h-2 bg-neutral-200 dark:bg-neutral-700 rounded-full overflow-hidden">
                                                    <motion.div
                                                        className="h-full bg-gradient-to-r from-green-500 to-emerald-500"
                                                        initial={{ width: 0 }}
                                                        animate={{ width: `${insights.plan_confidence * 100}%` }}
                                                        transition={{ duration: 1, ease: "easeOut" }}
                                                    />
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Suggestions */}
                                    <div className="bg-white/80 dark:bg-neutral-900/80 backdrop-blur-xl rounded-2xl p-6 border border-neutral-200/50 dark:border-neutral-700/50 shadow-lg">
                                        <div className="flex items-center gap-2 mb-4">
                                            <Lightbulb className="text-yellow-600 dark:text-yellow-400" size={20} />
                                            <h3 className="font-semibold text-neutral-900 dark:text-neutral-100">
                                                Insights
                                            </h3>
                                        </div>
                                        <div className="space-y-3">
                                            {insights.interventions.slice(0, 3).map((item, idx) => (
                                                <motion.div
                                                    key={idx}
                                                    initial={{ opacity: 0, x: 20 }}
                                                    animate={{ opacity: 1, x: 0 }}
                                                    transition={{ delay: idx * 0.1 }}
                                                    className="p-3 bg-neutral-50 dark:bg-neutral-800/50 rounded-lg"
                                                >
                                                    <div className="flex items-start gap-2">
                                                        <Zap className="text-primary-600 dark:text-primary-400 flex-shrink-0 mt-0.5" size={16} />
                                                        <p className="text-sm text-neutral-700 dark:text-neutral-300">
                                                            {item.what}
                                                        </p>
                                                    </div>
                                                </motion.div>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {/* Toggle Insight Panel */}
                    {insights && (
                        <motion.button
                            onClick={() => setInsightPanelOpen(!insightPanelOpen)}
                            className="absolute right-0 top-1/2 -translate-y-1/2 z-10 bg-white dark:bg-neutral-800 p-2 rounded-l-lg border border-r-0 border-neutral-200 dark:border-neutral-700 shadow-lg hover:bg-neutral-50 dark:hover:bg-neutral-700 transition-colors"
                            whileHover={{ x: insightPanelOpen ? 0 : -4 }}
                        >
                            {insightPanelOpen ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
                        </motion.button>
                    )}
                </div>
            </div>

            {/* Floating Action Dock */}
            <motion.div
                className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50"
                initial={{ y: 100, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.5 }}
            >
                <div className="bg-neutral-900 dark:bg-neutral-800 rounded-full px-6 py-4 shadow-2xl border border-neutral-700 flex items-center gap-4">
                    <motion.button
                        onClick={handleAnalyze}
                        disabled={!content.trim() || analyzing}
                        className="px-6 py-2 bg-gradient-to-r from-primary-600 to-secondary-600 hover:from-primary-700 hover:to-secondary-700 text-white font-medium rounded-full disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-all"
                        whileHover={!analyzing ? { scale: 1.05 } : {}}
                        whileTap={!analyzing ? { scale: 0.95 } : {}}
                    >
                        {analyzing ? (
                            <>
                                <motion.div
                                    animate={{ rotate: 360 }}
                                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                                >
                                    <Sparkles size={16} />
                                </motion.div>
                                AI Predicting Future Impact...
                            </>
                        ) : (
                            <>
                                <Target size={16} />
                                Analyze
                            </>
                        )}
                    </motion.button>

                    <div className="w-px h-6 bg-neutral-700" />

                    <motion.button
                        onClick={handleRewrite}
                        disabled={!content.trim() || rewriting}
                        className="px-4 py-2 hover:bg-neutral-800 dark:hover:bg-neutral-700 rounded-full text-white text-sm flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        whileHover={!rewriting ? { scale: 1.05 } : {}}
                        whileTap={!rewriting ? { scale: 0.95 } : {}}
                    >
                        {rewriting ? (
                            <>
                                <motion.div
                                    animate={{ rotate: 360 }}
                                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                                >
                                    <Wand2 size={16} />
                                </motion.div>
                                Rewriting...
                            </>
                        ) : (
                            <>
                                <Wand2 size={16} /> Rewrite
                            </>
                        )}
                    </motion.button>
                    <motion.button
                        onClick={handleImproveFlow}
                        disabled={!content.trim() || improving}
                        className="px-4 py-2 hover:bg-neutral-800 dark:hover:bg-neutral-700 rounded-full text-white text-sm flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        whileHover={!improving ? { scale: 1.05 } : {}}
                        whileTap={!improving ? { scale: 0.95 } : {}}
                    >
                        {improving ? (
                            <>
                                <motion.div
                                    animate={{ rotate: 360 }}
                                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                                >
                                    <TrendingUp size={16} />
                                </motion.div>
                                Improving Flow ({flowTone})...
                            </>
                        ) : (
                            <>
                                <TrendingUp size={16} /> Improve Flow
                            </>
                        )}
                    </motion.button>
                </div>
            </motion.div>
        </div>
    );
}
