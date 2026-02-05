import React, { useState, useEffect, useRef } from 'react';
import { useStoryStore } from '../store';
import { Volume2, VolumeX, Loader2, Calendar, FileText } from 'lucide-react';

export const SummaryCard = () => {
    const { token, user } = useStoryStore();
    const [summary, setSummary] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [audioUrl, setAudioUrl] = useState(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [generatingVoice, setGeneratingVoice] = useState(false);
    const audioRef = useRef(null);

    // Fetch latest summary on mount (if logged in)
    useEffect(() => {
        if (!token || !user) {
            setSummary(null);
            return;
        }

        const fetchSummary = async () => {
            setLoading(true);
            setError(null);

            try {
                const response = await fetch('http://localhost:8000/api/v1/manuscript/summaries/latest', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (response.status === 404) {
                    setSummary(null);
                    return;
                }

                if (!response.ok) {
                    throw new Error('Failed to fetch summary');
                }

                const data = await response.json();
                setSummary(data);
            } catch (err) {
                console.error('Error fetching summary:', err);
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchSummary();
    }, [token, user]);

    const handleGenerateVoice = async () => {
        if (!summary || !token) return;

        setGeneratingVoice(true);

        try {
            const response = await fetch(
                `http://localhost:8000/api/v1/manuscript/summaries/${summary.id}/generate-voice`,
                {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                }
            );

            if (!response.ok) {
                throw new Error('Failed to generate voice');
            }

            const data = await response.json();
            setAudioUrl(`http://localhost:8000${data.audio_url}`);
        } catch (err) {
            console.error('Voice generation error:', err);
            setError('Failed to generate voice');
        } finally {
            setGeneratingVoice(false);
        }
    };

    const handlePlayPause = () => {
        if (!audioRef.current) return;

        if (isPlaying) {
            audioRef.current.pause();
            setIsPlaying(false);
        } else {
            audioRef.current.play();
            setIsPlaying(true);
        }
    };

    // Don't render if not logged in
    if (!user || !token) {
        return null;
    }

    // Loading state
    if (loading) {
        return (
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <div className="flex items-center justify-center py-8">
                    <Loader2 className="animate-spin text-blue-600" size={24} />
                    <span className="ml-2 text-gray-600">Loading summary...</span>
                </div>
            </div>
        );
    }

    // Error state
    if (error && !summary) {
        return (
            <div className="bg-red-50 p-6 rounded-lg border border-red-200">
                <p className="text-red-600 text-sm">Error: {error}</p>
            </div>
        );
    }

    // Empty state
    if (!summary) {
        return (
            <div className="bg-gradient-to-br from-gray-50 to-gray-100 p-8 rounded-lg border border-gray-200">
                <div className="text-center">
                    <FileText className="mx-auto text-gray-400 mb-3" size={48} />
                    <p className="text-gray-600 font-medium mb-1">No summaries yet</p>
                    <p className="text-gray-500 text-sm">
                        Click "Save & Analyze" to generate your first AI-powered summary
                    </p>
                </div>
            </div>
        );
    }

    // Summary display
    return (
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-800 mb-2">{summary.title}</h3>
                    <div className="flex items-center gap-4 text-xs text-gray-500">
                        <div className="flex items-center gap-1">
                            <Calendar size={14} />
                            <span>{new Date(summary.created_at).toLocaleDateString()}</span>
                        </div>
                        <div className="flex items-center gap-1">
                            <FileText size={14} />
                            <span>{summary.word_count} words</span>
                        </div>
                        {summary.chapter && (
                            <span>Ch. {summary.chapter}, Para. {summary.paragraph}</span>
                        )}
                    </div>
                </div>

                <button
                    onClick={audioUrl ? handlePlayPause : handleGenerateVoice}
                    disabled={generatingVoice}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm font-medium"
                >
                    {generatingVoice ? (
                        <>
                            <Loader2 className="animate-spin" size={16} />
                            Generating...
                        </>
                    ) : audioUrl ? (
                        <>
                            {isPlaying ? <VolumeX size={16} /> : <Volume2 size={16} />}
                            {isPlaying ? 'Pause' : 'Play'}
                        </>
                    ) : (
                        <>
                            <Volume2 size={16} />
                            Generate Voice
                        </>
                    )}
                </button>
            </div>

            <div className="prose max-w-none">
                <p className="text-gray-700 leading-relaxed text-sm">{summary.summary}</p>
            </div>

            {error && (
                <div className="mt-3 p-2 bg-red-50 border border-red-200 rounded text-red-600 text-xs">
                    {error}
                </div>
            )}

            {audioUrl && (
                <audio
                    ref={audioRef}
                    src={audioUrl}
                    onEnded={() => setIsPlaying(false)}
                    onPause={() => setIsPlaying(false)}
                    onPlay={() => setIsPlaying(true)}
                />
            )}
        </div>
    );
};
